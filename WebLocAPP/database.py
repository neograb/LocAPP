import sqlite3
import json
import re
from datetime import datetime

class Database:
    def __init__(self, db_name='locapp.db'):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        # Add timeout=30 to wait up to 30 seconds for database locks to be released
        conn = sqlite3.connect(self.db_name, timeout=30)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize database with all tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Table pour les propriétés (menu principal)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                icon TEXT DEFAULT '🏠',
                location TEXT,
                description TEXT,
                theme TEXT DEFAULT 'mazet-bsa',
                accent_color TEXT DEFAULT '#D4A574',
                is_active BOOLEAN DEFAULT 1,
                display_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Table pour les informations générales
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS general_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                property_name TEXT NOT NULL,
                welcome_title TEXT,
                welcome_message TEXT,
                welcome_description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties(id)
            )
        ''')

        # Table pour WiFi
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wifi_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                ssid TEXT NOT NULL,
                password TEXT NOT NULL,
                location_description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties(id)
            )
        ''')

        # Table pour l'adresse
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS address (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                street TEXT NOT NULL,
                postal_code TEXT NOT NULL,
                city TEXT NOT NULL,
                country TEXT DEFAULT 'France',
                description TEXT,
                latitude REAL,
                longitude REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties(id)
            )
        ''')

        # Table pour le parking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parking_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                distance TEXT,
                description TEXT,
                is_free BOOLEAN DEFAULT 1,
                tips TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties(id)
            )
        ''')

        # Table pour les clés et accès
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                check_in_time TEXT DEFAULT '16:00',
                check_out_time TEXT DEFAULT '10:00',
                keybox_code TEXT,
                keybox_location TEXT,
                access_instructions TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties(id)
            )
        ''')

        # Table pour les contacts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contact_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                host_name TEXT,
                phone TEXT NOT NULL,
                email TEXT,
                whatsapp TEXT,
                airbnb_url TEXT,
                description TEXT,
                response_time TEXT,
                avatar TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties(id)
            )
        ''')

        # Table pour les numéros d'urgence
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emergency_numbers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                number TEXT NOT NULL,
                category TEXT DEFAULT 'emergency',
                display_order INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties(id)
            )
        ''')

        # Table pour les services à proximité
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nearby_services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                icon TEXT,
                address TEXT,
                phone TEXT,
                description TEXT,
                opening_hours TEXT,
                latitude REAL,
                longitude REAL,
                display_order INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties(id)
            )
        ''')

        # Table pour les activités
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                emoji TEXT,
                distance TEXT,
                latitude REAL,
                longitude REAL,
                display_order INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties(id)
            )
        ''')

        # Table pour les catégories d'activités
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                icon TEXT,
                color TEXT,
                display_order INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties(id)
            )
        ''')

        # Table pour les équipements
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS amenities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                name TEXT NOT NULL,
                icon TEXT,
                description TEXT,
                display_order INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties(id)
            )
        ''')

        # Table pour les instructions de départ
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checkout_instructions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                instruction TEXT NOT NULL,
                icon TEXT,
                display_order INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties(id)
            )
        ''')

        # Table pour les utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                password_hash TEXT,
                google_id TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Table pour les tokens de réinitialisation de mot de passe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT NOT NULL UNIQUE,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Table pour les photos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                original_name TEXT NOT NULL,
                title TEXT,
                description TEXT,
                display_order INTEGER DEFAULT 0,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties(id)
            )
        ''')

        # Table pour les photos d'accès
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                original_name TEXT NOT NULL,
                title TEXT,
                description TEXT,
                display_order INTEGER DEFAULT 0,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties(id)
            )
        ''')

        # Table pour la configuration de l'application
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT NOT NULL UNIQUE,
                config_value TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Table pour les abonnements
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                plan TEXT NOT NULL DEFAULT 'decouverte',
                plan_name TEXT DEFAULT 'Découverte',
                price REAL DEFAULT 0,
                max_properties INTEGER DEFAULT 1,
                activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                next_billing TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()

        # Migrer les données existantes et insérer les valeurs par défaut
        self._migrate_and_insert_default_data(cursor, conn)

        # Migrate: add user_id column if it doesn't exist
        self._migrate_add_user_id_to_properties(cursor, conn)

        # Migrate: add avatar column to contact_info if it doesn't exist
        self._migrate_add_avatar_to_contact_info(cursor, conn)

        # Migrate: add region column to properties if it doesn't exist
        self._migrate_add_region_to_properties(cursor, conn)

        # Migrate: add is_available column to amenities if it doesn't exist
        self._migrate_add_is_available_to_amenities(cursor, conn)

        # Migrate: add header_image column to general_info if it doesn't exist
        self._migrate_add_header_image_to_general_info(cursor, conn)

        # Migrate: add password_plain column to users if it doesn't exist
        self._migrate_add_password_plain_to_users(cursor, conn)

        # Migrate: add avatar column to users if it doesn't exist
        self._migrate_add_avatar_to_users(cursor, conn)

        # Migrate: insert default app config values
        self._migrate_insert_default_app_config(cursor, conn)

        conn.close()

    def _migrate_add_user_id_to_properties(self, cursor, conn):
        """Migration: Add user_id column to properties if it doesn't exist"""
        # Check if user_id column exists
        cursor.execute("PRAGMA table_info(properties)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'user_id' not in columns:
            cursor.execute('ALTER TABLE properties ADD COLUMN user_id INTEGER REFERENCES users(id)')
            conn.commit()

        # Create default user abonard@gmail.com if not exists
        cursor.execute("SELECT id FROM users WHERE email = ?", ('abonard@gmail.com',))
        user_row = cursor.fetchone()

        if not user_row:
            # Create the user
            cursor.execute('''
                INSERT INTO users (email, firstname, lastname, password_hash)
                VALUES (?, ?, ?, ?)
            ''', ('abonard@gmail.com', 'Alexandre', 'Bonard', None))
            conn.commit()
            user_id = cursor.lastrowid
        else:
            user_id = user_row[0]

        # Link existing properties (Mazet BSA and Vaujany) to abonard@gmail.com
        # Update properties that don't have a user_id yet
        cursor.execute("UPDATE properties SET user_id = ? WHERE user_id IS NULL", (user_id,))
        conn.commit()

    def _migrate_add_avatar_to_contact_info(self, cursor, conn):
        """Migration: Add avatar column to contact_info if it doesn't exist"""
        cursor.execute("PRAGMA table_info(contact_info)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'avatar' not in columns:
            cursor.execute('ALTER TABLE contact_info ADD COLUMN avatar TEXT')
            conn.commit()

    def _migrate_add_region_to_properties(self, cursor, conn):
        """Migration: Add region column to properties if it doesn't exist"""
        cursor.execute("PRAGMA table_info(properties)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'region' not in columns:
            cursor.execute('ALTER TABLE properties ADD COLUMN region TEXT')
            conn.commit()

    def _migrate_add_is_available_to_amenities(self, cursor, conn):
        """Migration: Add is_available column to amenities if it doesn't exist"""
        cursor.execute("PRAGMA table_info(amenities)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'is_available' not in columns:
            cursor.execute('ALTER TABLE amenities ADD COLUMN is_available BOOLEAN DEFAULT 1')
            conn.commit()

    def _migrate_add_header_image_to_general_info(self, cursor, conn):
        """Migration: Add header_image column to general_info if it doesn't exist"""
        cursor.execute("PRAGMA table_info(general_info)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'header_image' not in columns:
            cursor.execute('ALTER TABLE general_info ADD COLUMN header_image TEXT')
            conn.commit()

    def _migrate_add_password_plain_to_users(self, cursor, conn):
        """Migration: Add password_plain column to users for superadmin visibility"""
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'password_plain' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN password_plain TEXT')
            conn.commit()

    def _migrate_add_avatar_to_users(self, cursor, conn):
        """Migration: Add avatar column to users for account avatar"""
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'avatar' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN avatar TEXT')
            conn.commit()

    def _migrate_insert_default_app_config(self, cursor, conn):
        """Migration: Insert default app configuration values"""
        default_configs = [
            ('max_photos_gallery', '50', 'Nombre maximum de photos dans la galerie'),
            ('max_photos_access', '3', 'Nombre maximum de photos pour la page accès')
        ]

        for key, value, description in default_configs:
            cursor.execute('SELECT id FROM app_config WHERE config_key = ?', (key,))
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO app_config (config_key, config_value, description)
                    VALUES (?, ?, ?)
                ''', (key, value, description))

        conn.commit()

    def _migrate_and_insert_default_data(self, cursor, conn):
        """Migrate existing data and insert default data"""

        # Vérifier si les propriétés existent
        cursor.execute('SELECT COUNT(*) FROM properties')
        if cursor.fetchone()[0] == 0:
            # Créer la propriété Mazet BSA (Thème Orange Provence 🟠)
            cursor.execute('''
                INSERT INTO properties (name, slug, icon, location, description, theme, accent_color, display_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'Mazet BSA',
                'mazet-bsa',
                '🏡',
                'Bourg-Saint-Andéol, Ardèche',
                'Le Mazet de Bourg-Saint-Andéol',
                'mazet-bsa',
                '#D4A574',
                1
            ))
            mazet_id = cursor.lastrowid

            # Créer la propriété Vaujany (Thème Bleu Montagne 🔵)
            cursor.execute('''
                INSERT INTO properties (name, slug, icon, location, description, theme, accent_color, display_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'Vaujany',
                'vaujany',
                '🏔️',
                'Vaujany, Isère',
                'Appartement à Vaujany',
                'vaujany',
                '#5B8FB9',
                2
            ))
            vaujany_id = cursor.lastrowid

            conn.commit()

            # Insérer les données par défaut pour Mazet BSA
            self._insert_mazet_data(cursor, mazet_id)

            # Insérer les données par défaut pour Vaujany
            self._insert_vaujany_data(cursor, vaujany_id)

            conn.commit()

    def _insert_mazet_data(self, cursor, property_id):
        """Insert default data for Mazet BSA"""

        # General Info
        cursor.execute('''
            INSERT INTO general_info (property_id, property_name, welcome_title, welcome_message, welcome_description)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            property_id,
            'Le Mazet de BSA',
            'Bienvenue ! 🌿',
            'Nous sommes ravis de vous accueillir dans notre Mazet.',
            'Ce petit coin de paradis provençal est désormais le vôtre le temps de votre séjour.'
        ))

        # WiFi
        cursor.execute('''
            INSERT INTO wifi_config (property_id, ssid, password, location_description)
            VALUES (?, ?, ?, ?)
        ''', (
            property_id,
            'Roussel_Bonard_07',
            'Solex07700',
            'Le WiFi couvre l\'ensemble du mazet. La box se trouve dans le salon.'
        ))

        # Address
        cursor.execute('''
            INSERT INTO address (property_id, street, postal_code, city, country, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            property_id,
            '1 Chemin de sainte croix',
            '07700',
            'Bourg-Saint-Andéol',
            'France',
            'Le mazet se situe en plein cœur de Bourg-Saint-Andéol, à proximité immédiate des commerces et restaurants.'
        ))

        # Parking
        cursor.execute('''
            INSERT INTO parking_info (property_id, distance, description, is_free, tips)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            property_id,
            '150m',
            'Le parking le plus proche se trouve à environ 150 mètres du mazet. Tous les parkings de Bourg-Saint-Andéol sont gratuits.',
            1,
            'En été et les jours de marché (samedi), les places peuvent être plus difficiles à trouver près du centre.'
        ))

        # Access Info
        cursor.execute('''
            INSERT INTO access_info (property_id, check_in_time, check_out_time, keybox_code, keybox_location, access_instructions)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            property_id,
            '16:00',
            '10:00',
            '1012',
            'La boîte à clés se trouve à l\'entrée principale.',
            'Utilisez ce code pour l\'ouvrir et récupérer les clés de la location.'
        ))

        # Contact Info
        cursor.execute('''
            INSERT INTO contact_info (property_id, host_name, phone, email, whatsapp, airbnb_url, description, response_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            property_id,
            'Votre hôte',
            '+33688461607',
            'solex07700@gmail.com',
            '33688461607',
            'https://www.airbnb.fr/rooms/1057934025843677755',
            'À votre service pour un séjour parfait en Ardèche',
            'Je réponds généralement dans l\'heure'
        ))

        # Emergency Numbers
        emergency_numbers = [
            (property_id, 'SAMU', '15', 'emergency', 1),
            (property_id, 'Pompiers', '18', 'emergency', 2),
            (property_id, 'Police', '17', 'emergency', 3),
            (property_id, 'Urgences Europe', '112', 'emergency', 4)
        ]
        cursor.executemany('''
            INSERT INTO emergency_numbers (property_id, name, number, category, display_order)
            VALUES (?, ?, ?, ?, ?)
        ''', emergency_numbers)

        # Activity Categories
        categories = [
            (property_id, 'Incontournables', 'star.fill', 'yellow', 1),
            (property_id, 'Baignade & Kayak', 'water.waves', 'blue', 2),
            (property_id, 'Villes à visiter', 'building.2.fill', 'purple', 3),
            (property_id, 'Nature & Randonnées', 'leaf.fill', 'green', 4),
            (property_id, 'Marchés provençaux', 'basket.fill', 'orange', 5)
        ]
        cursor.executemany('''
            INSERT INTO activity_categories (property_id, name, icon, color, display_order)
            VALUES (?, ?, ?, ?, ?)
        ''', categories)

        # Activities
        activities = [
            (property_id, 'Gorges de l\'Ardèche', 'Incontournables', 'Route panoramique spectaculaire', '🏞️', '15 min', 1),
            (property_id, 'Pont d\'Arc', 'Incontournables', 'Arche naturelle monumentale', '🌉', '20 min', 2),
            (property_id, 'Grotte Chauvet 2', 'Incontournables', 'Réplique de la grotte préhistorique', '🦴', '25 min', 3),
            (property_id, 'Ferme aux Crocodiles', 'Incontournables', 'Pierrelatte - Plus grand vivarium d\'Europe', '🐊', '15 min', 4),
            (property_id, 'Descente en canoë', 'Baignade & Kayak', 'Mini (8km) ou Maxi (32km)', '🛶', '25 min', 1),
            (property_id, 'Plages de l\'Ardèche', 'Baignade & Kayak', 'Saint-Martin-d\'Ardèche', '🏖️', '10 min', 2),
            (property_id, 'Montélimar', 'Villes à visiter', 'Capitale du nougat', '🍬', '25 min', 1),
            (property_id, 'Avignon', 'Villes à visiter', 'Palais des Papes', '🏰', '50 min', 2)
        ]
        cursor.executemany('''
            INSERT INTO activities (property_id, name, category, description, emoji, distance, display_order)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', activities)

        # Nearby Services
        services = [
            (property_id, 'Pharmacie du Rhône', 'pharmacy', '💊', 'Place du Champ de Mars, 07700 Bourg-Saint-Andéol', None, 'Pharmacie située en plein centre-ville', None, 1),
            (property_id, 'Intermarché SUPER', 'supermarket', '🛒', 'ZAC des Faysses, 07700 Bourg-Saint-Andéol', '0475544650', 'Supermarché complet', 'Lun-Sam: 8h30-19h30', 2),
            (property_id, 'Boulangerie Pâtisserie', 'bakery', '🥖', 'Place du Champ de Mars', None, 'Pain frais et pâtisseries', None, 3)
        ]
        cursor.executemany('''
            INSERT INTO nearby_services (property_id, name, category, icon, address, phone, description, opening_hours, display_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', services)

    def _insert_vaujany_data(self, cursor, property_id):
        """Insert default data for Vaujany"""

        # General Info
        cursor.execute('''
            INSERT INTO general_info (property_id, property_name, welcome_title, welcome_message, welcome_description)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            property_id,
            'Appartement Vaujany',
            'Bienvenue ! 🏔️',
            'Bienvenue dans notre appartement au cœur des Alpes.',
            'Profitez de votre séjour à Vaujany, station familiale au pied de l\'Alpe d\'Huez.'
        ))

        # WiFi
        cursor.execute('''
            INSERT INTO wifi_config (property_id, ssid, password, location_description)
            VALUES (?, ?, ?, ?)
        ''', (
            property_id,
            'Vaujany_WiFi',
            'À configurer',
            'Le WiFi couvre l\'ensemble de l\'appartement.'
        ))

        # Address
        cursor.execute('''
            INSERT INTO address (property_id, street, postal_code, city, country, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            property_id,
            'À configurer',
            '38114',
            'Vaujany',
            'France',
            'L\'appartement se situe dans la station de Vaujany, au pied des pistes.'
        ))

        # Parking
        cursor.execute('''
            INSERT INTO parking_info (property_id, distance, description, is_free, tips)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            property_id,
            '50m',
            'Parking de la résidence disponible.',
            1,
            'En haute saison, pensez à arriver tôt pour avoir une place proche.'
        ))

        # Access Info
        cursor.execute('''
            INSERT INTO access_info (property_id, check_in_time, check_out_time, keybox_code, keybox_location, access_instructions)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            property_id,
            '16:00',
            '10:00',
            'À configurer',
            'À configurer',
            'Instructions d\'accès à configurer.'
        ))

        # Contact Info
        cursor.execute('''
            INSERT INTO contact_info (property_id, host_name, phone, email, whatsapp, airbnb_url, description, response_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            property_id,
            'Votre hôte',
            '+33688461607',
            'solex07700@gmail.com',
            '33688461607',
            '',
            'À votre service pour un séjour parfait en montagne',
            'Je réponds généralement dans l\'heure'
        ))

        # Emergency Numbers
        emergency_numbers = [
            (property_id, 'SAMU', '15', 'emergency', 1),
            (property_id, 'Pompiers', '18', 'emergency', 2),
            (property_id, 'Police', '17', 'emergency', 3),
            (property_id, 'Urgences Europe', '112', 'emergency', 4),
            (property_id, 'Secours Montagne', '112', 'emergency', 5)
        ]
        cursor.executemany('''
            INSERT INTO emergency_numbers (property_id, name, number, category, display_order)
            VALUES (?, ?, ?, ?, ?)
        ''', emergency_numbers)

        # Activity Categories
        categories = [
            (property_id, 'Ski & Montagne', 'snowflake', 'blue', 1),
            (property_id, 'Randonnées', 'figure.hiking', 'green', 2),
            (property_id, 'Bien-être', 'sparkles', 'purple', 3),
            (property_id, 'Gastronomie', 'fork.knife', 'orange', 4)
        ]
        cursor.executemany('''
            INSERT INTO activity_categories (property_id, name, icon, color, display_order)
            VALUES (?, ?, ?, ?, ?)
        ''', categories)

        # Activities
        activities = [
            (property_id, 'Domaine Alpe d\'Huez', 'Ski & Montagne', '250km de pistes', '⛷️', '10 min', 1),
            (property_id, 'Télécabine Vaujany', 'Ski & Montagne', 'Accès direct aux pistes', '🚡', '2 min', 2),
            (property_id, 'Lac du Verney', 'Randonnées', 'Balade familiale', '🏞️', '15 min', 1),
            (property_id, 'Cascade de la Fare', 'Randonnées', 'Randonnée spectaculaire', '💧', '30 min', 2),
            (property_id, 'Centre aquatique', 'Bien-être', 'Piscine et spa', '🏊', '5 min', 1)
        ]
        cursor.executemany('''
            INSERT INTO activities (property_id, name, category, description, emoji, distance, display_order)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', activities)

        # Nearby Services
        services = [
            (property_id, 'Pharmacie de Vaujany', 'pharmacy', '💊', 'Centre village, 38114 Vaujany', None, 'Pharmacie du village', None, 1),
            (property_id, 'Sherpa Supermarché', 'supermarket', '🛒', 'Centre village, 38114 Vaujany', None, 'Épicerie de montagne', '8h-19h', 2),
            (property_id, 'Boulangerie Le Fournil', 'bakery', '🥖', 'Centre village', None, 'Pain frais et spécialités', None, 3)
        ]
        cursor.executemany('''
            INSERT INTO nearby_services (property_id, name, category, icon, address, phone, description, opening_hours, display_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', services)

    # ==================== Properties ====================

    def get_all_properties(self, user_id=None):
        """Get all properties, optionally filtered by user_id"""
        conn = self.get_connection()
        if user_id:
            results = conn.execute(
                'SELECT * FROM properties WHERE is_active = 1 AND user_id = ? ORDER BY display_order',
                (user_id,)
            ).fetchall()
        else:
            results = conn.execute('SELECT * FROM properties WHERE is_active = 1 ORDER BY display_order').fetchall()
        conn.close()
        return [dict(row) for row in results]

    def get_properties_by_user(self, user_id):
        """Get all properties for a specific user with city from address table"""
        conn = self.get_connection()
        results = conn.execute('''
            SELECT p.*, a.city
            FROM properties p
            LEFT JOIN address a ON p.id = a.property_id
            WHERE p.user_id = ? AND p.is_active = 1
            ORDER BY p.display_order
        ''', (user_id,)).fetchall()
        conn.close()
        return [dict(row) for row in results]

    def get_property(self, property_id):
        """Get property by ID with city from address table"""
        conn = self.get_connection()
        result = conn.execute('''
            SELECT p.*, a.city
            FROM properties p
            LEFT JOIN address a ON p.id = a.property_id
            WHERE p.id=?
        ''', (property_id,)).fetchone()
        conn.close()
        return dict(result) if result else None

    def get_property_by_slug(self, slug):
        """Get property by slug with city from address table"""
        conn = self.get_connection()
        result = conn.execute('''
            SELECT p.*, a.city
            FROM properties p
            LEFT JOIN address a ON p.id = a.property_id
            WHERE p.slug=?
        ''', (slug,)).fetchone()
        conn.close()
        return dict(result) if result else None

    def create_property(self, data, user_id=None):
        """Create a new property and initialize all related tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Insert the property
        cursor.execute('''
            INSERT INTO properties (name, slug, icon, location, region, theme, is_active, display_order, user_id)
            VALUES (?, ?, ?, ?, ?, 'mazet-bsa', 1, (SELECT COALESCE(MAX(display_order), 0) + 1 FROM properties), ?)
        ''', (data['name'], data['slug'], data.get('icon', '🏠'), data.get('address', ''), data.get('region', ''), user_id))

        property_id = cursor.lastrowid

        # Initialize general_info
        cursor.execute('''
            INSERT INTO general_info (property_id, property_name, welcome_title, welcome_message, welcome_description)
            VALUES (?, ?, ?, ?, ?)
        ''', (property_id, data['name'], f"Bienvenue à {data['name']}", "Nous sommes ravis de vous accueillir!", "Toutes les informations utiles pour votre séjour."))

        # Initialize wifi_config
        cursor.execute('''
            INSERT INTO wifi_config (property_id, ssid, password, location_description)
            VALUES (?, ?, ?, ?)
        ''', (property_id, "WiFi_" + data['slug'].replace('-', '_'), "À configurer", "À configurer"))

        # Initialize address with geocoded data
        address_parts = data.get('address', '').split(',')
        street = address_parts[0].strip() if address_parts else ''
        city = address_parts[-1].strip() if len(address_parts) > 1 else ''
        postal_code = ''
        # Try to extract postal code
        postal_match = re.search(r'\b(\d{5})\b', data.get('address', ''))
        if postal_match:
            postal_code = postal_match.group(1)

        cursor.execute('''
            INSERT INTO address (property_id, street, postal_code, city, latitude, longitude, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (property_id, street, postal_code, city, data.get('latitude'), data.get('longitude'), data.get('address', '')))

        # Initialize parking_info
        cursor.execute('''
            INSERT INTO parking_info (property_id, distance, description, is_free, tips)
            VALUES (?, ?, ?, ?, ?)
        ''', (property_id, "À configurer", "À configurer", 1, ""))

        # Initialize access_info
        cursor.execute('''
            INSERT INTO access_info (property_id, key_location, arrival_instructions, door_code, special_notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (property_id, "À configurer", "À configurer", "", ""))

        # Initialize contact_info
        cursor.execute('''
            INSERT INTO contact_info (property_id, owner_name, owner_phone, owner_email)
            VALUES (?, ?, ?, ?)
        ''', (property_id, "À configurer", "", ""))

        conn.commit()
        conn.close()

        return property_id

    def duplicate_property_from_template(self, template_property_id, new_property_data, user_id=None):
        """
        Create a new property by duplicating all data from a template property.
        This is used for the "Create without AI" feature.

        Args:
            template_property_id: ID of the template property (e.g., Mazet-Demo = 3)
            new_property_data: dict with 'name', 'address', 'icon', 'latitude', 'longitude', 'region'
            user_id: ID of the user who will own the new property

        Returns:
            The ID of the newly created property
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # 1. Create the new property record
            cursor.execute('''
                INSERT INTO properties (name, slug, icon, location, region, theme, is_active, display_order, user_id)
                VALUES (?, ?, ?, ?, ?, 'mazet-bsa', 1, (SELECT COALESCE(MAX(display_order), 0) + 1 FROM properties), ?)
            ''', (
                new_property_data['name'],
                new_property_data['slug'],
                new_property_data.get('icon', '🏠'),
                new_property_data.get('address', ''),
                new_property_data.get('region', ''),
                user_id
            ))
            new_property_id = cursor.lastrowid

            # 2. Duplicate general_info from template
            cursor.execute('SELECT * FROM general_info WHERE property_id=?', (template_property_id,))
            template_general = cursor.fetchone()
            if template_general:
                cursor.execute('''
                    INSERT INTO general_info (property_id, property_name, welcome_title, welcome_message, welcome_description)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    new_property_id,
                    new_property_data['name'],  # Use the new property name
                    f"Bienvenue à {new_property_data['name']} ! 🌿",
                    template_general['welcome_message'],
                    template_general['welcome_description']
                ))

            # 3. Duplicate wifi_config from template
            cursor.execute('SELECT * FROM wifi_config WHERE property_id=?', (template_property_id,))
            template_wifi = cursor.fetchone()
            if template_wifi:
                cursor.execute('''
                    INSERT INTO wifi_config (property_id, ssid, password, location_description)
                    VALUES (?, ?, ?, ?)
                ''', (
                    new_property_id,
                    "WiFi_" + new_property_data['slug'].replace('-', '_'),  # Generate new SSID
                    "À configurer",  # Password to be configured
                    template_wifi['location_description']
                ))

            # 4. Parse and insert address
            address_str = new_property_data.get('address', '')
            address_parts = address_str.split(',')

            # Try to extract components from the address
            street = address_parts[0].strip() if address_parts else ''
            city = ''
            postal_code = ''
            country = 'France'

            # Parse address: typically "Street, Postal Code City, Country" or "Street, City"
            if len(address_parts) >= 2:
                # Look for postal code (5 digits in France)
                for part in address_parts[1:]:
                    postal_match = re.search(r'\b(\d{5})\b', part)
                    if postal_match:
                        postal_code = postal_match.group(1)
                        # City is the part after the postal code
                        city_part = part.replace(postal_code, '').strip()
                        if city_part:
                            city = city_part
                    elif not city and part.strip():
                        city = part.strip()

            # If city wasn't found but we have multiple parts, use the last one
            if not city and len(address_parts) > 1:
                city = address_parts[-1].strip()

            cursor.execute('''
                INSERT INTO address (property_id, street, postal_code, city, country, latitude, longitude, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                new_property_id,
                street,
                postal_code,
                city,
                country,
                new_property_data.get('latitude'),
                new_property_data.get('longitude'),
                address_str  # Full address as description
            ))

            # 5. Duplicate parking_info from template
            cursor.execute('SELECT * FROM parking_info WHERE property_id=?', (template_property_id,))
            template_parking = cursor.fetchone()
            if template_parking:
                cursor.execute('''
                    INSERT INTO parking_info (property_id, distance, description, is_free, tips)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    new_property_id,
                    template_parking['distance'],
                    template_parking['description'],
                    template_parking['is_free'],
                    template_parking['tips']
                ))

            # 6. Duplicate access_info from template
            cursor.execute('SELECT * FROM access_info WHERE property_id=?', (template_property_id,))
            template_access = cursor.fetchone()
            if template_access:
                access_dict = dict(template_access)
                cursor.execute('''
                    INSERT INTO access_info (property_id, check_in_time, check_out_time, keybox_code, keybox_location, access_instructions)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    new_property_id,
                    access_dict.get('check_in_time', '16:00'),
                    access_dict.get('check_out_time', '10:00'),
                    access_dict.get('keybox_code', ''),
                    access_dict.get('keybox_location', ''),
                    access_dict.get('access_instructions', '')
                ))

            # 7. Duplicate contact_info from template (with placeholder values)
            cursor.execute('SELECT * FROM contact_info WHERE property_id=?', (template_property_id,))
            template_contact = cursor.fetchone()
            if template_contact:
                contact_dict = dict(template_contact)
                cursor.execute('''
                    INSERT INTO contact_info (property_id, host_name, phone, email, whatsapp, airbnb_url, description, response_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    new_property_id,
                    contact_dict.get('host_name', 'Votre nom'),
                    contact_dict.get('phone', 'À configurer'),
                    contact_dict.get('email', 'À configurer'),
                    contact_dict.get('whatsapp', ''),
                    contact_dict.get('airbnb_url', ''),
                    contact_dict.get('description', 'À votre service pour un séjour parfait'),
                    contact_dict.get('response_time', 'Réponse rapide')
                ))

            # 8. Duplicate activities from template
            cursor.execute('SELECT * FROM activities WHERE property_id=?', (template_property_id,))
            template_activities = cursor.fetchall()
            for activity in template_activities:
                cursor.execute('''
                    INSERT INTO activities (property_id, category, name, description, emoji, distance, latitude, longitude, display_order)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    new_property_id,
                    activity['category'],
                    activity['name'],
                    activity['description'],
                    activity['emoji'],
                    activity['distance'],
                    activity['latitude'],
                    activity['longitude'],
                    activity['display_order']
                ))

            # 9. Duplicate nearby_services from template
            cursor.execute('SELECT * FROM nearby_services WHERE property_id=?', (template_property_id,))
            template_services = cursor.fetchall()
            for service in template_services:
                cursor.execute('''
                    INSERT INTO nearby_services (property_id, category, name, description, address, phone, opening_hours, icon, latitude, longitude, display_order)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    new_property_id,
                    service['category'],
                    service['name'],
                    service['description'],
                    service['address'],
                    service['phone'],
                    service['opening_hours'],
                    service['icon'],
                    service['latitude'],
                    service['longitude'],
                    service['display_order']
                ))

            # 10. Duplicate emergency_numbers from template
            cursor.execute('SELECT * FROM emergency_numbers WHERE property_id=?', (template_property_id,))
            template_emergency = cursor.fetchall()
            for emergency in template_emergency:
                cursor.execute('''
                    INSERT INTO emergency_numbers (property_id, name, number, category, display_order)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    new_property_id,
                    emergency['name'],
                    emergency['number'],
                    emergency['category'],
                    emergency['display_order']
                ))

            # 11. Duplicate amenities from template
            cursor.execute('SELECT * FROM amenities WHERE property_id=?', (template_property_id,))
            template_amenities = cursor.fetchall()
            for amenity in template_amenities:
                cursor.execute('''
                    INSERT INTO amenities (property_id, category, name, icon, description, display_order)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    new_property_id,
                    amenity['category'],
                    amenity['name'],
                    amenity['icon'],
                    amenity['description'],
                    amenity['display_order']
                ))

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

        return new_property_id

    def get_template_property_id(self):
        """Get the ID of the template property (Mazet - Demo)"""
        conn = self.get_connection()
        result = conn.execute("SELECT id FROM properties WHERE slug = 'mazet-demo' OR name LIKE '%Demo%' LIMIT 1").fetchone()
        conn.close()
        return result['id'] if result else None

    # ==================== General Info ====================

    def get_general_info(self, property_id=1):
        conn = self.get_connection()
        result = conn.execute('''
            SELECT gi.*, p.region, a.city
            FROM general_info gi
            LEFT JOIN properties p ON gi.property_id = p.id
            LEFT JOIN address a ON gi.property_id = a.property_id
            WHERE gi.property_id=?
            ORDER BY gi.id DESC LIMIT 1
        ''', (property_id,)).fetchone()
        conn.close()
        return dict(result) if result else None

    def update_general_info(self, property_id, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE general_info
            SET property_name=?, welcome_title=?, welcome_message=?, welcome_description=?, updated_at=CURRENT_TIMESTAMP
            WHERE property_id=?
        ''', (data['property_name'], data['welcome_title'], data['welcome_message'], data['welcome_description'], property_id))

        # Also update the property name in the properties table (for the dropdown menu)
        cursor.execute('''
            UPDATE properties
            SET name=?
            WHERE id=?
        ''', (data['property_name'], property_id))

        conn.commit()
        conn.close()

    def update_header_image(self, property_id, image_filename):
        """Update the header image for a property"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE general_info
            SET header_image=?, updated_at=CURRENT_TIMESTAMP
            WHERE property_id=?
        ''', (image_filename, property_id))
        conn.commit()
        conn.close()

    def delete_header_image(self, property_id):
        """Delete the header image for a property"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE general_info
            SET header_image=NULL, updated_at=CURRENT_TIMESTAMP
            WHERE property_id=?
        ''', (property_id,))
        conn.commit()
        conn.close()

    # ==================== WiFi ====================

    def get_wifi_config(self, property_id=1):
        conn = self.get_connection()
        result = conn.execute('SELECT * FROM wifi_config WHERE property_id=? ORDER BY id DESC LIMIT 1', (property_id,)).fetchone()
        conn.close()
        return dict(result) if result else None

    def update_wifi_config(self, property_id, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE wifi_config
            SET ssid=?, password=?, location_description=?, updated_at=CURRENT_TIMESTAMP
            WHERE property_id=?
        ''', (data['ssid'], data['password'], data['location_description'], property_id))
        conn.commit()
        conn.close()

    # ==================== Address ====================

    def get_address(self, property_id=1):
        conn = self.get_connection()
        result = conn.execute('SELECT * FROM address WHERE property_id=? ORDER BY id DESC LIMIT 1', (property_id,)).fetchone()
        conn.close()
        return dict(result) if result else None

    def update_address(self, property_id, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE address
            SET street=?, postal_code=?, city=?, country=?, description=?, updated_at=CURRENT_TIMESTAMP
            WHERE property_id=?
        ''', (data['street'], data['postal_code'], data['city'], data['country'], data['description'], property_id))
        conn.commit()
        conn.close()

    def update_address_description(self, property_id, description):
        """Update only the description field of an address (used by AI generation)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE address
            SET description=?, updated_at=CURRENT_TIMESTAMP
            WHERE property_id=?
        ''', (description, property_id))
        conn.commit()
        conn.close()

    # ==================== Parking ====================

    def get_parking_info(self, property_id=1):
        conn = self.get_connection()
        result = conn.execute('SELECT * FROM parking_info WHERE property_id=? ORDER BY id DESC LIMIT 1', (property_id,)).fetchone()
        conn.close()
        return dict(result) if result else None

    def update_parking_info(self, property_id, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE parking_info
            SET distance=?, description=?, is_free=?, tips=?, updated_at=CURRENT_TIMESTAMP
            WHERE property_id=?
        ''', (data['distance'], data['description'], data.get('is_free', True), data.get('tips', ''), property_id))
        conn.commit()
        conn.close()

    # ==================== Access ====================

    def get_access_info(self, property_id=1):
        conn = self.get_connection()
        result = conn.execute('SELECT * FROM access_info WHERE property_id=? ORDER BY id DESC LIMIT 1', (property_id,)).fetchone()
        conn.close()
        return dict(result) if result else None

    def update_access_info(self, property_id, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE access_info
            SET check_in_time=?, check_out_time=?, keybox_code=?, keybox_location=?, access_instructions=?, updated_at=CURRENT_TIMESTAMP
            WHERE property_id=?
        ''', (data['check_in_time'], data['check_out_time'], data['keybox_code'], data['keybox_location'], data['access_instructions'], property_id))
        conn.commit()
        conn.close()

    # ==================== Contact ====================

    def get_contact_info(self, property_id=1):
        conn = self.get_connection()
        result = conn.execute('SELECT * FROM contact_info WHERE property_id=? ORDER BY id DESC LIMIT 1', (property_id,)).fetchone()
        conn.close()
        return dict(result) if result else None

    def update_contact_info(self, property_id, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE contact_info
            SET host_name=?, phone=?, email=?, whatsapp=?, airbnb_url=?, description=?, response_time=?, updated_at=CURRENT_TIMESTAMP
            WHERE property_id=?
        ''', (data['host_name'], data['phone'], data['email'], data.get('whatsapp', ''), data.get('airbnb_url', ''), data.get('description', ''), data.get('response_time', ''), property_id))
        conn.commit()
        conn.close()

    def update_contact_avatar(self, property_id, avatar_filename):
        """Update only the avatar field for a contact"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE contact_info
            SET avatar=?, updated_at=CURRENT_TIMESTAMP
            WHERE property_id=?
        ''', (avatar_filename, property_id))
        conn.commit()
        conn.close()

    # ==================== Activities ====================

    def get_all_activities(self, property_id=1):
        conn = self.get_connection()
        results = conn.execute('SELECT * FROM activities WHERE property_id=? ORDER BY category, display_order', (property_id,)).fetchall()
        conn.close()
        return [dict(row) for row in results]

    def get_activity(self, activity_id):
        conn = self.get_connection()
        result = conn.execute('SELECT * FROM activities WHERE id=?', (activity_id,)).fetchone()
        conn.close()
        return dict(result) if result else None

    def create_activity(self, property_id, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO activities (property_id, name, category, description, emoji, distance, display_order)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (property_id, data['name'], data['category'], data['description'], data['emoji'], data['distance'], data.get('display_order', 0)))
        conn.commit()
        activity_id = cursor.lastrowid
        conn.close()
        return activity_id

    def update_activity(self, activity_id, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE activities
            SET name=?, category=?, description=?, emoji=?, distance=?, display_order=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (data['name'], data['category'], data['description'], data['emoji'], data['distance'], data.get('display_order', 0), activity_id))
        conn.commit()
        conn.close()

    def delete_activity(self, activity_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM activities WHERE id=?', (activity_id,))
        conn.commit()
        conn.close()

    def delete_all_activities(self, property_id):
        """Delete all activities and activity categories for a property (used before AI generation)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM activities WHERE property_id=?', (property_id,))
        cursor.execute('DELETE FROM activity_categories WHERE property_id=?', (property_id,))
        conn.commit()
        conn.close()

    # ==================== Emergency ====================

    def get_all_emergency_numbers(self, property_id=1):
        conn = self.get_connection()
        results = conn.execute('SELECT * FROM emergency_numbers WHERE property_id=? ORDER BY display_order', (property_id,)).fetchall()
        conn.close()
        return [dict(row) for row in results]

    # ==================== Services ====================

    def get_all_nearby_services(self, property_id=1):
        conn = self.get_connection()
        results = conn.execute('SELECT * FROM nearby_services WHERE property_id=? ORDER BY display_order', (property_id,)).fetchall()
        conn.close()
        return [dict(row) for row in results]

    def get_nearby_service(self, service_id):
        conn = self.get_connection()
        result = conn.execute('SELECT * FROM nearby_services WHERE id=?', (service_id,)).fetchone()
        conn.close()
        return dict(result) if result else None

    def create_nearby_service(self, property_id, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO nearby_services (property_id, name, category, icon, address, phone, description, opening_hours, display_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (property_id, data['name'], data['category'], data.get('icon'), data['address'], data.get('phone'), data.get('description'), data.get('opening_hours'), data.get('display_order', 0)))
        conn.commit()
        service_id = cursor.lastrowid
        conn.close()
        return service_id

    def update_nearby_service(self, service_id, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE nearby_services
            SET name=?, category=?, icon=?, address=?, phone=?, description=?, opening_hours=?, display_order=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (data['name'], data['category'], data.get('icon'), data['address'], data.get('phone'), data.get('description'), data.get('opening_hours'), data.get('display_order', 0), service_id))
        conn.commit()
        conn.close()

    def delete_nearby_service(self, service_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM nearby_services WHERE id=?', (service_id,))
        conn.commit()
        conn.close()

    def delete_all_nearby_services(self, property_id):
        """Delete all nearby services for a property (used before AI generation)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM nearby_services WHERE property_id=?', (property_id,))
        conn.commit()
        conn.close()

    # ==================== Activity Categories ====================

    def get_all_activity_categories(self, property_id=1):
        conn = self.get_connection()
        # First, sync categories from existing activities
        self._sync_activity_categories(property_id, conn)
        results = conn.execute('SELECT * FROM activity_categories WHERE property_id=? ORDER BY display_order', (property_id,)).fetchall()
        conn.close()
        return [dict(row) for row in results]

    def _sync_activity_categories(self, property_id, conn):
        """Auto-create categories from existing activities that don't have a category entry"""
        cursor = conn.cursor()
        # Get all unique categories from activities
        activity_cats = cursor.execute(
            'SELECT DISTINCT category FROM activities WHERE property_id=? AND category IS NOT NULL AND category != ""',
            (property_id,)
        ).fetchall()

        # Get existing category names
        existing_cats = cursor.execute(
            'SELECT name FROM activity_categories WHERE property_id=?',
            (property_id,)
        ).fetchall()
        existing_names = {row['name'] for row in existing_cats}

        # Default icons for common categories
        default_icons = {
            'Incontournables': '⭐',
            'Baignade & Kayak': '🏊',
            'Villes à visiter': '🏛️',
            'Nature & Randonnées': '🌿',
            'Marchés provençaux': '🧺',
            'Gastronomie': '🍽️',
            'Culture': '📚',
            'Sports': '⚽',
            'Famille': '👨‍👩‍👧‍👦'
        }

        # Get current max order
        max_order = cursor.execute(
            'SELECT MAX(display_order) FROM activity_categories WHERE property_id=?',
            (property_id,)
        ).fetchone()[0] or 0

        # Create missing categories
        for row in activity_cats:
            cat_name = row['category']
            if cat_name and cat_name not in existing_names:
                max_order += 1
                icon = default_icons.get(cat_name, '📍')
                cursor.execute('''
                    INSERT INTO activity_categories (property_id, name, icon, display_order)
                    VALUES (?, ?, ?, ?)
                ''', (property_id, cat_name, icon, max_order))

        conn.commit()

    def create_activity_category(self, property_id, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        # Get max display_order
        max_order = cursor.execute('SELECT MAX(display_order) FROM activity_categories WHERE property_id=?', (property_id,)).fetchone()[0] or 0
        cursor.execute('''
            INSERT INTO activity_categories (property_id, name, icon, color, display_order)
            VALUES (?, ?, ?, ?, ?)
        ''', (property_id, data['name'], data.get('icon', '📍'), data.get('color', ''), max_order + 1))
        category_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return category_id

    def update_activity_category(self, category_id, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE activity_categories
            SET name=?, icon=?, color=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (data['name'], data.get('icon', '📍'), data.get('color', ''), category_id))
        conn.commit()
        conn.close()

    def delete_activity_category(self, category_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        # Get category name first
        cat = cursor.execute('SELECT name FROM activity_categories WHERE id=?', (category_id,)).fetchone()
        if cat:
            # Delete activities in this category
            cursor.execute('DELETE FROM activities WHERE category=?', (cat['name'],))
        cursor.execute('DELETE FROM activity_categories WHERE id=?', (category_id,))
        conn.commit()
        conn.close()

    def reorder_activity_categories(self, property_id, category_ids):
        """Reorder categories based on the provided list of IDs"""
        conn = self.get_connection()
        cursor = conn.cursor()
        for order, cat_id in enumerate(category_ids):
            cursor.execute('UPDATE activity_categories SET display_order=? WHERE id=? AND property_id=?',
                         (order, cat_id, property_id))
        conn.commit()
        conn.close()

    def reorder_activities(self, category_name, activity_ids):
        """Reorder activities within a category based on the provided list of IDs"""
        conn = self.get_connection()
        cursor = conn.cursor()
        for order, activity_id in enumerate(activity_ids):
            cursor.execute('UPDATE activities SET display_order=? WHERE id=? AND category=?',
                         (order, activity_id, category_name))
        conn.commit()
        conn.close()

    # ==================== Export ====================

    def export_all_data(self, property_id=1):
        """Export all data as JSON for the iOS app"""
        data = {
            'general_info': self.get_general_info(property_id),
            'wifi': self.get_wifi_config(property_id),
            'address': self.get_address(property_id),
            'parking': self.get_parking_info(property_id),
            'access': self.get_access_info(property_id),
            'contact': self.get_contact_info(property_id),
            'emergency_numbers': self.get_all_emergency_numbers(property_id),
            'nearby_services': self.get_all_nearby_services(property_id),
            'activities': self.get_all_activities(property_id),
            'activity_categories': self.get_all_activity_categories(property_id),
            'exported_at': datetime.now().isoformat()
        }
        return data

    # ==================== Users ====================

    def get_user_by_email(self, email):
        """Get a user by email"""
        conn = self.get_connection()
        result = conn.execute('SELECT * FROM users WHERE email=? AND is_active=1', (email.lower(),)).fetchone()
        conn.close()
        return dict(result) if result else None

    def get_user_by_id(self, user_id):
        """Get a user by ID"""
        conn = self.get_connection()
        result = conn.execute('SELECT * FROM users WHERE id=? AND is_active=1', (user_id,)).fetchone()
        conn.close()
        return dict(result) if result else None

    def create_user(self, data):
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (email, firstname, lastname, password_hash, google_id, password_plain)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['email'].lower(),
            data['firstname'],
            data['lastname'],
            data.get('password_hash'),
            data.get('google_id'),
            data.get('password_plain')
        ))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id

    def update_user(self, user_id, data):
        """Update user information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users
            SET firstname=?, lastname=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (data.get('firstname'), data.get('lastname'), user_id))
        conn.commit()
        conn.close()

    def update_user_password(self, user_id, password_hash, password_plain=None):
        """Update user password"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if password_plain:
            cursor.execute('''
                UPDATE users
                SET password_hash=?, password_plain=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (password_hash, password_plain, user_id))
        else:
            cursor.execute('''
                UPDATE users
                SET password_hash=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (password_hash, user_id))
        conn.commit()
        conn.close()

    def update_user_google_id(self, user_id, google_id):
        """Update user's Google ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users
            SET google_id=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (google_id, user_id))
        conn.commit()
        conn.close()

    # ==================== Password Reset Tokens ====================

    def create_password_reset_token(self, user_id, token, expires_at):
        """Create a password reset token"""
        conn = self.get_connection()
        cursor = conn.cursor()
        # Invalidate any existing tokens for this user
        cursor.execute('UPDATE password_reset_tokens SET used = 1 WHERE user_id = ? AND used = 0', (user_id,))
        # Create new token
        cursor.execute('''
            INSERT INTO password_reset_tokens (user_id, token, expires_at)
            VALUES (?, ?, ?)
        ''', (user_id, token, expires_at))
        conn.commit()
        token_id = cursor.lastrowid
        conn.close()
        return token_id

    def get_valid_reset_token(self, token):
        """Get a valid (unused, not expired) reset token"""
        conn = self.get_connection()
        result = conn.execute('''
            SELECT prt.*, u.email, u.firstname, u.lastname
            FROM password_reset_tokens prt
            JOIN users u ON prt.user_id = u.id
            WHERE prt.token = ? AND prt.used = 0 AND prt.expires_at > datetime('now')
        ''', (token,)).fetchone()
        conn.close()
        return dict(result) if result else None

    def mark_token_as_used(self, token):
        """Mark a reset token as used"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE password_reset_tokens SET used = 1 WHERE token = ?', (token,))
        conn.commit()
        conn.close()

    # ==================== Photos ====================

    def get_all_photos(self, property_id):
        """Get all photos for a property"""
        conn = self.get_connection()
        results = conn.execute(
            'SELECT * FROM photos WHERE property_id=? ORDER BY display_order, uploaded_at DESC',
            (property_id,)
        ).fetchall()
        conn.close()
        return [dict(row) for row in results]

    def get_photo(self, photo_id):
        """Get a single photo by ID"""
        conn = self.get_connection()
        result = conn.execute('SELECT * FROM photos WHERE id=?', (photo_id,)).fetchone()
        conn.close()
        return dict(result) if result else None

    def create_photo(self, data, property_id):
        """Create a new photo entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO photos (property_id, filename, original_name, title, description, display_order)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            property_id,
            data['filename'],
            data['original_name'],
            data.get('title', ''),
            data.get('description', ''),
            data.get('display_order', 0)
        ))
        conn.commit()
        photo_id = cursor.lastrowid
        conn.close()
        return photo_id

    def update_photo(self, photo_id, data):
        """Update a photo's metadata"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE photos
            SET title=?, description=?, display_order=?
            WHERE id=?
        ''', (
            data.get('title', ''),
            data.get('description', ''),
            data.get('display_order', 0),
            photo_id
        ))
        conn.commit()
        conn.close()

    def delete_photo(self, photo_id):
        """Delete a photo entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM photos WHERE id=?', (photo_id,))
        conn.commit()
        conn.close()

    # ==================== Access Photos ====================

    def get_all_access_photos(self, property_id):
        """Get all access photos for a property"""
        conn = self.get_connection()
        results = conn.execute(
            'SELECT * FROM access_photos WHERE property_id=? ORDER BY display_order, uploaded_at DESC',
            (property_id,)
        ).fetchall()
        conn.close()
        return [dict(row) for row in results]

    def get_access_photo(self, photo_id):
        """Get a single access photo by ID"""
        conn = self.get_connection()
        result = conn.execute('SELECT * FROM access_photos WHERE id=?', (photo_id,)).fetchone()
        conn.close()
        return dict(result) if result else None

    def create_access_photo(self, data, property_id):
        """Create a new access photo entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO access_photos (property_id, filename, original_name, title, description, display_order)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            property_id,
            data['filename'],
            data['original_name'],
            data.get('title', ''),
            data.get('description', ''),
            data.get('display_order', 0)
        ))
        conn.commit()
        photo_id = cursor.lastrowid
        conn.close()
        return photo_id

    def count_access_photos(self, property_id):
        """Count access photos for a property"""
        conn = self.get_connection()
        result = conn.execute('SELECT COUNT(*) FROM access_photos WHERE property_id=?', (property_id,)).fetchone()
        conn.close()
        return result[0] if result else 0

    def update_access_photo(self, photo_id, data):
        """Update an access photo's metadata"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE access_photos
            SET title=?, description=?, display_order=?
            WHERE id=?
        ''', (
            data.get('title', ''),
            data.get('description', ''),
            data.get('display_order', 0),
            photo_id
        ))
        conn.commit()
        conn.close()

    def delete_access_photo(self, photo_id):
        """Delete an access photo entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM access_photos WHERE id=?', (photo_id,))
        conn.commit()
        conn.close()

    # ==================== App Config ====================

    def get_app_config(self, key):
        """Get a config value by key"""
        conn = self.get_connection()
        result = conn.execute('SELECT config_value FROM app_config WHERE config_key=?', (key,)).fetchone()
        conn.close()
        return result[0] if result else None

    def get_all_app_config(self):
        """Get all app config values"""
        conn = self.get_connection()
        results = conn.execute('SELECT config_key, config_value, description FROM app_config').fetchall()
        conn.close()
        return {row[0]: {'value': row[1], 'description': row[2]} for row in results}

    def set_app_config(self, key, value, description=None):
        """Set a config value"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM app_config WHERE config_key=?', (key,))
        if cursor.fetchone():
            if description:
                cursor.execute('''
                    UPDATE app_config SET config_value=?, description=?, updated_at=CURRENT_TIMESTAMP
                    WHERE config_key=?
                ''', (value, description, key))
            else:
                cursor.execute('''
                    UPDATE app_config SET config_value=?, updated_at=CURRENT_TIMESTAMP
                    WHERE config_key=?
                ''', (value, key))
        else:
            cursor.execute('''
                INSERT INTO app_config (config_key, config_value, description)
                VALUES (?, ?, ?)
            ''', (key, value, description or ''))
        conn.commit()
        conn.close()

    # ==================== Amenities (Équipements) ====================

    # Liste des équipements prédéfinis par catégorie
    DEFAULT_AMENITIES = [
        # Literie
        {'category': 'Literie', 'name': 'Lits faits à l\'arrivée', 'icon': '🛏️', 'display_order': 1},
        {'category': 'Literie', 'name': 'Oreillers', 'icon': '💤', 'display_order': 2},
        {'category': 'Literie', 'name': 'Couettes', 'icon': '🛋️', 'display_order': 3},
        {'category': 'Literie', 'name': 'Couvertures supplémentaires', 'icon': '🧣', 'display_order': 4},
        {'category': 'Literie', 'name': 'Lit bébé', 'icon': '🚒', 'display_order': 5},

        # Salle de bain
        {'category': 'Salle de bain', 'name': 'Serviettes', 'icon': '🛁', 'display_order': 1},
        {'category': 'Salle de bain', 'name': 'Sèche-cheveux', 'icon': '💨', 'display_order': 2},
        {'category': 'Salle de bain', 'name': 'Savon / Gel douche', 'icon': '🧴', 'display_order': 3},
        {'category': 'Salle de bain', 'name': 'Shampoing', 'icon': '🧴', 'display_order': 4},
        {'category': 'Salle de bain', 'name': 'Papier toilette', 'icon': '🧻', 'display_order': 5},

        # Cuisine - Électroménager
        {'category': 'Cuisine - Électroménager', 'name': 'Réfrigérateur', 'icon': '🧊', 'display_order': 1},
        {'category': 'Cuisine - Électroménager', 'name': 'Congélateur', 'icon': '❄️', 'display_order': 2},
        {'category': 'Cuisine - Électroménager', 'name': 'Four', 'icon': '♨️', 'display_order': 3},
        {'category': 'Cuisine - Électroménager', 'name': 'Micro-ondes', 'icon': '⏱️', 'display_order': 4},
        {'category': 'Cuisine - Électroménager', 'name': 'Plaques de cuisson', 'icon': '🍳', 'display_order': 5},
        {'category': 'Cuisine - Électroménager', 'name': 'Lave-vaisselle', 'icon': '🍽️', 'display_order': 6},
        {'category': 'Cuisine - Électroménager', 'name': 'Cafetière', 'icon': '☕', 'display_order': 7},
        {'category': 'Cuisine - Électroménager', 'name': 'Bouilloire', 'icon': '🫖', 'display_order': 8},
        {'category': 'Cuisine - Électroménager', 'name': 'Grille-pain', 'icon': '🥪', 'display_order': 9},
        {'category': 'Cuisine - Électroménager', 'name': 'Mixeur / Blender', 'icon': '🥣', 'display_order': 10},

        # Cuisine - Ustensiles
        {'category': 'Cuisine - Ustensiles', 'name': 'Casseroles et poêles', 'icon': '🍳', 'display_order': 1},
        {'category': 'Cuisine - Ustensiles', 'name': 'Vaisselle complète', 'icon': '🍽️', 'display_order': 2},
        {'category': 'Cuisine - Ustensiles', 'name': 'Couverts', 'icon': '🍴', 'display_order': 3},
        {'category': 'Cuisine - Ustensiles', 'name': 'Verres et tasses', 'icon': '🥛', 'display_order': 4},
        {'category': 'Cuisine - Ustensiles', 'name': 'Ustensiles de cuisine', 'icon': '🥄', 'display_order': 5},
        {'category': 'Cuisine - Ustensiles', 'name': 'Planche à découper', 'icon': '🔪', 'display_order': 6},
        {'category': 'Cuisine - Ustensiles', 'name': 'Ouvre-bouteille / Tire-bouchon', 'icon': '🍾', 'display_order': 7},

        # Cuisine - Provisions
        {'category': 'Cuisine - Provisions', 'name': 'Sel et poivre', 'icon': '🧂', 'display_order': 1},
        {'category': 'Cuisine - Provisions', 'name': 'Huile et vinaigre', 'icon': '🫒', 'display_order': 2},
        {'category': 'Cuisine - Provisions', 'name': 'Café / Thé', 'icon': '☕', 'display_order': 3},
        {'category': 'Cuisine - Provisions', 'name': 'Sucre', 'icon': '🧊', 'display_order': 4},

        # Multimédia
        {'category': 'Multimédia', 'name': 'Télévision', 'icon': '📺', 'display_order': 1},
        {'category': 'Multimédia', 'name': 'Netflix / Streaming', 'icon': '🎬', 'display_order': 2},
        {'category': 'Multimédia', 'name': 'Enceinte Bluetooth', 'icon': '🔊', 'display_order': 3},
        {'category': 'Multimédia', 'name': 'Jeux de société', 'icon': '🎲', 'display_order': 4},
        {'category': 'Multimédia', 'name': 'Livres', 'icon': '📚', 'display_order': 5},

        # Ménage
        {'category': 'Ménage', 'name': 'Aspirateur', 'icon': '🧹', 'display_order': 1},
        {'category': 'Ménage', 'name': 'Balai et pelle', 'icon': '🧹', 'display_order': 2},
        {'category': 'Ménage', 'name': 'Fer à repasser', 'icon': '👔', 'display_order': 3},
        {'category': 'Ménage', 'name': 'Lave-linge', 'icon': '🌀', 'display_order': 4},
        {'category': 'Ménage', 'name': 'Sèche-linge', 'icon': '💨', 'display_order': 5},
        {'category': 'Ménage', 'name': 'Étendoir', 'icon': '👕', 'display_order': 6},
        {'category': 'Ménage', 'name': 'Produits ménagers', 'icon': '🧽', 'display_order': 7},

        # Extérieur
        {'category': 'Extérieur', 'name': 'Terrasse / Balcon', 'icon': '🌳', 'display_order': 1},
        {'category': 'Extérieur', 'name': 'Jardin', 'icon': '🌿', 'display_order': 2},
        {'category': 'Extérieur', 'name': 'Barbecue', 'icon': '🔥', 'display_order': 3},
        {'category': 'Extérieur', 'name': 'Mobilier de jardin', 'icon': '🪑', 'display_order': 4},
        {'category': 'Extérieur', 'name': 'Piscine', 'icon': '🏊', 'display_order': 5},
        {'category': 'Extérieur', 'name': 'Parking privé', 'icon': '🅿️', 'display_order': 6},
        {'category': 'Extérieur', 'name': 'Vélos', 'icon': '🚲', 'display_order': 7},

        # Confort
        {'category': 'Confort', 'name': 'Climatisation', 'icon': '❄️', 'display_order': 1},
        {'category': 'Confort', 'name': 'Chauffage', 'icon': '🌡️', 'display_order': 2},
        {'category': 'Confort', 'name': 'Cheminée', 'icon': '🏠', 'display_order': 3},
        {'category': 'Confort', 'name': 'Ventilateur', 'icon': '🌀', 'display_order': 4},

        # Sécurité
        {'category': 'Sécurité', 'name': 'Détecteur de fumée', 'icon': '🚨', 'display_order': 1},
        {'category': 'Sécurité', 'name': 'Détecteur de CO', 'icon': '🚨', 'display_order': 2},
        {'category': 'Sécurité', 'name': 'Extincteur', 'icon': '🧯', 'display_order': 3},
        {'category': 'Sécurité', 'name': 'Trousse de secours', 'icon': '🩹', 'display_order': 4},
        {'category': 'Sécurité', 'name': 'Coffre-fort', 'icon': '🔐', 'display_order': 5},

        # Famille
        {'category': 'Famille', 'name': 'Chaise haute', 'icon': '🪑', 'display_order': 1},
        {'category': 'Famille', 'name': 'Baignoire bébé', 'icon': '🛁', 'display_order': 2},
        {'category': 'Famille', 'name': 'Jouets enfants', 'icon': '🧸', 'display_order': 3},
        {'category': 'Famille', 'name': 'Barrière de sécurité', 'icon': '🚧', 'display_order': 4},
    ]

    def get_all_amenities(self, property_id=1):
        """Get all amenities for a property"""
        conn = self.get_connection()
        results = conn.execute('SELECT * FROM amenities WHERE property_id=? ORDER BY category, display_order', (property_id,)).fetchall()
        conn.close()
        return [dict(row) for row in results]

    def get_amenity(self, amenity_id):
        """Get a single amenity by ID"""
        conn = self.get_connection()
        result = conn.execute('SELECT * FROM amenities WHERE id=?', (amenity_id,)).fetchone()
        conn.close()
        return dict(result) if result else None

    def initialize_amenities_for_property(self, property_id):
        """Initialize all default amenities for a property (all unchecked by default)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Check if amenities already exist for this property
        cursor.execute('SELECT COUNT(*) FROM amenities WHERE property_id=?', (property_id,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return  # Already initialized

        for amenity in self.DEFAULT_AMENITIES:
            cursor.execute('''
                INSERT INTO amenities (property_id, category, name, icon, description, display_order, is_available)
                VALUES (?, ?, ?, ?, ?, ?, 0)
            ''', (property_id, amenity['category'], amenity['name'], amenity['icon'], '', amenity['display_order']))

        conn.commit()
        conn.close()

    def toggle_amenity(self, amenity_id, is_available):
        """Toggle the availability of an amenity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE amenities
            SET is_available=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (1 if is_available else 0, amenity_id))
        conn.commit()
        conn.close()

    def create_amenity(self, property_id, data):
        """Create a new custom amenity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO amenities (property_id, category, name, icon, description, display_order, is_available)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (property_id, data['category'], data['name'], data.get('icon', ''), data.get('description', ''), data.get('display_order', 0), 1))
        conn.commit()
        amenity_id = cursor.lastrowid
        conn.close()
        return amenity_id

    def update_amenity(self, amenity_id, data):
        """Update an amenity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE amenities
            SET category=?, name=?, icon=?, description=?, display_order=?, is_available=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (data['category'], data['name'], data.get('icon', ''), data.get('description', ''), data.get('display_order', 0), data.get('is_available', 1), amenity_id))
        conn.commit()
        conn.close()

    def delete_amenity(self, amenity_id):
        """Delete an amenity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM amenities WHERE id=?', (amenity_id,))
        conn.commit()
        conn.close()

    def get_amenity_categories(self, property_id=1):
        """Get distinct amenity categories for a property"""
        conn = self.get_connection()
        results = conn.execute('SELECT DISTINCT category FROM amenities WHERE property_id=? ORDER BY category', (property_id,)).fetchall()
        conn.close()
        return [row['category'] for row in results]

    def get_available_amenities(self, property_id=1):
        """Get only available amenities for a property (for display to guests)"""
        conn = self.get_connection()
        results = conn.execute('SELECT * FROM amenities WHERE property_id=? AND is_available=1 ORDER BY category, display_order', (property_id,)).fetchall()
        conn.close()
        return [dict(row) for row in results]

    # ==================== Subscriptions ====================

    SUBSCRIPTION_PLANS = {
        'decouverte': {'name': 'Découverte', 'price': 0, 'max_properties': 1},
        'proprietaire': {'name': 'Propriétaire', 'price': 9, 'max_properties': 3},
        'gestionnaire': {'name': 'Gestionnaire', 'price': 29, 'max_properties': -1}  # -1 = unlimited
    }

    def get_user_subscription(self, user_id):
        """Get the subscription for a user, create default if not exists"""
        conn = self.get_connection()
        result = conn.execute('SELECT * FROM subscriptions WHERE user_id=?', (user_id,)).fetchone()

        if not result:
            # Create default subscription (Découverte)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO subscriptions (user_id, plan, plan_name, price, max_properties)
                VALUES (?, 'decouverte', 'Découverte', 0, 1)
            ''', (user_id,))
            conn.commit()
            result = conn.execute('SELECT * FROM subscriptions WHERE user_id=?', (user_id,)).fetchone()

        conn.close()
        return dict(result) if result else None

    def update_subscription(self, user_id, plan):
        """Update user subscription to a new plan"""
        if plan not in self.SUBSCRIPTION_PLANS:
            return False

        plan_info = self.SUBSCRIPTION_PLANS[plan]
        conn = self.get_connection()
        cursor = conn.cursor()

        # Check if subscription exists
        cursor.execute('SELECT id FROM subscriptions WHERE user_id=?', (user_id,))
        if cursor.fetchone():
            cursor.execute('''
                UPDATE subscriptions
                SET plan=?, plan_name=?, price=?, max_properties=?, updated_at=CURRENT_TIMESTAMP
                WHERE user_id=?
            ''', (plan, plan_info['name'], plan_info['price'], plan_info['max_properties'], user_id))
        else:
            cursor.execute('''
                INSERT INTO subscriptions (user_id, plan, plan_name, price, max_properties)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, plan, plan_info['name'], plan_info['price'], plan_info['max_properties']))

        conn.commit()
        conn.close()
        return True

    def can_add_property(self, user_id):
        """Check if user can add more properties based on subscription"""
        subscription = self.get_user_subscription(user_id)
        if not subscription:
            return False

        max_props = subscription['max_properties']
        if max_props == -1:  # Unlimited
            return True

        current_count = self.count_user_properties(user_id)
        return current_count < max_props

    def count_user_properties(self, user_id):
        """Count properties for a user"""
        conn = self.get_connection()
        result = conn.execute('SELECT COUNT(*) FROM properties WHERE user_id=?', (user_id,)).fetchone()
        conn.close()
        return result[0] if result else 0

    # ==================== Account Management ====================

    def get_all_user_properties(self, user_id):
        """Get all properties for a user (including inactive) with city"""
        conn = self.get_connection()
        results = conn.execute('''
            SELECT p.*, a.city
            FROM properties p
            LEFT JOIN address a ON p.id = a.property_id
            WHERE p.user_id = ?
            ORDER BY p.display_order
        ''', (user_id,)).fetchall()
        conn.close()
        return [dict(row) for row in results]

    def toggle_property_active(self, property_id, is_active):
        """Toggle property active status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE properties
            SET is_active=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (1 if is_active else 0, property_id))
        conn.commit()
        conn.close()

    def delete_property_with_data(self, property_id):
        """Delete a property and all associated data"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Delete all associated data
        tables = [
            'general_info', 'wifi_config', 'address', 'parking_info',
            'access_info', 'contact_info', 'emergency_numbers', 'nearby_services',
            'activities', 'activity_categories', 'amenities', 'checkout_instructions',
            'photos', 'access_photos'
        ]

        for table in tables:
            cursor.execute(f'DELETE FROM {table} WHERE property_id=?', (property_id,))

        # Delete the property itself
        cursor.execute('DELETE FROM properties WHERE id=?', (property_id,))

        conn.commit()
        conn.close()

    def get_account_info(self, user_id):
        """Get account info for a user"""
        conn = self.get_connection()
        result = conn.execute('''
            SELECT id, email, firstname, lastname, avatar, created_at, updated_at
            FROM users WHERE id=?
        ''', (user_id,)).fetchone()
        conn.close()
        return dict(result) if result else None

    def update_user_avatar(self, user_id, avatar):
        """Update user avatar"""
        conn = self.get_connection()
        conn.execute('''
            UPDATE users SET avatar=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (avatar, user_id))
        conn.commit()
        conn.close()

    def delete_user(self, user_id):
        """Delete a user account"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Delete subscription
        cursor.execute('DELETE FROM subscriptions WHERE user_id=?', (user_id,))

        # Delete the user
        cursor.execute('DELETE FROM users WHERE id=?', (user_id,))

        conn.commit()
        conn.close()
