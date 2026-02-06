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
import time
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

# OpenAI API Configuration (for AI property generation)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')

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
    'smtp_server': os.environ.get('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.environ.get('SMTP_PORT', 587)),
    'sender_email': os.environ.get('SENDER_EMAIL', 'myskyidentity@gmail.com'),
    'sender_password': os.environ.get('SENDER_PASSWORD', ''),
    'notification_email': os.environ.get('NOTIFICATION_EMAIL', 'abonard@gmail.com')
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

def login_required(f):
    """Decorator to require login for admin routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        if not current_user:
            return redirect(url_for('login') + '?error=session_expired')
        return f(*args, **kwargs)
    return decorated_function

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
        subject = "Nouveau compte sur LocAPP"
        body = f"Mr {user.lastname} {user.firstname} vient de créer un compte sur LocAPP."

        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = EMAIL_CONFIG['notification_email']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send email via SMTP
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            server.send_message(msg)

        print(f"[EMAIL NOTIFICATION] Email envoyé à {EMAIL_CONFIG['notification_email']}")
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
    """Get property_id from query parameter, header, or default to 1 (Mazet BSA)"""
    # First check query parameters
    property_id = request.args.get('property_id', type=int)
    if property_id:
        return property_id

    # Then check X-Property-ID header (used by AI regeneration endpoints)
    header_id = request.headers.get('X-Property-ID')
    if header_id:
        try:
            return int(header_id)
        except (ValueError, TypeError):
            pass

    # Default fallback
    return 1

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

    # Validation - tous les champs requis
    if not email or not password or not firstname or not lastname:
        return jsonify({'error': 'Tous les champs sont requis'}), 400

    # Validation - format email
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return jsonify({'error': 'Le format de l\'adresse email est invalide', 'field': 'email'}), 400

    # Validation - longueur nom et prénom (minimum 2 caractères)
    if len(firstname) < 2:
        return jsonify({'error': 'Le prénom doit contenir au moins 2 caractères', 'field': 'firstname'}), 400

    if len(lastname) < 2:
        return jsonify({'error': 'Le nom doit contenir au moins 2 caractères', 'field': 'lastname'}), 400

    # Validation - longueur mot de passe
    if len(password) < 8:
        return jsonify({'error': 'Le mot de passe doit contenir au moins 8 caractères', 'field': 'password'}), 400

    # Check if user already exists in database
    existing_user = db.get_user_by_email(email)
    if existing_user:
        return jsonify({'error': 'Un compte existe déjà avec cette adresse email', 'field': 'email', 'code': 'EMAIL_EXISTS'}), 400

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

    # Store action (login or register) in session
    action = request.args.get('action', 'login')
    session['google_oauth_action'] = action

    # Generate redirect URI
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/api/auth/google/callback')
def google_callback():
    """Google OAuth callback - handle the response from Google"""
    if not google:
        return redirect(url_for('login'))

    try:
        # Get the action from session (login or register)
        action = session.pop('google_oauth_action', 'login')

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
            # No existing account
            if action == 'login':
                # Trying to login but account doesn't exist
                return redirect(url_for('login') + '?error=account_not_found')

            # Register - create new user
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
            # User exists
            existing_google_id = user_data.get('google_id')

            # If trying to REGISTER but account already exists
            if action == 'register':
                return redirect(url_for('login') + '?error=account_exists')

            # Login - allow login and update google_id if needed
            if not existing_google_id and google_id:
                db.update_user_google_id(user_data['id'], google_id)

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
        if EMAIL_CONFIG['sender_password']:
            with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
                server.starttls()
                server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
                server.send_message(msg)
                print(f"[PASSWORD RESET EMAIL] Email sent successfully to {user_data['email']}")
        else:
            print(f"[PASSWORD RESET EMAIL] SMTP not configured, email not sent")

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
@login_required
def admin_home():
    """Admin dashboard"""
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    return render_template('index.html', properties=properties, current_user=current_user)

@app.route('/property/new')
@login_required
def new_property_page():
    """Page to create a new property"""
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    return render_template('property_new.html', properties=properties, current_user=current_user, config=app.config)

@app.route('/general')
@login_required
def general_page():
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    subscription = db.get_user_subscription(current_user.id) if current_user else None
    has_ai_access = subscription and subscription.get('plan') != 'decouverte'
    return render_template('general.html', properties=properties, current_user=current_user, has_ai_access=has_ai_access)

@app.route('/wifi')
@login_required
def wifi_page():
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    return render_template('wifi.html', properties=properties, current_user=current_user)

@app.route('/address')
@login_required
def address_page():
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    subscription = db.get_user_subscription(current_user.id) if current_user else None
    has_ai_access = subscription and subscription.get('plan') != 'decouverte'
    return render_template('address.html', properties=properties, current_user=current_user, has_ai_access=has_ai_access)

@app.route('/parking')
@login_required
def parking_page():
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    subscription = db.get_user_subscription(current_user.id) if current_user else None
    has_ai_access = subscription and subscription.get('plan') != 'decouverte'
    return render_template('parking.html', properties=properties, current_user=current_user, has_ai_access=has_ai_access)

@app.route('/access')
@login_required
def access_page():
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    return render_template('access.html', properties=properties, current_user=current_user)

@app.route('/contact')
@login_required
def contact_page():
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    return render_template('contact.html', properties=properties, current_user=current_user)

@app.route('/activities')
@login_required
def activities_page():
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    subscription = db.get_user_subscription(current_user.id) if current_user else None
    has_ai_access = subscription and subscription.get('plan') != 'decouverte'
    return render_template('activities.html', properties=properties, current_user=current_user, has_ai_access=has_ai_access)

@app.route('/services')
@login_required
def services_page():
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    subscription = db.get_user_subscription(current_user.id) if current_user else None
    has_ai_access = subscription and subscription.get('plan') != 'decouverte'
    return render_template('services.html', properties=properties, current_user=current_user, has_ai_access=has_ai_access)

@app.route('/emergency')
@login_required
def emergency_page():
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    return render_template('emergency.html', properties=properties, current_user=current_user)

@app.route('/photos')
@login_required
def photos_page():
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    return render_template('photos.html', properties=properties, current_user=current_user)

@app.route('/account')
@login_required
def account_page():
    """Account management page"""
    current_user = get_current_user()
    properties = get_user_properties(current_user)
    return render_template('account.html', properties=properties, current_user=current_user)

@app.route('/equipements')
@login_required
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

    # Check property limit based on subscription
    if not db.can_add_property(current_user.id):
        subscription = db.get_user_subscription(current_user.id)
        max_props = subscription.get('max_properties', 1) if subscription else 1
        return jsonify({
            'error': f'Vous avez atteint la limite de {max_props} propriété(s) pour votre abonnement. Passez à un plan supérieur pour créer plus de propriétés.'
        }), 403

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

@app.route('/api/properties/generate-ai', methods=['POST'])
def generate_property_with_ai():
    """Generate property content using AI based on address"""
    from ai_service import AIService

    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Vous devez être connecté'}), 401

    # Check property limit based on subscription
    if not db.can_add_property(current_user.id):
        subscription = db.get_user_subscription(current_user.id)
        max_props = subscription.get('max_properties', 1) if subscription else 1
        return jsonify({
            'error': f'Vous avez atteint la limite de {max_props} propriété(s) pour votre abonnement. Passez à un plan supérieur pour créer plus de propriétés.'
        }), 403

    # Check if OpenAI is configured
    if not os.environ.get('OPENAI_API_KEY'):
        return jsonify({'error': 'La génération IA n\'est pas configurée. Contactez l\'administrateur.'}), 503

    data = request.json
    property_name = data.get('name', '').strip()
    address = data.get('address', '').strip()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    display_name = data.get('display_name', '').strip()
    region = data.get('region', '').strip()

    if not property_name:
        return jsonify({'error': 'Le nom de la propriété est requis'}), 400

    if not address or not latitude or not longitude:
        return jsonify({'error': 'L\'adresse et les coordonnées sont requises'}), 400

    try:
        ai_service = AIService()

        # Extract city from address
        address_parts = address.split(',')
        city = ''
        for part in address_parts:
            part = part.strip()
            # Skip parts that are mainly numbers (postal codes, street numbers)
            if part and not part[0].isdigit():
                city = part
                break
        if not city:
            city = region

        print(f"[AI Generate] Starting generation for: {address}")
        print(f"[AI Generate] City: {city}, Region: {region}")

        # 1. Generate property description
        print("[AI Generate] Generating property description...")
        description = ai_service.generate_property_description(address, city, region)
        print(f"[AI Generate] Description generated: {description[:50]}...")

        # 2. Find nearby services (Pharmacy, Supermarket, Bakery)
        print("[AI Generate] Finding nearby services...")
        service_types = [
            ('pharmacy', 'Pharmacie', '💊'),
            ('supermarket', 'Supermarché', '🛒'),
            ('bakery', 'Boulangerie', '🥖')
        ]
        services = ai_service.find_nearby_places(
            float(latitude),
            float(longitude),
            service_types
        )
        print(f"[AI Generate] Found {len(services)} services")

        # 3. Find nearest parking
        print("[AI Generate] Finding nearest parking...")
        parking_info = ai_service.find_nearest_parking(
            float(latitude),
            float(longitude),
            city,
            region
        )
        if parking_info:
            print(f"[AI Generate] Parking found: {parking_info.get('distance')}")

        # 4. Generate activities based on the property address
        print("[AI Generate] Generating activities...")
        full_address = display_name or address
        activities_data = ai_service.generate_activities(full_address, city, region, float(latitude), float(longitude))
        print(f"[AI Generate] Activities generated")

        # 5. Generate welcome message
        print("[AI Generate] Generating welcome message...")
        welcome_data = ai_service.generate_welcome_message(property_name, full_address, city, region)
        print(f"[AI Generate] Welcome message generated")

        # 6. Generate slug from user-provided name
        slug = re.sub(r'[^a-z0-9]+', '-', property_name.lower()).strip('-')

        # Ensure slug is unique
        existing = db.get_property_by_slug(slug)
        if existing:
            import time
            slug = f"{slug}-{int(time.time())}"

        # 6. Create property in database
        print("[AI Generate] Creating property in database...")
        template_id = db.get_template_property_id()

        if template_id:
            property_id = db.duplicate_property_from_template(
                template_property_id=template_id,
                new_property_data={
                    'name': property_name,
                    'slug': slug,
                    'icon': '🏠',
                    'address': display_name or address,
                    'latitude': latitude,
                    'longitude': longitude,
                    'region': region
                },
                user_id=current_user.id
            )
        else:
            property_id = db.create_property({
                'name': property_name,
                'slug': slug,
                'icon': '🏠',
                'address': display_name or address,
                'latitude': latitude,
                'longitude': longitude,
                'region': region
            }, user_id=current_user.id)

        # 8. Update address description with AI-generated content
        print("[AI Generate] Updating address description...")
        db.update_address_description(property_id, description)

        # 9. Update welcome message with AI-generated content
        print("[AI Generate] Updating welcome message...")
        db.update_general_info(property_id, {
            'property_name': property_name,
            'welcome_title': welcome_data.get('welcome_title', f"Bienvenue à {property_name} !"),
            'welcome_message': welcome_data.get('welcome_message', ''),
            'welcome_description': welcome_data.get('welcome_description', '')
        })

        # 11. Delete template services and add AI-generated ones
        print("[AI Generate] Removing template services...")
        db.delete_all_nearby_services(property_id)

        print("[AI Generate] Adding AI-generated services...")
        for service in services:
            db.create_nearby_service(property_id, service)

        # 12. Update parking info
        if parking_info:
            print("[AI Generate] Updating parking info...")
            db.update_parking_info(property_id, parking_info)

        # 13. Delete template activities and create AI-generated ones
        print("[AI Generate] Removing template activities...")
        db.delete_all_activities(property_id)

        print("[AI Generate] Creating AI-generated activities...")
        activities_created = 0

        # Category mapping: key in activities_data -> (category_name, icon)
        category_mapping = {
            'incontournables': ('Incontournables', '⭐'),
            'sports': ('Sport', '🏃'),
            'restaurants': ('Restaurant', '🍽️'),
            'visites': ('Visite', '🗺️')
        }

        for key, (cat_name, cat_icon) in category_mapping.items():
            if key in activities_data and activities_data[key]:
                # Create category
                category_id = db.create_activity_category(property_id, {
                    'name': cat_name,
                    'icon': cat_icon
                })
                print(f"[AI Generate] Created category: {cat_name}")

                # Create activities for this category
                for idx, activity in enumerate(activities_data[key]):
                    db.create_activity(property_id, {
                        'name': activity.get('name', 'Sans nom'),
                        'category': cat_name,
                        'description': activity.get('description', ''),
                        'emoji': activity.get('emoji', '📍'),
                        'distance': '',
                        'display_order': idx
                    })
                    activities_created += 1

        print(f"[AI Generate] Created {activities_created} activities")

        print(f"[AI Generate] Property created successfully with ID: {property_id}")

        return jsonify({
            'success': True,
            'id': property_id,
            'slug': slug,
            'message': 'Propriété générée avec succès par l\'IA',
            'generated': {
                'description': description,
                'services_count': len(services),
                'has_parking': parking_info is not None,
                'activities_count': activities_created
            }
        })

    except ValueError as e:
        print(f"[AI Generate] Value error: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"[AI Generate] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Erreur lors de la génération IA. Veuillez réessayer.'}), 500

# ==================== AI Regeneration Endpoints ====================

def check_ai_access(current_user):
    """Check if user has AI access (paid plan)"""
    if not current_user:
        return False
    subscription = db.get_user_subscription(current_user.id)
    return subscription and subscription.get('plan') != 'decouverte'

def get_property_address_info(property_id):
    """Get address info for a property"""
    address_data = db.get_address(property_id)
    if not address_data:
        return None, None, None, None, None

    city = address_data.get('city', '')
    street = address_data.get('street', '')
    postal_code = address_data.get('postal_code', '')
    full_address = f"{street}, {postal_code} {city}".strip(', ')
    latitude = address_data.get('latitude')
    longitude = address_data.get('longitude')

    # Get region from property
    conn = db.get_connection()
    prop = conn.execute('SELECT region FROM properties WHERE id=?', (property_id,)).fetchone()
    conn.close()
    region = prop['region'] if prop else ''

    return full_address, city, region, latitude, longitude

@app.route('/api/ai/regenerate/general', methods=['POST'])
@requires_auth
def ai_regenerate_general():
    """Regenerate welcome message with AI"""
    from ai_service import AIService

    current_user = get_current_user()
    if not check_ai_access(current_user):
        return jsonify({'error': 'Fonctionnalité réservée aux abonnés'}), 403

    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Propriété non trouvée'}), 404

    try:
        ai_service = AIService()

        # Get property info
        general_info = db.get_general_info(property_id)
        property_name = general_info.get('property_name', 'Ma propriété')

        full_address, city, region, _, _ = get_property_address_info(property_id)
        if not city:
            city = region or 'France'

        # Generate welcome message
        welcome_data = ai_service.generate_welcome_message(property_name, full_address or '', city, region or '')

        # Update general info
        db.update_general_info(property_id, {
            'property_name': property_name,
            'welcome_title': welcome_data.get('welcome_title', f"Bienvenue à {property_name} !"),
            'welcome_message': welcome_data.get('welcome_message', ''),
            'welcome_description': welcome_data.get('welcome_description', '')
        })

        return jsonify({
            'success': True,
            'data': welcome_data,
            'message': 'Message de bienvenue régénéré avec succès'
        })
    except Exception as e:
        print(f"[AI Regenerate General] Error: {e}")
        return jsonify({'error': 'Erreur lors de la régénération'}), 500

@app.route('/api/ai/regenerate/address', methods=['POST'])
@requires_auth
def ai_regenerate_address():
    """Regenerate address description with AI"""
    from ai_service import AIService

    current_user = get_current_user()
    if not check_ai_access(current_user):
        return jsonify({'error': 'Fonctionnalité réservée aux abonnés'}), 403

    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Propriété non trouvée'}), 404

    try:
        ai_service = AIService()

        full_address, city, region, _, _ = get_property_address_info(property_id)
        if not full_address:
            return jsonify({'error': 'Adresse non configurée'}), 400

        # Generate description
        description = ai_service.generate_property_description(full_address, city, region or '')

        # Update address description
        db.update_address_description(property_id, description)

        return jsonify({
            'success': True,
            'description': description,
            'message': 'Description régénérée avec succès'
        })
    except Exception as e:
        print(f"[AI Regenerate Address] Error: {e}")
        return jsonify({'error': 'Erreur lors de la régénération'}), 500

@app.route('/api/ai/regenerate/activities', methods=['POST'])
@requires_auth
def ai_regenerate_activities():
    """Regenerate activities with AI"""
    from ai_service import AIService

    current_user = get_current_user()
    if not check_ai_access(current_user):
        return jsonify({'error': 'Fonctionnalité réservée aux abonnés'}), 403

    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Propriété non trouvée'}), 404

    try:
        ai_service = AIService()

        full_address, city, region, latitude, longitude = get_property_address_info(property_id)
        if not latitude or not longitude:
            return jsonify({'error': 'Coordonnées GPS non configurées'}), 400

        # Generate activities
        activities_data = ai_service.generate_activities(
            full_address or '', city or '', region or '',
            float(latitude), float(longitude)
        )

        # Delete existing activities and categories
        db.delete_all_activities(property_id)

        # Create new activities
        activities_created = 0
        category_mapping = {
            'incontournables': ('Incontournables', '⭐'),
            'sports': ('Sport', '🏃'),
            'restaurants': ('Restaurant', '🍽️'),
            'visites': ('Visite', '🗺️')
        }

        for key, (cat_name, cat_icon) in category_mapping.items():
            if key in activities_data and activities_data[key]:
                db.create_activity_category(property_id, {'name': cat_name, 'icon': cat_icon})
                for idx, activity in enumerate(activities_data[key]):
                    db.create_activity(property_id, {
                        'name': activity.get('name', 'Sans nom'),
                        'category': cat_name,
                        'description': activity.get('description', ''),
                        'emoji': activity.get('emoji', '📍'),
                        'distance': '',
                        'display_order': idx
                    })
                    activities_created += 1

        return jsonify({
            'success': True,
            'activities_count': activities_created,
            'message': f'{activities_created} activités régénérées avec succès'
        })
    except Exception as e:
        print(f"[AI Regenerate Activities] Error: {e}")
        return jsonify({'error': 'Erreur lors de la régénération'}), 500

@app.route('/api/ai/regenerate/services', methods=['POST'])
@requires_auth
def ai_regenerate_services():
    """Regenerate nearby services with AI"""
    from ai_service import AIService

    current_user = get_current_user()
    if not check_ai_access(current_user):
        return jsonify({'error': 'Fonctionnalité réservée aux abonnés'}), 403

    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Propriété non trouvée'}), 404

    try:
        ai_service = AIService()

        _, _, _, latitude, longitude = get_property_address_info(property_id)
        if not latitude or not longitude:
            return jsonify({'error': 'Coordonnées GPS non configurées'}), 400

        # Find nearby services
        service_types = [
            ('pharmacy', 'Pharmacie', '💊'),
            ('supermarket', 'Supermarché', '🛒'),
            ('bakery', 'Boulangerie', '🥖')
        ]
        services = ai_service.find_nearby_places(float(latitude), float(longitude), service_types)

        # Delete existing services and add new ones
        db.delete_all_nearby_services(property_id)
        for service in services:
            db.create_nearby_service(property_id, service)

        return jsonify({
            'success': True,
            'services_count': len(services),
            'message': f'{len(services)} services régénérés avec succès'
        })
    except Exception as e:
        print(f"[AI Regenerate Services] Error: {e}")
        return jsonify({'error': 'Erreur lors de la régénération'}), 500

@app.route('/api/ai/regenerate/parking', methods=['POST'])
@requires_auth
def ai_regenerate_parking():
    """Regenerate parking info with AI"""
    from ai_service import AIService

    current_user = get_current_user()
    if not check_ai_access(current_user):
        return jsonify({'error': 'Fonctionnalité réservée aux abonnés'}), 403

    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Propriété non trouvée'}), 404

    try:
        ai_service = AIService()

        full_address, city, region, latitude, longitude = get_property_address_info(property_id)
        if not latitude or not longitude:
            return jsonify({'error': 'Coordonnées GPS non configurées'}), 400

        # Find nearest parking
        parking_info = ai_service.find_nearest_parking(
            float(latitude), float(longitude),
            city or '', region or ''
        )

        if parking_info:
            db.update_parking_info(property_id, parking_info)
            return jsonify({
                'success': True,
                'parking': parking_info,
                'message': 'Informations parking régénérées avec succès'
            })
        else:
            return jsonify({'error': 'Aucun parking trouvé à proximité'}), 404
    except Exception as e:
        print(f"[AI Regenerate Parking] Error: {e}")
        return jsonify({'error': 'Erreur lors de la régénération'}), 500

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
    activity_id = db.create_activity(property_id, data)
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
    property_id = get_property_id()
    data = db.get_all_activity_categories(property_id)
    return jsonify(data)

@app.route('/api/activity-categories', methods=['POST'])
@requires_auth
def create_activity_category():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Accès non autorisé à cette propriété'}), 403
    data = request.json
    category_id = db.create_activity_category(property_id, data)
    return jsonify({'success': True, 'id': category_id, 'message': 'Catégorie créée'})

@app.route('/api/activity-categories/<int:category_id>', methods=['PUT'])
@requires_auth
def update_activity_category(category_id):
    data = request.json
    db.update_activity_category(category_id, data)
    return jsonify({'success': True, 'message': 'Catégorie mise à jour'})

@app.route('/api/activity-categories/<int:category_id>', methods=['DELETE'])
@requires_auth
def delete_activity_category(category_id):
    db.delete_activity_category(category_id)
    return jsonify({'success': True, 'message': 'Catégorie supprimée'})

@app.route('/api/activity-categories/reorder', methods=['POST'])
@requires_auth
def reorder_activity_categories():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Accès non autorisé à cette propriété'}), 403
    data = request.json
    db.reorder_activity_categories(property_id, data.get('category_ids', []))
    return jsonify({'success': True, 'message': 'Ordre mis à jour'})

@app.route('/api/activities/reorder', methods=['POST'])
@requires_auth
def reorder_activities():
    data = request.json
    db.reorder_activities(data.get('category'), data.get('activity_ids', []))
    return jsonify({'success': True, 'message': 'Ordre mis à jour'})

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
# Access Photos API
# ============================================

@app.route('/api/access-photos', methods=['GET'])
def get_access_photos():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify([])
    data = db.get_all_access_photos(property_id)
    return jsonify(data)

@app.route('/api/access-photos', methods=['POST'])
@requires_auth
def upload_access_photo():
    property_id = get_verified_property_id()
    if not property_id:
        return jsonify({'error': 'Accès non autorisé à cette propriété'}), 403

    # Check photo limit
    max_photos = int(db.get_app_config('max_photos_access') or 3)
    current_count = db.count_access_photos(property_id)
    if current_count >= max_photos:
        return jsonify({'error': f'Limite atteinte: maximum {max_photos} photos autorisées'}), 400

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
    unique_filename = f"access_{property_id}_{uuid.uuid4().hex}.{ext}"

    # Create access photos subfolder
    access_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'access', str(property_id))
    os.makedirs(access_folder, exist_ok=True)

    # Save file
    filepath = os.path.join(access_folder, unique_filename)
    file.save(filepath)

    # Get optional metadata
    title = request.form.get('title', '')
    description = request.form.get('description', '')

    # Save to database
    photo_id = db.create_access_photo({
        'filename': f"access/{property_id}/{unique_filename}",
        'original_name': original_name,
        'title': title,
        'description': description
    }, property_id)

    return jsonify({
        'success': True,
        'id': photo_id,
        'filename': f"access/{property_id}/{unique_filename}",
        'message': 'Photo uploadée avec succès'
    })

@app.route('/api/access-photos/<int:photo_id>', methods=['PUT'])
@requires_auth
def update_access_photo(photo_id):
    photo = db.get_access_photo(photo_id)
    if not photo:
        return jsonify({'error': 'Photo non trouvée'}), 404

    property_id = get_verified_property_id()
    if not property_id or photo['property_id'] != property_id:
        return jsonify({'error': 'Accès non autorisé'}), 403

    data = request.json
    db.update_access_photo(photo_id, data)
    return jsonify({'success': True, 'message': 'Photo mise à jour'})

@app.route('/api/access-photos/<int:photo_id>', methods=['DELETE'])
@requires_auth
def delete_access_photo(photo_id):
    photo = db.get_access_photo(photo_id)
    if not photo:
        return jsonify({'error': 'Photo non trouvée'}), 404

    property_id = get_verified_property_id()
    if not property_id or photo['property_id'] != property_id:
        return jsonify({'error': 'Accès non autorisé'}), 403

    # Delete file from disk
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], photo['filename'])
    if os.path.exists(filepath):
        os.remove(filepath)

    db.delete_access_photo(photo_id)
    return jsonify({'success': True, 'message': 'Photo supprimée'})

@app.route('/api/access-photos/limit', methods=['GET'])
def get_access_photos_limit():
    """Get the current photo limit and count for access page"""
    property_id = get_verified_property_id()
    max_photos = int(db.get_app_config('max_photos_access') or 3)
    current_count = db.count_access_photos(property_id) if property_id else 0
    return jsonify({
        'max': max_photos,
        'current': current_count,
        'remaining': max_photos - current_count
    })

# ============================================
# Account & Subscription API Routes
# ============================================

@app.route('/api/account', methods=['GET'])
@requires_auth
def get_account_info():
    """Get account information for logged in user"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401

    account_info = db.get_account_info(current_user.id)
    if account_info:
        return jsonify(account_info)
    return jsonify({'error': 'Compte non trouvé'}), 404

@app.route('/api/account', methods=['DELETE'])
@requires_auth
def delete_account():
    """Delete user account and all associated data"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401

    try:
        # Delete all user properties and their data
        properties = db.get_all_user_properties(current_user.id)
        for prop in properties:
            db.delete_property_with_data(prop['id'])

        # Delete user avatar if exists
        account_info = db.get_account_info(current_user.id)
        if account_info and account_info.get('avatar'):
            avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], account_info['avatar'])
            if os.path.exists(avatar_path):
                os.remove(avatar_path)

        # Delete user account
        db.delete_user(current_user.id)

        return jsonify({'message': 'Compte supprimé avec succès'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/account/avatar', methods=['POST'])
@requires_auth
def upload_account_avatar():
    """Upload avatar for user account"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401

    if 'avatar' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400

    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400

    if file and allowed_file(file.filename):
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"user_avatar_{current_user.id}_{int(time.time())}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Delete old avatar if exists
        account_info = db.get_account_info(current_user.id)
        if account_info and account_info.get('avatar'):
            old_path = os.path.join(app.config['UPLOAD_FOLDER'], account_info['avatar'])
            if os.path.exists(old_path):
                os.remove(old_path)

        file.save(filepath)

        # Update database
        db.update_user_avatar(current_user.id, filename)

        return jsonify({'success': True, 'avatar': filename})

    return jsonify({'error': 'Type de fichier non autorisé'}), 400

@app.route('/api/account/avatar', methods=['DELETE'])
@requires_auth
def delete_account_avatar():
    """Delete avatar for user account"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401

    account_info = db.get_account_info(current_user.id)
    if account_info and account_info.get('avatar'):
        avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], account_info['avatar'])
        if os.path.exists(avatar_path):
            os.remove(avatar_path)

        db.update_user_avatar(current_user.id, None)
        return jsonify({'success': True, 'message': 'Avatar supprimé'})

    return jsonify({'error': 'Aucun avatar à supprimer'}), 404

@app.route('/api/subscription', methods=['GET'])
@requires_auth
def get_subscription():
    """Get subscription for logged in user"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401

    subscription = db.get_user_subscription(current_user.id)
    if subscription:
        # Calculate duration
        if subscription['activated_at']:
            from datetime import datetime
            try:
                activated = datetime.fromisoformat(subscription['activated_at'].replace('Z', '+00:00'))
                now = datetime.now()
                duration_days = (now - activated.replace(tzinfo=None)).days
                if duration_days < 30:
                    subscription['duration'] = f"{duration_days} jours"
                elif duration_days < 365:
                    months = duration_days // 30
                    subscription['duration'] = f"{months} mois"
                else:
                    years = duration_days // 365
                    subscription['duration'] = f"{years} an{'s' if years > 1 else ''}"
            except Exception:
                subscription['duration'] = '-'
        return jsonify(subscription)
    return jsonify({'error': 'Abonnement non trouvé'}), 404

@app.route('/api/subscription', methods=['PUT'])
@requires_auth
def update_subscription():
    """Update subscription plan"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401

    data = request.json
    plan = data.get('plan')

    if not plan:
        return jsonify({'error': 'Plan requis'}), 400

    if db.update_subscription(current_user.id, plan):
        return jsonify({'message': 'Abonnement mis à jour avec succès'})
    return jsonify({'error': 'Plan invalide'}), 400

@app.route('/api/subscription/can-create-property', methods=['GET'])
@requires_auth
def can_create_property():
    """Check if user can create more properties based on subscription"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401

    can_create = db.can_add_property(current_user.id)
    subscription = db.get_user_subscription(current_user.id)
    current_count = db.count_user_properties(current_user.id)
    max_props = subscription.get('max_properties', 1) if subscription else 1

    return jsonify({
        'can_create': can_create,
        'current_count': current_count,
        'max_properties': max_props,
        'plan': subscription.get('plan', 'decouverte') if subscription else 'decouverte'
    })

@app.route('/api/account/properties', methods=['GET'])
@requires_auth
def get_account_properties():
    """Get all properties for logged in user (including inactive)"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401

    properties = db.get_all_user_properties(current_user.id)
    return jsonify(properties)

@app.route('/api/account/properties/<int:property_id>/toggle', methods=['PUT'])
@requires_auth
def toggle_property(property_id):
    """Toggle property active status"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401

    # Verify ownership
    prop = db.get_property(property_id)
    if not prop or prop.get('user_id') != current_user.id:
        return jsonify({'error': 'Propriété non trouvée ou non autorisée'}), 404

    data = request.json
    is_active = data.get('is_active', True)

    db.toggle_property_active(property_id, is_active)
    status = 'activée' if is_active else 'désactivée'
    return jsonify({'message': f'Propriété {status} avec succès'})

@app.route('/api/account/properties/<int:property_id>', methods=['DELETE'])
@requires_auth
def delete_property(property_id):
    """Delete a property and all associated data"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401

    # Verify ownership
    prop = db.get_property(property_id)
    if not prop or prop.get('user_id') != current_user.id:
        return jsonify({'error': 'Propriété non trouvée ou non autorisée'}), 404

    db.delete_property_with_data(property_id)
    return jsonify({'message': 'Propriété supprimée avec succès'})

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

# OpenAI API Configuration (for AI property generation)
# Get your API key from: https://platform.openai.com/api-keys
# Models: gpt-4o-mini (fast & cheap), gpt-4o (powerful), gpt-4-turbo (large context)
OPENAI_API_KEY={OPENAI_API_KEY}
OPENAI_MODEL={OPENAI_MODEL}

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

@app.route('/superadmin/api/test-openai', methods=['POST'])
@requires_superadmin
def superadmin_test_openai():
    """Test OpenAI API connection"""
    api_key = os.environ.get('OPENAI_API_KEY', '')
    if not api_key:
        return jsonify({'error': 'Clé API OpenAI non configurée'}), 400

    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=os.environ.get('OPENAI_MODEL', 'gpt-4o-mini'),
            messages=[{"role": "user", "content": "Say 'OK'"}],
            max_tokens=10
        )
        return jsonify({'success': True, 'message': 'Connexion réussie'})
    except ImportError:
        return jsonify({'error': 'Module openai non installé. Exécutez: pip install openai'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/superadmin/api/app-config', methods=['GET'])
@requires_superadmin
def superadmin_get_app_config():
    """Get all app configuration"""
    config = db.get_all_app_config()
    return jsonify(config)

@app.route('/superadmin/api/app-config', methods=['PUT'])
@requires_superadmin
def superadmin_update_app_config():
    """Update app configuration"""
    data = request.json
    for key, value in data.items():
        db.set_app_config(key, str(value))
    return jsonify({'success': True, 'message': 'Configuration mise à jour'})

# ============================================
# Guest Preview Routes (Public)
# ============================================

@app.route('/g/<int:property_id>')
def guest_preview(property_id):
    """Public guest preview - Mobile app simulation"""
    # Get property info
    property_info = db.get_property(property_id)
    if not property_info:
        return "Propriété non trouvée", 404

    # Check if property is active
    if not property_info.get('is_active', True):
        return "Cette propriété n'est pas disponible", 404

    # Gather all property data
    property_data = {
        'property': property_info,
        'general': db.get_general_info(property_id) or {},
        'wifi': db.get_wifi_config(property_id) or {},
        'address': db.get_address(property_id) or {},
        'parking': db.get_parking_info(property_id) or {},
        'access': db.get_access_info(property_id) or {},
        'contact': db.get_contact_info(property_id) or {},
        'activities': db.get_all_activities(property_id) or [],
        'services': db.get_all_nearby_services(property_id) or [],
        'amenities': db.get_available_amenities(property_id) or [],
        'photos': db.get_all_photos(property_id) or [],
        'access_photos': db.get_all_access_photos(property_id) or [],
        'emergency_numbers': db.get_all_emergency_numbers(property_id) or []
    }

    return render_template('guest_preview.html',
        property=property_info,
        general=property_data['general'],
        wifi=property_data['wifi'],
        address=property_data['address'],
        parking=property_data['parking'],
        access=property_data['access'],
        contact=property_data['contact'],
        property_data=property_data
    )

@app.route('/api/guest/<int:property_id>')
def api_guest_data(property_id):
    """API endpoint to get all guest data for a property"""
    # Get property info
    property_info = db.get_property(property_id)
    if not property_info:
        return jsonify({'error': 'Property not found'}), 404

    # Check if property is active
    if not property_info.get('is_active', True):
        return jsonify({'error': 'Property not available'}), 404

    # Gather all property data
    property_data = {
        'property': property_info,
        'general': db.get_general_info(property_id) or {},
        'wifi': db.get_wifi_config(property_id) or {},
        'address': db.get_address(property_id) or {},
        'parking': db.get_parking_info(property_id) or {},
        'access': db.get_access_info(property_id) or {},
        'contact': db.get_contact_info(property_id) or {},
        'activities': db.get_all_activities(property_id) or [],
        'services': db.get_all_nearby_services(property_id) or [],
        'amenities': db.get_available_amenities(property_id) or [],
        'photos': db.get_all_photos(property_id) or [],
        'access_photos': db.get_all_access_photos(property_id) or [],
        'emergency_numbers': db.get_all_emergency_numbers(property_id) or []
    }

    return jsonify(property_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
