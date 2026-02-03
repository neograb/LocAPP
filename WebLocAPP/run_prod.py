#!/usr/bin/env python3
"""
Script de lancement - Mode PRODUCTION
Port: 5001
"""

from app import app
from config_prod import config

if __name__ == '__main__':
    print("=" * 50)
    print("  LocApp - Mode PRODUCTION")
    print(f"  URL: http://localhost:{config.PORT}")
    print("  Debug: OFF")
    print("=" * 50)

    app.run(
        debug=config.DEBUG,
        host=config.HOST,
        port=config.PORT
    )
