from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from database import Database
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import json
import hashlib
import secrets
import os
import re
import smtplib
import uuid
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps

# Load environment variables from .env-weblocapp file
load_dotenv('.env-weblocapp')

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'locapp-secret-key-change-in-production')

# Configuration pour les uploads de photos
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads', 'photos')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Créer le dossier d'upload s'il n'existe pas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')

# Google Maps API Key (for Places Autocomplete and Maps)
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')
app.config['GOOGLE_MAPS_API_KEY'] = GOOGLE_MAPS_API_KEY

# Initialize OAuth
oauth = OAuth(app)

# Only register Google OAuth if credentials are configured
if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    google = oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
else:
    google = None

db = Database()

# Simple authentication (in production, use proper authentication)
USERNAME = 'admin'
PASSWORD = 'admin'

# Email configuration for notifications
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'myskyidentity@gmail.com',
    'sender_password': '',  # Configure via SENDER_PASSWORD env var
    'notification_email': 'abonard@gmail.com'
}

# Session storage (sessions are temporary, users are in database)
# Structure: {token: {'email': str, 'login_time': datetime, 'last_activity': datetime, 'user_agent': str, 'ip_address': str}}
sessions_db = {}

class User:
    def __init__(self, id, email, firstname, lastname, password_hash=None):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.password_hash = password_hash
        self.is_authenticated = True

    @staticmethod
    def from_db(data):
        """Create User object from database row"""
        if not data:
            return None
        return User(
            id=data['id'],
            email=data['email'],
            firstname=data['firstname'],
            lastname=data['lastname'],
            password_hash=data.get('password_hash')
        )

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'firstname': self.firstname,
            'lastname': self.lastname
        }

def get_current_user():
    """Get current user from session (stored in database)"""
    token = session.get('auth_token')
    if token and token in sessions_db:
        session_data = sessions_db[token]
        # Handle both old (string) and new (dict) session formats
        if isinstance(session_data, dict):
            email = session_data['email']
            # Update last activity
            session_data['last_activity'] = datetime.now()
        else:
            email = session_data
        user_data = db.get_user_by_email(email)
        return User.from_db(user_data)
    return None

def create_session(email, request_obj=None):
    """Create a new session with detailed tracking"""
    token = secrets.token_urlsafe(32)
    sessions_db[token] = {
        'email': email,
        'login_time': datetime.now(),
        'last_activity': datetime.now(),
        'user_agent': request_obj.headers.get('User-Agent', 'Unknown') if request_obj else 'Unknown',
        'ip_address': request_obj.remote_addr if request_obj else 'Unknown'
    }
    return token

def get_active_sessions():
    """Get list of all active sessions with user details"""
    active_sessions = []
    for token, session_data in sessions_db.items():
        # Handle both old (string) and new (dict) session formats
        if isinstance(session_data, dict):
            email = session_data['email']
            login_time = session_data.get('login_time')
            last_activity = session_data.get('last_activity')
            user_agent = session_data.get('user_agent', 'Unknown')
            ip_address = session_data.get('ip_address', 'Unknown')
        else:
            email = session_data
            login_time = None
            last_activity = None
            user_agent = 'Unknown'
            ip_address = 'Unknown'

        # Get user details from database
        user_data = db.get_user_by_email(email)
        if user_data:
            active_sessions.append({
                'email': email,
                'firstname': user_data.get('firstname', ''),
                'lastname': user_data.get('lastname', ''),
                'login_time': login_time.isoformat() if login_time else None,
                'last_activity': last_activity.isoformat() if last_activity else None,
                'user_agent': user_agent,
                'ip_address': ip_address,
                'token_preview': token[:8] + '...'  # Show only first 8 chars for security
            })
    return active_sessions

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def send_notification_email(user):
    """Send notification email when a new user registers"""
    try:
        subject = "Nouvel inscrit sur LocAPP"
        body = f"Mr {user.lastname} {user.firstname} s'est inscrit avec l'adresse mail {user.email}"

        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = EMAIL_CONFIG['notification_email']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Note: In production, configure SMTP credentials
        # For now, just log the email
        print(f"[EMAIL NOTIFICATION] To: {EMAIL_CONFIG['notification_email']}")
        print(f"[EMAIL NOTIFICATION] Subject: {subject}")
        print(f"[EMAIL NOTIFICATION] Body: {body}")

        # Uncomment below to actually send email when SMTP is configured
        # with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
        #     server.starttls()
        #     server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        #     server.send_message(msg)

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def requires_auth(f):
    """Decorator for routes that require user authentication (session-based)"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated

def requires_user_auth(f):
    """Decorator for routes that require user authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated

def get_property_id():
    """Get property_id from query parameter, default to 1 (Mazet BSA)"""
    return request.args.get('property_id', 1, type=int)

def user_owns_property(user, property_id):
    """Check if user owns the given property"""
    if not user:
        return False
    user_properties = db.get_properties_by_user(user.id)
    return any(p['id'] == property_id for p in user_properties)

def get_verified_property_id():
    """Get property_id only if user owns it, otherwise return None"""
    current_user = get_current_user()
    property_id = get_property_id()

    if not current_user:
        return None

    if not user_owns_property(current_user, property_id):
        return None

    return property_id

# ============================================
# Commercial Site Routes
# ============================================

@app.route('/site')
def commercial_home():
    """Landing page for LocAPP commercial site"""
    current_user = get_current_user()
    return render_template('commercial/home.html', current_user=current_user)

@app.route('/site/fonctionnalites')
def commercial_features():
    """Features page"""
    current_user = get_current_user()
    return render_template('commercial/features.html', current_user=current_user)

@app.route('/site/tarifs')
def commercial_pricing():
    """Pricing page"""
    current_user = get_current_user()
    return render_template('commercial/pricing.html', current_user=current_user)

@app.route('/site/demo')
def commercial_demo():
    """Demo page with video"""
    current_user = get_current_user()
    return render_template('commercial/demo.html', current_user=current_user)

@app.route('/site/connexion')
def login():
    """Login/Register page"""
    current_user = get_current_user()
    if current_user:
        return redirect(url_for('admin_home'))
    return render_template('commercial/login.html', current_user=None)

@app.route('/logout')
def logout():
    """Logout user"""
    token = session.get('auth_token')
    if token and token in sessions_db:
        del sessions_db[token]
    session.pop('auth_token', None)
    return redirect(url_for('commercial_home'))

# ============================================
# Authentication API Routes
# ============================================

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    """Register a new user"""
    data = request.json
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    firstname = data.get('firstname', '').strip()
    lastname = data.get('lastname', '').strip()

    # Validation
    if not email or not password or not firstname or not lastname:
        return jsonify({'error': 'Tous les champs sont requis'}), 400

    if len(password) < 8:
        return jsonify({'error': 'Le mot de passe doit contenir au moins 8 caractères'}), 400

    # Check if user already exists in database
    existing_user = db.get_user_by_email(email)
    if existing_user:
        return jsonify({'error': 'Cette adresse email est déjà utilisée'}), 400

    # Create user in database
    user_id = db.create_user({
        'email': email,
        'firstname': firstname,
        'lastname': lastname,
        'password_hash': hash_password(password),
        'password_plain': password
    })

    user = User(
        id=user_id,
        email=email,
        firstname=firstname,
        lastname=lastname,
        password_hash=hash_password(password)
    )

    # Create session token with tracking
    token = create_session(email, request)
    session['auth_token'] = token

    # Send notification email
    send_notification_email(user)

    return jsonify({
        'success': True,
        'token': token,
        'user': user.to_dict(),
        'message': 'Compte créé avec succès'
    })

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """Login user"""
    data = request.json
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')

    # Check credentials from database
    user_data = db.get_user_by_email(email)
    if not user_data or user_data.get('password_hash') != hash_password(password):
        return jsonify({'error': 'Email ou mot de passe incorrect'}), 401

    user = User.from_db(user_data)

    # Create session token with tracking
    token = create_session(email, request)
    session['auth_token'] = token

    return jsonify({
        'success': True,
        'token': token,
        'user': user.to_dict(),
        'message': 'Connexion réussie'
    })

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    """Logout user"""
    token = session.get('auth_token')
    if token and token in sessions_db:
        del sessions_db[token]
    session.pop('auth_token', None)
    return jsonify({'success': True, 'message': 'Déconnexion réussie'})

@app.route('/api/auth/google')
def google_login():
    """Google OAuth - redirect to Google for authentication"""
    if not google:
        return jsonify({
            'error': 'Google OAuth non configuré. Définissez GOOGLE_CLIENT_ID et GOOGLE_CLIENT_SECRET.'
        }), 501

    # Generate redirect URI
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/api/auth/google/callback')
def google_callback():
    """Google OAuth callback - handle the response from Google"""
    if not google:
        return redirect(url_for('login'))

    try:
        # Get the token from Google
        token = google.authorize_access_token()

        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            # Fetch user info if not in token
            resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')
            user_info = resp.json()

        email = user_info.get('email', '').lower()
        firstname = user_info.get('given_name', '')
        lastname = user_info.get('family_name', '')
        google_id = user_info.get('sub', '')

        if not email:
            return redirect(url_for('login') + '?error=no_email')

        # Check if user already exists in database
        user_data = db.get_user_by_email(email)

        if not user_data:
            # Create new user in database (Google users don't have password)
            user_id = db.create_user({
                'email': email,
                'firstname': firstname or 'Utilisateur',
                'lastname': lastname or 'Google',
                'password_hash': None,
                'google_id': google_id
            })
            user = User(
                id=user_id,
                email=email,
                firstname=firstname or 'Utilisateur',
                lastname=lastname or 'Google',
                password_hash=None
            )

            # Send notification email for new user
            send_notification_email(user)
        else:
            user = User.from_db(user_data)

        # Create session token with tracking
        auth_token = create_session(email, request)
        session['auth_token'] = auth_token

        # Redirect to admin home
        return redirect(url_for('admin_home'))

    except Exception as e:
        print(f"Google OAuth error: {e}")
        return redirect(url_for('login') + '?error=oauth_failed')

@app.route('/api/auth/me')
def api_current_user():
    """Get current authenticated user"""
    user = get_current_user()
    if user:
        return jsonify({'user': user.to_dict()})
    return jsonify({'user': None})

# ============================================
# Password Reset Routes
# ============================================

@app.route('/site/mot-de-passe-oublie')
def forgot_password_page():
    """Page to request password reset"""
    current_user = get_current_user()
    if current_user:
        return redirect(url_for('admin_home'))
    return render_template('commercial/forgot_password.html', current_user=None)

@app.route('/site/reinitialiser-mot-de-passe/<token>')
def reset_password_page(token):
    """Page to reset password with token"""
    # Verify token is valid
    token_data = db.get_valid_reset_token(token)
    if not token_data:
        return render_template('commercial/reset_password.html',
                             current_user=None,
                             error='Ce lien de réinitialisation est invalide ou a expiré.',
                             token=None)
    return render_template('commercial/reset_password.html',
                         current_user=None,
                         token=token,
                         email=token_data['email'])

@app.route('/api/auth/forgot-password', methods=['POST'])
def api_forgot_password():
    """Request password reset email"""
    data = request.json
    email = data.get('email', '').lower().strip()

    if not email:
        return jsonify({'error': 'L\'adresse email est requise'}), 400

    # Check if user exists
    user_data = db.get_user_by_email(email)

    # Always return success to prevent email enumeration
    if not user_data:
        return jsonify({
            'success': True,
            'message': 'Si cette adresse email est associée à un compte, vous recevrez un lien de réinitialisation.'
        })

    # Check if user is a Google-only user (no password)
    if user_data.get('google_id') and not user_data.get('password_hash'):
        return jsonify({
            'success': True,
            'message': 'Si cette adresse email est associée à un compte, vous recevrez un lien de réinitialisation.'
        })

    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=1)

    # Save token to database
    db.create_password_reset_token(user_data['id'], reset_token, expires_at.isoformat())

    # Send reset email
    send_password_reset_email(user_data, reset_token)

    return jsonify({
        'success': True,
        'message': 'Si cette adresse email est associée à un compte, vous recevrez un lien de réinitialisation.'
    })

@app.route('/api/auth/reset-password', methods=['POST'])
def api_reset_password():
    """Reset password with token"""
    data = request.json
    token = data.get('token', '')
    new_password = data.get('password', '')

    if not token or not new_password:
        return jsonify({'error': 'Token et mot de passe requis'}), 400

    if len(new_password) < 8:
        return jsonify({'error': 'Le mot de passe doit contenir au moins 8 caractères'}), 400

    # Verify token
    token_data = db.get_valid_reset_token(token)
    if not token_data:
        return jsonify({'error': 'Ce lien de réinitialisation est invalide ou a expiré'}), 400

    # Update password
    db.update_user_password(token_data['user_id'], hash_password(new_password), new_password)

    # Mark token as used
    db.mark_token_as_used(token)

    return jsonify({
        'success': True,
        'message': 'Votre mot de passe a été réinitialisé avec succès'
    })

def send_password_reset_email(user_data, token):
    """Send password reset email"""
    try:
        reset_url = url_for('reset_password_page', token=token, _external=True)

        subject = "Réinitialisation de votre mot de passe LocAPP"
        body = f"""Bonjour {user_data['firstname']},

Vous avez demandé la réinitialisation de votre mot de passe sur LocAPP.

Cliquez sur le lien ci-dessous pour définir un nouveau mot de passe :
{reset_url}

Ce lien est valable pendant 1 heure.

Si vous n'avez pas demandé cette réinitialisation, ignorez simplement cet email.

Cordialement,
L'équipe LocAPP
"""

        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = user_data['email']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Log the email (for development)
        print(f"[PASSWORD RESET EMAIL] To: {user_data['email']}")
        print(f"[PASSWORD RESET EMAIL] Subject: {subject}")
        print(f"[PASSWORD RESET EMAIL] Reset URL: {reset_url}")

        # Send email if SMTP is configured
        smtp_password = os.environ.get('SENDER_PASSWORD', '')
        if smtp_password:
            with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
                server.starttls()
                server.login(os.environ.get('SENDER_EMAIL', EMAIL_CONFIG['sender_email']), smtp_password)
                server.send_message(msg)
                print(f"[PASSWORD RESET EMAIL] Email sent successfully to {user_data['email']}")

        return True
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False

# ============================================
# Admin Routes (existing)
# ============================================

def get_user_properties(current_user):
    """Get properties for the current user"""
    if current_user:
        return db.get_properties_by_user(current_user.id)
    return []

@app.route('/')
def home():
    """Redirect to commercial site"""
    return redirect(url_for('commercial_home'))

@app.route('/admin')
def admin_home():
    """Admin dashboard"""
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    return render_template('index.html', properties=properties, current_user=current_user)

@app.route('/property/new')
def new_property_page():
    """Page to create a new property"""
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    return render_template('property_new.html', properties=properties, current_user=current_user, config=app.config)

@app.route('/general')
def general_page():
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    return render_template('general.html', properties=properties, current_user=current_user)

@app.route('/wifi')
def wifi_page():
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    return render_template('wifi.html', properties=properties, current_user=current_user)

@app.route('/address')
def address_page():
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    return render_template('address.html', properties=properties, current_user=current_user)

@app.route('/parking')
def parking_page():
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    return render_template('parking.html', properties=properties, current_user=current_user)

@app.route('/access')
def access_page():
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    return render_template('access.html', properties=properties, current_user=current_user)

@app.route('/contact')
def contact_page():
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    return render_template('contact.html', properties=properties, current_user=current_user)

@app.route('/activities')
def activities_page():
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    return render_template('activities.html', properties=properties, current_user=current_user)

@app.route('/services')
def services_page():
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    return render_template('services.html', properties=properties, current_user=current_user)

@app.route('/emergency')
def emergency_page():
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    return render_template('emergency.html', properties=properties, current_user=current_user)

@app.route('/photos')
def photos_page():
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    return render_template('photos.html', properties=properties, current_user=current_user)

@app.route('/equipements')
def equipements_page():
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    return render_template('equipements.html', properties=properties, current_user=current_user)

# API Routes - Properties
@app.route('/api/properties', methods=['GET'])
def get_properties():
    current_user = get_current_user()
    if current_user:
        data = db.get_properties_by_user(current_user.id)
    else:
        data = []
    return jsonify(data)

@app.route('/api/properties/<slug>', methods=['GET'])
def get_property_by_slug(slug):
    data = db.get_property_by_slug(slug)
    if data:
        return jsonify(data)
    return jsonify({'error': 'Property not found'}), 404

@app.route('/api/properties/<int:property_id>', methods=['GET'])
def get_property(property_id):
    data = db.get_property(property_id)
    if data:
        return jsonify(data)
    return jsonify({'error': 'Property not found'}), 404

@app.route('/api/properties', methods=['POST'])
def create_property():
    """Create a new property by duplicating the template (Mazet-Demo)"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Vous devez être connecté pour créer une propriété'}), 401

    data = request.json
    name = data.get('name', '').strip()
    address = data.get('address', '').strip()
    icon = data.get('icon', '🏠')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    display_name = data.get('display_name', '').strip()  # Full address from Nominatim
    region = data.get('region', '').strip()  # Region extracted from Nominatim

    if not name or not address:
        return jsonify({'error': 'Le nom et l\'adresse sont requis'}), 400

    # Generate slug from name
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

    # Get the template property ID (Mazet-Demo)
    template_id = db.get_template_property_id()

    if template_id:
        # Create property by duplicating the template
        property_id = db.duplicate_property_from_template(
            template_property_id=template_id,
            new_property_data={
                'name': name,
                'slug': slug,
                'icon': icon,
                'address': display_name or address,  # Use full address from Nominatim if available
                'latitude': latitude,
                'longitude': longitude,
                'region': region
            },
            user_id=current_user.id
        )
        message = 'Propriété créée avec succès à partir du modèle'
    else:
        # Fallback: create property with default values
        property_id = db.create_property({
            'name': name,
            'slug': slug,
            'icon': icon,
            'address': display_name or address,
            'latitude': latitude,
            'longitude': longitude,
            'region': region
        }, user_id=current_user.id)
        message = 'Propriété créée avec succès'

    return jsonify({
        'success': True,
        'id': property_id,
        'slug': slug,
        'message': message
    })

# API Routes - General Info
@app.route('/api/general', methods=['GET'])
def get_general_info():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({})
    data = db.get_general_info(property_id)
    return jsonify(data)

@app.route('/api/general', methods=['PUT'])
@requires_auth
def update_general_info():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Accès non autorisé à cette propriété'}), 403
    data = request.json
    db.update_general_info(property_id, data)
    return jsonify({'success': True, 'message': 'Informations générales mises à jour'})

@app.route('/api/general/header-image', methods=['POST'])
@requires_auth
def upload_header_image():
    """Upload a header image for the property"""
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Accès non autorisé à cette propriété'}), 403

    if 'image' not in request.files:
        return jsonify({'error': 'Aucune image fournie'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400

    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in allowed_extensions:
        return jsonify({'error': 'Type de fichier non autorisé. Utilisez PNG, JPG, GIF ou WebP'}), 400

    # Create uploads directory if it doesn't exist
    upload_dir = os.path.join(app.static_folder, 'uploads', 'headers')
    os.makedirs(upload_dir, exist_ok=True)

    # Generate unique filename
    filename = f"header_{property_id}_{int(datetime.now().timestamp())}.{ext}"
    filepath = os.path.join(upload_dir, filename)

    # Delete old header image if exists
    general_info = db.get_general_info(property_id)
    if general_info and general_info.get('header_image'):
        old_filepath = os.path.join(upload_dir, general_info['header_image'])
        if os.path.exists(old_filepath):
            os.remove(old_filepath)

    # Save the new file
    file.save(filepath)

    # Update database
    db.update_header_image(property_id, filename)

    return jsonify({
        'success': True,
        'message': 'Image d\'en-tête mise à jour',
        'filename': filename,
        'url': f'/static/uploads/headers/{filename}'
    })

@app.route('/api/general/header-image', methods=['DELETE'])
@requires_auth
def delete_header_image():
    """Delete the header image for the property"""
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Accès non autorisé à cette propriété'}), 403

    # Get current header image
    general_info = db.get_general_info(property_id)
    if general_info and general_info.get('header_image'):
        # Delete the file
        upload_dir = os.path.join(app.static_folder, 'uploads', 'headers')
        filepath = os.path.join(upload_dir, general_info['header_image'])
        if os.path.exists(filepath):
            os.remove(filepath)

    # Update database
    db.delete_header_image(property_id)

    return jsonify({'success': True, 'message': 'Image d\'en-tête supprimée'})

# API Routes - WiFi
@app.route('/api/wifi', methods=['GET'])
def get_wifi():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({})
    data = db.get_wifi_config(property_id)
    return jsonify(data)

@app.route('/api/wifi', methods=['PUT'])
@requires_auth
def update_wifi():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Accès non autorisé à cette propriété'}), 403
    data = request.json
    db.update_wifi_config(property_id, data)
    return jsonify({'success': True, 'message': 'Configuration WiFi mise à jour'})

# API Routes - Address
@app.route('/api/address', methods=['GET'])
def get_address():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({})
    data = db.get_address(property_id)
    return jsonify(data)

@app.route('/api/address', methods=['PUT'])
@requires_auth
def update_address():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Accès non autorisé à cette propriété'}), 403
    data = request.json
    db.update_address(property_id, data)
    return jsonify({'success': True, 'message': 'Adresse mise à jour'})

# API Routes - Parking
@app.route('/api/parking', methods=['GET'])
def get_parking():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({})
    data = db.get_parking_info(property_id)
    return jsonify(data)

@app.route('/api/parking', methods=['PUT'])
@requires_auth
def update_parking():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Accès non autorisé à cette propriété'}), 403
    data = request.json
    db.update_parking_info(property_id, data)
    return jsonify({'success': True, 'message': 'Informations parking mises à jour'})

# API Routes - Access
@app.route('/api/access', methods=['GET'])
def get_access():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({})
    data = db.get_access_info(property_id)
    return jsonify(data)

@app.route('/api/access', methods=['PUT'])
@requires_auth
def update_access():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Accès non autorisé à cette propriété'}), 403
    data = request.json
    db.update_access_info(property_id, data)
    return jsonify({'success': True, 'message': 'Informations d\'accès mises à jour'})

# API Routes - Contact
@app.route('/api/contact', methods=['GET'])
def get_contact():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({})
    data = db.get_contact_info(property_id)
    return jsonify(data)

@app.route('/api/contact', methods=['PUT'])
@requires_auth
def update_contact():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Accès non autorisé à cette propriété'}), 403
    data = request.json
    db.update_contact_info(property_id, data)
    return jsonify({'success': True, 'message': 'Informations de contact mises à jour'})

@app.route('/api/contact/avatar', methods=['POST'])
@requires_auth
def upload_contact_avatar():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Accès non autorisé à cette propriété'}), 403

    if 'avatar' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400

    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Type de fichier non autorisé. Utilisez: png, jpg, jpeg, gif, webp'}), 400

    # Generate unique filename for avatar
    original_name = secure_filename(file.filename)
    ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else 'jpg'
    unique_filename = f"avatar_{property_id}_{uuid.uuid4().hex}.{ext}"

    # Create avatars subfolder
    avatars_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'avatars')
    os.makedirs(avatars_folder, exist_ok=True)

    # Save file
    filepath = os.path.join(avatars_folder, unique_filename)
    file.save(filepath)

    # Update database with avatar filename
    db.update_contact_avatar(property_id, f"avatars/{unique_filename}")

    return jsonify({
        'success': True,
        'avatar': f"avatars/{unique_filename}",
        'message': 'Avatar mis à jour avec succès'
    })

@app.route('/api/contact/avatar', methods=['DELETE'])
@requires_auth
def delete_contact_avatar():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Accès non autorisé à cette propriété'}), 403

    # Get current avatar
    contact = db.get_contact_info(property_id)
    if contact and contact.get('avatar'):
        # Delete file from disk
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], contact['avatar'])
        if os.path.exists(filepath):
            os.remove(filepath)

    # Update database to remove avatar
    db.update_contact_avatar(property_id, None)

    return jsonify({'success': True, 'message': 'Avatar supprimé'})

# API Routes - Activities
@app.route('/api/activities', methods=['GET'])
def get_activities():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify([])
    data = db.get_all_activities(property_id)
    return jsonify(data)

@app.route('/api/activities/<int:activity_id>', methods=['GET'])
def get_activity(activity_id):
    data = db.get_activity(activity_id)
    if data:
        return jsonify(data)
    return jsonify({'error': 'Activity not found'}), 404

@app.route('/api/activities', methods=['POST'])
@requires_auth
def create_activity():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Accès non autorisé à cette propriété'}), 403
    data = request.json
    activity_id = db.create_activity(data, property_id)
    return jsonify({'success': True, 'id': activity_id, 'message': 'Activité créée'})

@app.route('/api/activities/<int:activity_id>', methods=['PUT'])
@requires_auth
def update_activity(activity_id):
    data = request.json
    db.update_activity(activity_id, data)
    return jsonify({'success': True, 'message': 'Activité mise à jour'})

@app.route('/api/activities/<int:activity_id>', methods=['DELETE'])
@requires_auth
def delete_activity(activity_id):
    db.delete_activity(activity_id)
    return jsonify({'success': True, 'message': 'Activité supprimée'})

# API Routes - Activity Categories
@app.route('/api/activity-categories', methods=['GET'])
def get_activity_categories():
    data = db.get_all_activity_categories()
    return jsonify(data)

# API Routes - Nearby Services
@app.route('/api/services', methods=['GET'])
def get_services():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify([])
    data = db.get_all_nearby_services(property_id)
    return jsonify(data)

@app.route('/api/services/<int:service_id>', methods=['GET'])
def get_service(service_id):
    data = db.get_nearby_service(service_id)
    if data:
        return jsonify(data)
    return jsonify({'error': 'Service not found'}), 404

@app.route('/api/services', methods=['POST'])
@requires_auth
def create_service():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Accès non autorisé à cette propriété'}), 403
    data = request.json
    service_id = db.create_nearby_service(data, property_id)
    return jsonify({'success': True, 'id': service_id, 'message': 'Service créé'})

@app.route('/api/services/<int:service_id>', methods=['PUT'])
@requires_auth
def update_service(service_id):
    data = request.json
    db.update_nearby_service(service_id, data)
    return jsonify({'success': True, 'message': 'Service mis à jour'})

@app.route('/api/services/<int:service_id>', methods=['DELETE'])
@requires_auth
def delete_service(service_id):
    db.delete_nearby_service(service_id)
    return jsonify({'success': True, 'message': 'Service supprimé'})

# API Routes - Emergency Numbers
@app.route('/api/emergency', methods=['GET'])
def get_emergency():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify([])
    data = db.get_all_emergency_numbers(property_id)
    return jsonify(data)

# API Routes - Amenities (Équipements)
@app.route('/api/amenities', methods=['GET'])
def get_amenities():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify([])
    # Initialize amenities if not yet done
    db.initialize_amenities_for_property(property_id)
    data = db.get_all_amenities(property_id)
    return jsonify(data)

@app.route('/api/amenities/available', methods=['GET'])
def get_available_amenities():
    """Get only available amenities (for guest display)"""
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify([])
    data = db.get_available_amenities(property_id)
    return jsonify(data)

@app.route('/api/amenities/<int:amenity_id>', methods=['GET'])
def get_amenity(amenity_id):
    data = db.get_amenity(amenity_id)
    if data:
        return jsonify(data)
    return jsonify({'error': 'Amenity not found'}), 404

@app.route('/api/amenities/<int:amenity_id>/toggle', methods=['POST'])
@requires_auth
def toggle_amenity(amenity_id):
    """Toggle the availability of an amenity"""
    data = request.json
    is_available = data.get('is_available', False)
    db.toggle_amenity(amenity_id, is_available)
    return jsonify({'success': True, 'message': 'Équipement mis à jour'})

@app.route('/api/amenities/bulk-update', methods=['POST'])
@requires_auth
def bulk_update_amenities():
    """Update multiple amenities at once"""
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Accès non autorisé à cette propriété'}), 403

    data = request.json
    amenities_status = data.get('amenities', {})  # {amenity_id: is_available}

    for amenity_id, is_available in amenities_status.items():
        db.toggle_amenity(int(amenity_id), is_available)

    return jsonify({'success': True, 'message': 'Équipements enregistrés avec succès'})

@app.route('/api/amenities', methods=['POST'])
@requires_auth
def create_amenity():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Accès non autorisé à cette propriété'}), 403
    data = request.json
    amenity_id = db.create_amenity(property_id, data)
    return jsonify({'success': True, 'id': amenity_id, 'message': 'Équipement créé'})

@app.route('/api/amenities/<int:amenity_id>', methods=['PUT'])
@requires_auth
def update_amenity(amenity_id):
    data = request.json
    db.update_amenity(amenity_id, data)
    return jsonify({'success': True, 'message': 'Équipement mis à jour'})

@app.route('/api/amenities/<int:amenity_id>', methods=['DELETE'])
@requires_auth
def delete_amenity(amenity_id):
    db.delete_amenity(amenity_id)
    return jsonify({'success': True, 'message': 'Équipement supprimé'})

@app.route('/api/amenity-categories', methods=['GET'])
def get_amenity_categories():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify([])
    data = db.get_amenity_categories(property_id)
    return jsonify(data)

# Export endpoint
@app.route('/api/export', methods=['GET'])
def export_data():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({})
    data = db.export_all_data(property_id)
    return jsonify(data)

@app.route('/api/export/download', methods=['GET'])
@requires_auth
def download_export():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Accès non autorisé à cette propriété'}), 403
    data = db.export_all_data(property_id)

    # Get property info for filename
    property_info = db.get_property(property_id)
    filename = f'locapp_{property_info["slug"] if property_info else "export"}.json'

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return send_file(filename, as_attachment=True, download_name=filename)

# API Routes - Photos
@app.route('/api/photos', methods=['GET'])
def get_photos():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify([])
    data = db.get_all_photos(property_id)
    return jsonify(data)

@app.route('/api/photos', methods=['POST'])
@requires_auth
def upload_photo():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Accès non autorisé à cette propriété'}), 403

    if 'photo' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400

    file = request.files['photo']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Type de fichier non autorisé. Utilisez: png, jpg, jpeg, gif, webp'}), 400

    # Generate unique filename
    original_name = secure_filename(file.filename)
    ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else 'jpg'
    unique_filename = f"{property_id}_{uuid.uuid4().hex}.{ext}"

    # Create property subfolder
    property_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(property_id))
    os.makedirs(property_folder, exist_ok=True)

    # Save file
    filepath = os.path.join(property_folder, unique_filename)
    file.save(filepath)

    # Get optional metadata
    title = request.form.get('title', '')
    description = request.form.get('description', '')

    # Save to database
    photo_id = db.create_photo({
        'filename': f"{property_id}/{unique_filename}",
        'original_name': original_name,
        'title': title,
        'description': description
    }, property_id)

    return jsonify({
        'success': True,
        'id': photo_id,
        'filename': f"{property_id}/{unique_filename}",
        'message': 'Photo uploadée avec succès'
    })

@app.route('/api/photos/<int:photo_id>', methods=['PUT'])
@requires_auth
def update_photo(photo_id):
    # Get photo to verify ownership
    photo = db.get_photo(photo_id)
    if not photo:
        return jsonify({'error': 'Photo non trouvée'}), 404

    property_id = get_verified_property_id()
    if not property_id or photo['property_id'] != property_id:
        return jsonify({'error': 'Accès non autorisé'}), 403

    data = request.json
    db.update_photo(photo_id, data)
    return jsonify({'success': True, 'message': 'Photo mise à jour'})

@app.route('/api/photos/<int:photo_id>', methods=['DELETE'])
@requires_auth
def delete_photo(photo_id):
    # Get photo to verify ownership and get filename
    photo = db.get_photo(photo_id)
    if not photo:
        return jsonify({'error': 'Photo non trouvée'}), 404

    property_id = get_verified_property_id()
    if not property_id or photo['property_id'] != property_id:
        return jsonify({'error': 'Accès non autorisé'}), 403

    # Delete file from disk
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], photo['filename'])
    if os.path.exists(filepath):
        os.remove(filepath)

    # Delete from database
    db.delete_photo(photo_id)
    return jsonify({'success': True, 'message': 'Photo supprimée'})

# ============================================
# SuperAdmin Routes (Secure Database Admin)
# ============================================

# SuperAdmin credentials (hashed for security)
SUPERADMIN_USERNAME = 'Alex'
SUPERADMIN_PASSWORD_HASH = hashlib.sha256('River'.encode()).hexdigest()

def check_superadmin():
    """Check if user is authenticated as superadmin"""
    return session.get('superadmin_authenticated') == True

def requires_superadmin(f):
    """Decorator for routes that require superadmin authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not check_superadmin():
            return redirect(url_for('superadmin_login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/superadmin')
def superadmin_redirect():
    """Redirect to superadmin login or dashboard"""
    if check_superadmin():
        return redirect(url_for('superadmin_dashboard'))
    return redirect(url_for('superadmin_login'))

@app.route('/superadmin/login', methods=['GET', 'POST'])
def superadmin_login():
    """SuperAdmin login page"""
    if check_superadmin():
        return redirect(url_for('superadmin_dashboard'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        if username == SUPERADMIN_USERNAME and password_hash == SUPERADMIN_PASSWORD_HASH:
            session['superadmin_authenticated'] = True
            session['superadmin_user'] = username
            return redirect(url_for('superadmin_dashboard'))
        else:
            error = 'Identifiants incorrects'

    return render_template('superadmin_login.html', error=error)

@app.route('/superadmin/logout')
def superadmin_logout():
    """Logout from superadmin"""
    session.pop('superadmin_authenticated', None)
    session.pop('superadmin_user', None)
    return redirect(url_for('superadmin_login'))

@app.route('/superadmin/logout-silent', methods=['GET', 'POST'])
def superadmin_logout_silent():
    """Silent logout for superadmin (used by beforeunload)"""
    session.pop('superadmin_authenticated', None)
    session.pop('superadmin_user', None)
    return '', 204  # No content response

@app.route('/superadmin/dashboard')
@requires_superadmin
def superadmin_dashboard():
    """SuperAdmin dashboard"""
    conn = db.get_connection()

    # Get active sessions
    active_sessions = get_active_sessions()

    # Get stats
    stats = {
        'users': conn.execute('SELECT COUNT(*) FROM users').fetchone()[0],
        'properties': conn.execute('SELECT COUNT(*) FROM properties').fetchone()[0],
        'activities': conn.execute('SELECT COUNT(*) FROM activities').fetchone()[0],
        'services': conn.execute('SELECT COUNT(*) FROM nearby_services').fetchone()[0],
        'active_sessions': len(active_sessions),
    }

    # Get all users
    users = [dict(row) for row in conn.execute('SELECT * FROM users ORDER BY id DESC').fetchall()]

    # Get all properties with owner email (including inactive)
    properties_rows = conn.execute('''
        SELECT p.*, u.email as owner_email
        FROM properties p
        LEFT JOIN users u ON p.user_id = u.id
        ORDER BY p.id
    ''').fetchall()
    properties = [dict(row) for row in properties_rows]

    conn.close()

    return render_template('superadmin.html',
        stats=stats,
        users=users,
        properties=properties,
        active_sessions=active_sessions,
        admin_user=session.get('superadmin_user', 'Admin')
    )

# SuperAdmin API Routes
@app.route('/superadmin/api/users/<int:user_id>', methods=['DELETE'])
@requires_superadmin
def superadmin_delete_user(user_id):
    """Delete a user"""
    try:
        conn = db.get_connection()
        conn.execute('DELETE FROM users WHERE id=?', (user_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Utilisateur supprimé'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/superadmin/api/users/<int:user_id>/reset-password', methods=['POST'])
@requires_superadmin
def superadmin_reset_user_password(user_id):
    """Reset a user's password from SuperAdmin"""
    try:
        data = request.json
        new_password = data.get('password', '')

        if not new_password:
            return jsonify({'error': 'Le mot de passe est requis'}), 400

        if len(new_password) < 8:
            return jsonify({'error': 'Le mot de passe doit contenir au moins 8 caractères'}), 400

        # Update the user's password
        db.update_user_password(user_id, hash_password(new_password), new_password)

        return jsonify({'success': True, 'message': 'Mot de passe réinitialisé avec succès'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/superadmin/api/properties/<int:prop_id>', methods=['DELETE'])
@requires_superadmin
def superadmin_delete_property(prop_id):
    """Delete a property and all associated data"""
    try:
        conn = db.get_connection()
        # Delete associated data
        conn.execute('DELETE FROM general_info WHERE property_id=?', (prop_id,))
        conn.execute('DELETE FROM wifi_config WHERE property_id=?', (prop_id,))
        conn.execute('DELETE FROM address WHERE property_id=?', (prop_id,))
        conn.execute('DELETE FROM parking_info WHERE property_id=?', (prop_id,))
        conn.execute('DELETE FROM access_info WHERE property_id=?', (prop_id,))
        conn.execute('DELETE FROM contact_info WHERE property_id=?', (prop_id,))
        conn.execute('DELETE FROM activities WHERE property_id=?', (prop_id,))
        conn.execute('DELETE FROM nearby_services WHERE property_id=?', (prop_id,))
        conn.execute('DELETE FROM emergency_numbers WHERE property_id=?', (prop_id,))
        # Delete property
        conn.execute('DELETE FROM properties WHERE id=?', (prop_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Propriété supprimée'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/superadmin/api/properties/<int:prop_id>/toggle', methods=['POST'])
@requires_superadmin
def superadmin_toggle_property(prop_id):
    """Toggle property active status"""
    try:
        conn = db.get_connection()
        conn.execute('UPDATE properties SET is_active = NOT is_active WHERE id=?', (prop_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Statut modifié'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/superadmin/api/properties/<int:prop_id>/owner', methods=['POST'])
@requires_superadmin
def superadmin_change_property_owner(prop_id):
    """Change property owner"""
    try:
        data = request.json
        user_email = data.get('email', '').lower().strip()

        if not user_email:
            return jsonify({'error': 'Email du propriétaire requis'}), 400

        # Find user by email
        user = db.get_user_by_email(user_email)
        if not user:
            return jsonify({'error': f'Utilisateur {user_email} non trouvé'}), 404

        conn = db.get_connection()
        conn.execute('UPDATE properties SET user_id = ? WHERE id = ?', (user['id'], prop_id))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': f'Propriété assignée à {user_email}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/superadmin/api/sessions', methods=['GET'])
@requires_superadmin
def superadmin_get_sessions():
    """Get all active user sessions"""
    try:
        active_sessions = get_active_sessions()
        return jsonify({
            'success': True,
            'sessions': active_sessions,
            'count': len(active_sessions)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/superadmin/api/sessions/<token_preview>', methods=['DELETE'])
@requires_superadmin
def superadmin_disconnect_session(token_preview):
    """Disconnect a user session by token preview"""
    try:
        # Find and remove the session matching the token preview
        token_to_remove = None
        for token in sessions_db:
            if token.startswith(token_preview.replace('...', '')):
                token_to_remove = token
                break

        if token_to_remove:
            del sessions_db[token_to_remove]
            return jsonify({'success': True, 'message': 'Session déconnectée'})
        else:
            return jsonify({'error': 'Session non trouvée'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/superadmin/api/sql', methods=['POST'])
@requires_superadmin
def superadmin_execute_sql():
    """Execute read-only SQL query"""
    try:
        data = request.json
        query = data.get('query', '').strip()

        # Security: Only allow SELECT queries
        if not query.upper().startswith('SELECT'):
            return jsonify({'error': 'Seules les requêtes SELECT sont autorisées'}), 400

        # Block dangerous keywords
        dangerous = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE']
        query_upper = query.upper()
        for keyword in dangerous:
            if keyword in query_upper:
                return jsonify({'error': f'Mot-clé interdit: {keyword}'}), 400

        conn = db.get_connection()
        results = [dict(row) for row in conn.execute(query).fetchall()]
        conn.close()

        return jsonify({'success': True, 'data': results, 'count': len(results)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/superadmin/api/env-config', methods=['GET'])
@requires_superadmin
def superadmin_get_env_config():
    """Get environment configuration from .env-weblocapp"""
    try:
        env_file = os.path.join(os.path.dirname(__file__), '.env-weblocapp')
        config = {}

        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()

        return jsonify(config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/superadmin/api/env-config', methods=['PUT'])
@requires_superadmin
def superadmin_update_env_config():
    """Update environment configuration in .env-weblocapp"""
    try:
        data = request.json
        env_file = os.path.join(os.path.dirname(__file__), '.env-weblocapp')

        # Build the new content
        content = """# LocAPP Environment Variables
# This file is loaded by the application

# Flask Secret Key (generated secure random string)
SECRET_KEY={SECRET_KEY}

# Google OAuth Credentials
# Get these from Google Cloud Console: https://console.cloud.google.com/
# 1. Create a new project or select existing
# 2. Go to APIs & Services > Credentials
# 3. Create OAuth 2.0 Client ID (Web application)
# 4. Add authorized redirect URI: http://localhost:5001/api/auth/google/callback
GOOGLE_CLIENT_ID={GOOGLE_CLIENT_ID}
GOOGLE_CLIENT_SECRET={GOOGLE_CLIENT_SECRET}

# Google Maps API Key (for Maps and Places Autocomplete)
# Get from Google Cloud Console > APIs & Services > Credentials
# Enable: Maps JavaScript API, Places API
GOOGLE_MAPS_API_KEY={GOOGLE_MAPS_API_KEY}

# Email Configuration (for password reset and notifications)
# For Gmail: You MUST use an App Password, not your regular password
# 1. Go to https://myaccount.google.com/security
# 2. Enable 2-Step Verification (if not already)
# 3. Go to App Passwords (under 2-Step Verification)
# 4. Generate a new app password for "Mail" / "Other (LocApp)"
# 5. Copy the 16-character password here (without spaces)
SMTP_SERVER={SMTP_SERVER}
SMTP_PORT={SMTP_PORT}
SENDER_EMAIL={SENDER_EMAIL}
SENDER_PASSWORD={SENDER_PASSWORD}
NOTIFICATION_EMAIL={NOTIFICATION_EMAIL}
""".format(**data)

        with open(env_file, 'w') as f:
            f.write(content)

        # Reload environment variables
        for key, value in data.items():
            os.environ[key] = value

        return jsonify({'success': True, 'message': 'Configuration sauvegardée'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
