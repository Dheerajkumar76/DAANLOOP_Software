"""
DAANLOOP Database Module
========================

Handles SQLite3 connection and schema initialization.
"""

import sqlite3
from config import Config


def get_db():
    """Get a database connection with row factory."""
    db = sqlite3.connect(Config.DATABASE)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def close_db(db):
    """Close a database connection."""
    if db:
        db.close()


def init_db():
    """Initialize all database tables."""
    db = get_db()
    cursor = db.cursor()

    # — Sprint 1 Tables —

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user' CHECK(role IN ('user', 'admin')),
            city TEXT DEFAULT '',
            avatar TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            city TEXT NOT NULL,
            location TEXT DEFAULT '',
            condition TEXT DEFAULT 'Good',
            contact_number TEXT DEFAULT '',
            image_path TEXT DEFAULT '',
            owner_id INTEGER NOT NULL,
            status TEXT DEFAULT 'active' CHECK(status IN ('active','soft_deleted','claimed')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users(id)
        )
    ''')

    # — Sprint 2 Tables —

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            listing_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (listing_id) REFERENCES listings(id),
            UNIQUE(user_id, listing_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rater_id INTEGER NOT NULL,
            rated_user_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            review TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (rater_id) REFERENCES users(id),
            FOREIGN KEY (rated_user_id) REFERENCES users(id),
            UNIQUE(rater_id, rated_user_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reporter_id INTEGER NOT NULL,
            listing_id INTEGER NOT NULL,
            reason TEXT NOT NULL,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending','reviewed','dismissed')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (reporter_id) REFERENCES users(id),
            FOREIGN KEY (listing_id) REFERENCES listings(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            details TEXT DEFAULT '',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # — Sprint 3 Tables —

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            listing_id INTEGER NOT NULL,
            message_text TEXT NOT NULL,
            reply_text TEXT DEFAULT '',
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            replied_at TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id),
            FOREIGN KEY (listing_id) REFERENCES listings(id)
        )
    ''')

    db.commit()
    close_db(db)
    print("[DB] All tables initialized successfully.")


def seed_demo_data():
    """Insert demo/admin user if not exists."""
    from utils.security import hash_password

    db = get_db()
    cursor = db.cursor()

    # Check if admin exists
    cursor.execute("SELECT id FROM users WHERE username = ?", ('admin',))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, city)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@daanloop.com', hash_password('admin123'), 'admin', 'Mumbai'))
        print("[DB] Admin user created (admin / admin123)")

    # Check if demo user exists
    cursor.execute("SELECT id FROM users WHERE username = ?", ('demo',))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, city)
            VALUES (?, ?, ?, ?, ?)
        ''', ('demo', 'demo@daanloop.com', hash_password('demo123'), 'user', 'Delhi'))
        print("[DB] Demo user created (demo / demo123)")

    # Seed some demo listings
    cursor.execute("SELECT COUNT(*) as cnt FROM listings")
    count = cursor.fetchone()['cnt']

    if count == 0:
        demo_listings = [
            ('Wooden Bookshelf', 'Solid wood bookshelf in great condition. 5 shelves.', 'Furniture', 'Mumbai', 'Bandra West, near Carter Road', 'Good', '9876543210', '', 1),
            ('Python Programming Book', 'Learn Python the hard way. Barely used.', 'Books', 'Delhi', 'Connaught Place, Block C', 'Like New', '9123456789', '', 2),
            ('Kids Bicycle', 'Suitable for ages 5-8. Minor scratches.', 'Sports', 'Bangalore', 'Koramangala, 5th Block', 'Fair', '9988776655', '', 2),
            ('Office Chair', 'Ergonomic office chair with lumbar support.', 'Furniture', 'Mumbai', 'Andheri East, Marol', 'Good', '9876543210', '', 1),
            ('Samsung Galaxy S20', 'Old phone, works perfectly. Factory reset done.', 'Electronics', 'Chennai', 'Anna Nagar, 2nd Avenue', 'Good', '9445566778', '', 2),
            ('Winter Jacket', 'Size L, barely worn. Perfect for cold weather.', 'Clothing', 'Delhi', 'Lajpat Nagar, Market 2', 'Like New', '9876543210', '', 1)
        ]

        for item in demo_listings:
            cursor.execute('''
                INSERT INTO listings (title, description, category, city, location, condition, contact_number, image_path, owner_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', item)

        print(f"[DB] {len(demo_listings)} demo listings created.")

    db.commit()
    close_db(db)


if __name__ == "__main__":
    init_db()
    seed_demo_data()
    print("[DB] Database setup complete!")
