"""
AI Service Module for LocApp
Handles OpenAI API calls and Google Places API for property generation
"""

import os
import requests
from math import radians, cos, sin, sqrt, atan2


class AIService:
    """Service class for AI-powered property content generation"""

    def __init__(self):
        self.openai_client = None
        self.google_maps_key = os.environ.get('GOOGLE_MAPS_API_KEY', '')

    def _get_openai_client(self):
        """Lazy-load OpenAI client"""
        if not self.openai_client:
            import openai
            api_key = os.environ.get('OPENAI_API_KEY', '')
            if not api_key:
                raise ValueError("Clé API OpenAI non configurée")
            self.openai_client = openai.OpenAI(api_key=api_key)
        return self.openai_client

    def generate_property_description(self, address, city, region):
        """Generate a 3-line description of the property area using OpenAI"""
        import random
        client = self._get_openai_client()
        model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')

        # Add variation elements
        angles = ["patrimoine et histoire", "nature et paysages", "gastronomie locale", "art de vivre", "authenticité du terroir"]
        tones = ["poétique", "enthousiaste", "intimiste", "inspirant", "chaleureux"]
        chosen_angle = random.choice(angles)
        chosen_tone = random.choice(tones)

        prompt = f"""Tu es un expert en locations de vacances en France.
Génère une description UNIQUE et ORIGINALE en exactement 3 phrases pour une propriété située à:
Adresse: {address}
Ville: {city}
Région: {region}

Angle principal à mettre en avant: {chosen_angle}
Ton souhaité: {chosen_tone}

La description doit:
- Être {chosen_tone} et accueillante
- Mettre l'accent sur {chosen_angle}
- Donner envie aux voyageurs de découvrir les alentours
- Être COMPLÈTEMENT DIFFÉRENTE à chaque génération

IMPORTANT: Varie les formulations, le vocabulaire et la structure des phrases. Évite les clichés.

Réponds uniquement avec la description, sans introduction ni explication."""

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.95  # Higher temperature for more variation
        )

        return response.choices[0].message.content.strip()

    def generate_welcome_message(self, property_name, address, city, region):
        """Generate a personalized welcome message for the property using OpenAI

        Returns a dictionary with:
        - welcome_title: Short welcome title
        - welcome_message: Main welcome message (2-3 sentences)
        - welcome_description: Brief description of what guests will find
        """
        import random
        client = self._get_openai_client()
        model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')

        # Add variation elements
        styles = ["poétique", "chaleureux", "enthousiaste", "élégant", "authentique", "convivial"]
        themes = ["le repos", "la découverte", "l'aventure", "la détente", "l'évasion", "le ressourcement"]
        chosen_style = random.choice(styles)
        chosen_theme = random.choice(themes)

        prompt = f"""Tu es un hôte chaleureux qui accueille des voyageurs dans sa location de vacances.

Propriété : {property_name}
Adresse : {address}
Ville : {city}
Région : {region}

Génère un message de bienvenue UNIQUE et ORIGINAL pour cette propriété.
Style souhaité : {chosen_style}
Thème principal : {chosen_theme}

IMPORTANT : Génère un contenu complètement différent à chaque fois, avec des formulations variées et créatives.

Réponds UNIQUEMENT en JSON valide avec cette structure exacte (pas de texte avant ou après):
{{
    "welcome_title": "Titre court et accueillant avec un emoji (max 50 caractères)",
    "welcome_message": "Message de bienvenue chaleureux en 2-3 phrases, mentionnant la région et ce qui rend ce lieu spécial.",
    "welcome_description": "Une phrase décrivant ce que les voyageurs trouveront dans ce guide (informations pratiques, conseils locaux, etc.)"
}}

Le message doit :
- Être {chosen_style} et personnel
- Mentionner le nom de la propriété et sa localisation
- Donner envie de découvrir la région
- Utiliser un ou deux emojis appropriés
- Être DIFFÉRENT de tout message précédent"""

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.9  # Higher temperature for more variation
            )

            import json
            content = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            content = content.strip()

            welcome_data = json.loads(content)
            print(f"[AI Service] Generated welcome message for {property_name}")
            return welcome_data

        except Exception as e:
            print(f"[AI Service] Error generating welcome message: {e}")
            # Return default values on error
            return {
                "welcome_title": f"Bienvenue à {property_name} ! 🌿",
                "welcome_message": f"Nous sommes ravis de vous accueillir dans notre propriété située à {city}. Profitez de votre séjour pour découvrir les merveilles de la région {region}.",
                "welcome_description": "Retrouvez ici toutes les informations utiles pour un séjour parfait."
            }

    def find_nearby_places(self, latitude, longitude, place_types):
        """Find nearby places using Google Places API

        Args:
            latitude: Property latitude
            longitude: Property longitude
            place_types: List of tuples (google_type, category_name, icon)
                e.g., [('pharmacy', 'Pharmacie', '💊'), ...]

        Returns:
            List of service dictionaries
        """
        if not self.google_maps_key:
            print("[AI Service] Google Maps API key not configured")
            return []

        results = []

        for google_type, category_name, icon in place_types:
            try:
                url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                params = {
                    'location': f"{latitude},{longitude}",
                    'rankby': 'distance',
                    'type': google_type,
                    'key': self.google_maps_key,
                    'language': 'fr'
                }

                response = requests.get(url, params=params, timeout=10)
                data = response.json()

                if data.get('results'):
                    place = data['results'][0]  # Get nearest

                    # Get place details for phone number
                    place_id = place.get('place_id')
                    details = self._get_place_details(place_id) if place_id else {}

                    results.append({
                        'name': place.get('name'),
                        'category': category_name,
                        'icon': icon,
                        'address': place.get('vicinity', ''),
                        'phone': details.get('formatted_phone_number', ''),
                        'latitude': place['geometry']['location']['lat'],
                        'longitude': place['geometry']['location']['lng'],
                        'opening_hours': self._format_opening_hours(details.get('opening_hours', {}))
                    })
                    print(f"[AI Service] Found {category_name}: {place.get('name')}")
                else:
                    print(f"[AI Service] No {category_name} found nearby")

            except Exception as e:
                print(f"[AI Service] Error finding {category_name}: {e}")

        return results

    def _get_place_details(self, place_id):
        """Get detailed information about a place"""
        try:
            url = "https://maps.googleapis.com/maps/api/place/details/json"
            params = {
                'place_id': place_id,
                'fields': 'formatted_phone_number,opening_hours',
                'key': self.google_maps_key,
                'language': 'fr'
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            return data.get('result', {})
        except Exception as e:
            print(f"[AI Service] Error getting place details: {e}")
            return {}

    def _format_opening_hours(self, opening_hours):
        """Format opening hours to a readable string"""
        if not opening_hours or 'weekday_text' not in opening_hours:
            return ''
        # Return first 3 days as sample
        return '\n'.join(opening_hours['weekday_text'][:3])

    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points in kilometers using Haversine formula"""
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return 6371 * c  # Earth radius in km

    def find_nearest_parking(self, latitude, longitude, city, region):
        """Find nearest parking and determine if it's free

        Args:
            latitude: Property latitude
            longitude: Property longitude
            city: City name for AI pricing estimation
            region: Region name for AI pricing estimation

        Returns:
            Dictionary with parking info or None
        """
        if not self.google_maps_key:
            print("[AI Service] Google Maps API key not configured")
            return None

        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': f"{latitude},{longitude}",
                'rankby': 'distance',
                'type': 'parking',
                'key': self.google_maps_key,
                'language': 'fr'
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if not data.get('results'):
                print("[AI Service] No parking found nearby")
                return None

            parking = data['results'][0]

            # Calculate distance
            parking_lat = parking['geometry']['location']['lat']
            parking_lng = parking['geometry']['location']['lng']
            distance_km = self._calculate_distance(latitude, longitude, parking_lat, parking_lng)

            # Determine if parking appears to be free (heuristic based on name)
            name_lower = parking.get('name', '').lower()
            is_free = any(word in name_lower for word in ['gratuit', 'free', 'public', 'municipal'])

            # Format distance
            if distance_km < 1:
                distance_text = f"{int(distance_km * 1000)} m"
            else:
                distance_text = f"{distance_km:.1f} km"

            # Generate AI description for parking with price estimation if paid
            parking_description = self._generate_parking_description(
                parking.get('name'),
                distance_text,
                is_free,
                city,
                region
            )

            print(f"[AI Service] Found parking: {parking.get('name')} ({distance_text})")

            return {
                'distance': distance_text,
                'description': parking_description,
                'is_free': is_free,
                'tips': f"Parking le plus proche : {parking.get('name')}"
            }

        except Exception as e:
            print(f"[AI Service] Error finding parking: {e}")
            return None

    def _generate_parking_description(self, parking_name, distance, is_free, city, region):
        """Generate a helpful parking description with price estimation if paid"""
        import random
        try:
            client = self._get_openai_client()
            model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')

            # Add variation elements
            tones = ["pratique et direct", "rassurant", "informatif et convivial", "utile et concis"]
            chosen_tone = random.choice(tones)

            if is_free:
                prompt = f"""Génère une courte description UNIQUE (2 phrases max) pour informer les voyageurs sur le stationnement gratuit:
- Parking: {parking_name}
- Distance: {distance}
- Type: Gratuit

Ton souhaité: {chosen_tone}

Varie les formulations. Sois {chosen_tone}. Réponds uniquement avec la description."""
            else:
                prompt = f"""Génère une courte description UNIQUE (2-3 phrases) pour informer les voyageurs sur le stationnement:
- Parking: {parking_name}
- Distance: {distance}
- Ville: {city}
- Région: {region}
- Type: Payant

Ton souhaité: {chosen_tone}

Inclus une estimation du tarif horaire moyen pour un parking dans cette zone (estime selon la ville/région).
Varie les formulations. Sois {chosen_tone}. Réponds uniquement avec la description."""

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.9  # Higher temperature for more variation
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"[AI Service] Error generating parking description: {e}")
            # Fallback description
            if is_free:
                return f"Stationnement gratuit disponible à {distance} de la propriété ({parking_name})."
            else:
                return f"Parking payant à {distance} de la propriété ({parking_name})."

    def generate_activities(self, address, city, region, latitude, longitude):
        """Generate activities for the property location

        Returns a dictionary with activity categories and their items:
        - Incontournables: 3 must-do activities
        - Sport: 3 sports activities nearby
        - Restaurant: 5 best restaurants
        - Visite: 2 nearby cities to visit
        """
        import random
        client = self._get_openai_client()
        model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')

        # Add variation elements
        activity_focus = random.choice(["culture et patrimoine", "nature et plein air", "détente et bien-être", "aventure et découverte", "traditions locales"])
        cuisine_focus = random.choice(["cuisine traditionnelle", "restaurants gastronomiques", "bonnes tables locales", "saveurs du terroir", "tables authentiques"])
        sport_focus = random.choice(["sports nautiques", "randonnées", "sports de montagne", "activités outdoor", "loisirs nature"])

        # Randomize emoji sets for variety
        incontournable_emojis = random.sample(["🎯", "🏛️", "🌟", "✨", "🎭", "🏰", "🌸", "💎", "🗿", "🎨"], 3)
        sport_emojis = random.sample(["⛷️", "🚴", "🏊", "🏄", "🧗", "🥾", "🎣", "⛵", "🏌️", "🎿"], 3)
        restaurant_emojis = random.sample(["🍽️", "🍴", "🥘", "🍕", "🥗", "🍷", "🥐", "🧀", "🍝", "🥖"], 5)

        prompt = f"""Tu es un expert en tourisme en France. Une propriété de location est située à l'adresse suivante :
Adresse : {address}
Ville : {city}
Région : {region}
Coordonnées GPS : {latitude}, {longitude}

Génère des recommandations d'activités UNIQUES et ORIGINALES basées sur cette localisation.

Focus recommandé pour les incontournables : {activity_focus}
Focus recommandé pour les sports : {sport_focus}
Focus recommandé pour les restaurants : {cuisine_focus}

Réponds UNIQUEMENT en JSON valide avec cette structure exacte (pas de texte avant ou après):
{{
    "incontournables": [
        {{"name": "Nom de l'activité", "description": "Description courte (1-2 phrases)", "emoji": "{incontournable_emojis[0]}"}},
        {{"name": "Nom de l'activité 2", "description": "Description courte", "emoji": "{incontournable_emojis[1]}"}},
        {{"name": "Nom de l'activité 3", "description": "Description courte", "emoji": "{incontournable_emojis[2]}"}}
    ],
    "sports": [
        {{"name": "Nom du sport", "description": "Description courte avec lieu si possible", "emoji": "{sport_emojis[0]}"}},
        {{"name": "Nom du sport 2", "description": "Description courte", "emoji": "{sport_emojis[1]}"}},
        {{"name": "Nom du sport 3", "description": "Description courte", "emoji": "{sport_emojis[2]}"}}
    ],
    "restaurants": [
        {{"name": "Nom du restaurant", "description": "Adresse et téléphone si connu, sinon type de cuisine", "emoji": "{restaurant_emojis[0]}"}},
        {{"name": "Restaurant 2", "description": "Adresse et téléphone", "emoji": "{restaurant_emojis[1]}"}},
        {{"name": "Restaurant 3", "description": "Adresse et téléphone", "emoji": "{restaurant_emojis[2]}"}},
        {{"name": "Restaurant 4", "description": "Adresse et téléphone", "emoji": "{restaurant_emojis[3]}"}},
        {{"name": "Restaurant 5", "description": "Adresse et téléphone", "emoji": "{restaurant_emojis[4]}"}}
    ],
    "visites": [
        {{"name": "Ville proche 1", "description": "Distance approximative depuis {city} et ce qu'il y a à voir", "emoji": "🏙️"}},
        {{"name": "Ville proche 2", "description": "Distance approximative depuis {city} et ce qu'il y a à voir", "emoji": "🗺️"}}
    ]
}}

IMPORTANT :
- Génère des recommandations DIFFÉRENTES à chaque appel
- Varie les lieux, descriptions et formulations
- Les incontournables doivent mettre en avant : {activity_focus}
- Les sports doivent être orientés : {sport_focus}
- Les restaurants doivent proposer : {cuisine_focus}
- Les visites doivent être 2 villes intéressantes à visiter depuis {city}

Utilise les emojis fournis et varie les descriptions."""

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.95  # Higher temperature for more variation
            )

            import json
            content = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            content = content.strip()

            activities = json.loads(content)
            print(f"[AI Service] Generated activities for {city}")
            return activities

        except Exception as e:
            print(f"[AI Service] Error generating activities: {e}")
            # Return empty structure on error
            return {
                "incontournables": [],
                "sports": [],
                "restaurants": [],
                "visites": []
            }

    def find_restaurants(self, latitude, longitude, limit=5):
        """Find nearby restaurants using Google Places API"""
        if not self.google_maps_key:
            print("[AI Service] Google Maps API key not configured")
            return []

        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': f"{latitude},{longitude}",
                'radius': 5000,  # 5km radius
                'type': 'restaurant',
                'key': self.google_maps_key,
                'language': 'fr'
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            results = []
            if data.get('results'):
                for place in data['results'][:limit]:
                    place_id = place.get('place_id')
                    details = self._get_place_details(place_id) if place_id else {}

                    phone = details.get('formatted_phone_number', '')
                    address = place.get('vicinity', '')
                    description = f"{address}"
                    if phone:
                        description += f" - Tél: {phone}"

                    results.append({
                        'name': place.get('name'),
                        'description': description,
                        'emoji': '🍽️',
                        'rating': place.get('rating', 0)
                    })

            # Sort by rating
            results.sort(key=lambda x: x.get('rating', 0), reverse=True)
            print(f"[AI Service] Found {len(results)} restaurants")
            return results

        except Exception as e:
            print(f"[AI Service] Error finding restaurants: {e}")
            return []
