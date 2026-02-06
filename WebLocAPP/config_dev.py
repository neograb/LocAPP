# Configuration Developpement
# Port: 5001

import os

class DevelopmentConfig:
    # Server
    HOST = '0.0.0.0'
    PORT = 5001
    DEBUG = True

    # Database
    DATABASE_NAME = 'locapp.db'

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'locapp-dev-secret-key-for-development-only')

    # Session
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # OAuth - Development URLs
    GOOGLE_REDIRECT_URI = 'http://localhost:5001/api/auth/google/callback'

    # Logging
    LOG_LEVEL = 'DEBUG'

    # Development features
    TEMPLATES_AUTO_RELOAD = True

config = DevelopmentConfig()
