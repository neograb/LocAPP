"""
Calendar Service - iCal import/export for LocApp
Handles synchronization with Booking.com, Airbnb, and other iCal sources
"""

import requests
from datetime import datetime, timedelta
from icalendar import Calendar, Event
from io import BytesIO
import re


class CalendarService:
    """Service for managing iCal calendar import/export"""

    def __init__(self, db):
        self.db = db

    def fetch_ical(self, url, timeout=30):
        """Fetch iCal data from a URL"""
        try:
            response = requests.get(url, timeout=timeout, headers={
                'User-Agent': 'LocApp Calendar Sync/1.0',
                'Accept': 'text/calendar, application/calendar+xml, */*'
            })
            response.raise_for_status()
            return response.text
        except requests.exceptions.Timeout:
            raise CalendarError("Timeout: Le serveur ne répond pas")
        except requests.exceptions.RequestException as e:
            raise CalendarError(f"Erreur de connexion: {str(e)}")

    def parse_ical(self, ical_content):
        """Parse iCal content and extract events"""
        try:
            cal = Calendar.from_ical(ical_content)
            events = []

            for component in cal.walk():
                if component.name == "VEVENT":
                    event = self._parse_event(component)
                    if event:
                        events.append(event)

            return events
        except Exception as e:
            raise CalendarError(f"Erreur de parsing iCal: {str(e)}")

    def _parse_event(self, component):
        """Parse a single VEVENT component"""
        try:
            uid = str(component.get('uid', ''))
            summary = str(component.get('summary', 'Réservation'))
            description = str(component.get('description', ''))

            # Get start and end dates
            dtstart = component.get('dtstart')
            dtend = component.get('dtend')

            if not dtstart:
                return None

            start_date = dtstart.dt
            if hasattr(start_date, 'date'):
                start_date = start_date.date()

            if dtend:
                end_date = dtend.dt
                if hasattr(end_date, 'date'):
                    end_date = end_date.date()
            else:
                # If no end date, assume 1 day event
                end_date = start_date + timedelta(days=1)

            # Try to extract guest name and platform from summary/description
            guest_name = self._extract_guest_name(summary, description)
            platform = self._detect_platform(summary, description, uid)
            status = self._parse_status(component.get('status', 'CONFIRMED'))

            return {
                'uid': uid,
                'summary': summary,
                'start_date': start_date.isoformat() if hasattr(start_date, 'isoformat') else str(start_date),
                'end_date': end_date.isoformat() if hasattr(end_date, 'isoformat') else str(end_date),
                'guest_name': guest_name,
                'platform': platform,
                'status': status,
                'description': description
            }
        except Exception as e:
            print(f"Error parsing event: {e}")
            return None

    def _extract_guest_name(self, summary, description):
        """Try to extract guest name from summary or description"""
        # Common patterns for guest names
        patterns = [
            r'(?:Reserved|Réservé)\s*[-:]\s*(.+?)(?:\s*\(|$)',
            r'(?:Guest|Client|Voyageur)\s*[-:]\s*(.+?)(?:\s*\(|$)',
            r'^(.+?)\s*[-–]\s*(?:Airbnb|Booking|VRBO)',
            r'(?:Reservation|Réservation)\s+(?:de\s+)?(.+?)(?:\s*[-–]|$)',
        ]

        for text in [summary, description]:
            if not text:
                continue
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    if name and len(name) > 1 and len(name) < 50:
                        return name

        # If summary looks like a name (no special keywords), use it
        if summary and not any(kw in summary.lower() for kw in ['reserved', 'blocked', 'unavailable', 'not available', 'réservé', 'bloqué', 'indisponible']):
            # Check if it's a reasonable name
            if len(summary) < 50 and not summary.startswith(('http', 'www')):
                return summary

        return None

    def _detect_platform(self, summary, description, uid):
        """Detect which platform the reservation came from"""
        text = f"{summary} {description} {uid}".lower()

        if 'airbnb' in text:
            return 'Airbnb'
        elif 'booking' in text or 'booking.com' in text:
            return 'Booking.com'
        elif 'vrbo' in text or 'homeaway' in text:
            return 'VRBO'
        elif 'expedia' in text:
            return 'Expedia'
        elif 'abritel' in text:
            return 'Abritel'

        return None

    def _parse_status(self, status):
        """Convert iCal status to our status"""
        status_str = str(status).upper()
        if status_str in ['CONFIRMED', 'TENTATIVE']:
            return 'confirmed'
        elif status_str == 'CANCELLED':
            return 'cancelled'
        return 'confirmed'

    def sync_calendar_source(self, source_id):
        """Synchronize a calendar source with the remote iCal"""
        # Get source info
        conn = self.db.get_connection()
        source = conn.execute(
            'SELECT * FROM calendar_sources WHERE id=?', (source_id,)
        ).fetchone()
        conn.close()

        if not source:
            raise CalendarError("Source de calendrier introuvable")

        try:
            # Fetch and parse iCal
            ical_content = self.fetch_ical(source['ical_url'])
            events = self.parse_ical(ical_content)

            # Update events in database
            property_id = source['property_id']

            # Clear old events from this source and re-import
            self.db.clear_events_from_source(source_id)

            for event in events:
                self.db.upsert_calendar_event(
                    property_id=property_id,
                    source_id=source_id,
                    uid=event['uid'],
                    start_date=event['start_date'],
                    end_date=event['end_date'],
                    summary=event['summary'],
                    guest_name=event['guest_name'],
                    platform=event['platform'] or source['source_name'],
                    status=event['status']
                )

            # Update sync status
            self.db.update_calendar_sync_status(source_id, 'success')

            return {
                'success': True,
                'events_count': len(events),
                'message': f'{len(events)} événements synchronisés'
            }

        except CalendarError as e:
            self.db.update_calendar_sync_status(source_id, 'error', str(e))
            raise
        except Exception as e:
            error_msg = f"Erreur inattendue: {str(e)}"
            self.db.update_calendar_sync_status(source_id, 'error', error_msg)
            raise CalendarError(error_msg)

    def sync_all_property_sources(self, property_id):
        """Sync all calendar sources for a property"""
        sources = self.db.get_calendar_sources(property_id)
        results = []

        for source in sources:
            if not source['is_active']:
                continue
            try:
                result = self.sync_calendar_source(source['id'])
                results.append({
                    'source_id': source['id'],
                    'source_name': source['source_name'],
                    'success': True,
                    'events_count': result['events_count']
                })
            except CalendarError as e:
                results.append({
                    'source_id': source['id'],
                    'source_name': source['source_name'],
                    'success': False,
                    'error': str(e)
                })

        return results

    def generate_ical_export(self, property_id, property_name=None, property_slug=None):
        """Generate an iCal file for a property's calendar (unified export)"""
        events = self.db.get_calendar_events(property_id)

        cal = Calendar()
        cal.add('prodid', '-//LocApp//Calendar Export//FR')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')
        cal.add('method', 'PUBLISH')
        cal.add('x-wr-calname', f'{property_name or "Property"} - LocApp')

        for event_data in events:
            if event_data['status'] == 'cancelled':
                continue

            event = Event()

            # Create unique UID for export
            uid = event_data.get('uid') or f"locapp-{event_data['id']}-{property_slug or property_id}"
            event.add('uid', uid)

            # Parse dates
            start_date = datetime.fromisoformat(event_data['start_date']).date() if isinstance(event_data['start_date'], str) else event_data['start_date']
            end_date = datetime.fromisoformat(event_data['end_date']).date() if isinstance(event_data['end_date'], str) else event_data['end_date']

            event.add('dtstart', start_date)
            event.add('dtend', end_date)

            # Build summary
            summary_parts = []
            if event_data.get('guest_name'):
                summary_parts.append(event_data['guest_name'])
            if event_data.get('platform'):
                summary_parts.append(f"({event_data['platform']})")
            event.add('summary', ' '.join(summary_parts) if summary_parts else 'Réservé')

            # Add status
            event.add('status', 'CONFIRMED')
            event.add('transp', 'OPAQUE')

            # Add creation/modification timestamps
            now = datetime.now()
            event.add('dtstamp', now)
            event.add('created', now)
            event.add('last-modified', now)

            cal.add_component(event)

        return cal.to_ical()

    def check_availability(self, property_id, check_in, check_out):
        """Check if dates are available for a property"""
        events = self.db.get_calendar_events(property_id, check_in, check_out)

        # Filter out cancelled events
        active_events = [e for e in events if e['status'] != 'cancelled']

        if active_events:
            return {
                'available': False,
                'conflicts': active_events
            }

        return {'available': True, 'conflicts': []}


class CalendarError(Exception):
    """Custom exception for calendar-related errors"""
    pass
