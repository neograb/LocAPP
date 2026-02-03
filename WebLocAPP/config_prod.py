# Configuration Production
# Port: 5001

import os

class ProductionConfig:
    # Server
    HOST = '0.0.0.0'
    PORT = 5001
    DEBUG = False

    # Database
    DATABASE_NAME = 'locapp.db'

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'locapp-prod-7f8k9m2n4p6q1r3s5t8v0w2x4y6z8a1b3c5d')

    # Session
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # OAuth - Production URLs
    GOOGLE_REDIRECT_URI = 'http://localhost:5001/api/auth/google/callback'

    # Logging
    LOG_LEVEL = 'WARNING'

config = ProductionConfig()
