#!/usr/bin/env python3
"""
Script de lancement - Mode DEVELOPPEMENT
Port: 6001
"""

from app import app
from config_dev import config

if __name__ == '__main__':
    print("=" * 50)
    print("  LocApp - Mode DEVELOPPEMENT")
    print(f"  URL: http://localhost:{config.PORT}")
    print("  Debug: ON")
    print("=" * 50)

    app.config['TEMPLATES_AUTO_RELOAD'] = config.TEMPLATES_AUTO_RELOAD

    app.run(
        debug=config.DEBUG,
        host=config.HOST,
        port=config.PORT
    )
