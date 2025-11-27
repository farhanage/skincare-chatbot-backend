# app/database/connection.py
import sqlite3
import os
from pathlib import Path

def get_db():
    """
    Get database connection
    """
    # Database path - gunakan folder backend untuk database
    db_path = Path(__file__).parent.parent.parent / "database.db"
    
    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create connection
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    
    return conn

def init_db():
    """
    Initialize database dengan sample data
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL,
            category TEXT,
            image_url TEXT
        )
    ''')
    
    # Insert sample data jika belum ada
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    
    if count == 0:
        sample_products = [
            ('Cetaphil Gentle Skin Cleanser', 'Pembersih wajah lembut untuk kulit sensitif', 125000, 'Cleanser', 'https://example.com/cetaphil.jpg'),
            ('La Roche-Posay Effaclar Duo+', 'Krim untuk acne-prone skin', 250000, 'Acne Treatment', 'https://example.com/laroche.jpg'),
            ('Avoskin Miraculous Refining Toner', 'Toner dengan AHA/BHA untuk eksfoliasi', 180000, 'Toner', 'https://example.com/avoskin.jpg'),
            ('The Ordinary Niacinamide 10% + Zinc 1%', 'Serum untuk minyak berlebih dan pori-pori', 90000, 'Serum', 'https://example.com/ordinary.jpg'),
            ('Skintific 5X Ceramide Barrier Moisture Gel', 'Moisturizer untuk skin barrier repair', 150000, 'Moisturizer', 'https://example.com/skintific.jpg'),
            ('EltaMD UV Clear Tinted Sunscreen', 'Sunscreen untuk kulit sensitif dan berjerawat', 350000, 'Sunscreen', 'https://example.com/eltamd.jpg'),
            ('Hada Labo Gokujyun Premium Lotion', 'Hyaluronic acid lotion untuk hidrasi intensif', 120000, 'Essence', 'https://example.com/hadalabo.jpg'),
            ('Cosrx Advanced Snail 96 Mucin Power Essence', 'Essence dengan 96% snail mucin', 150000, 'Essence', 'https://example.com/cosrx.jpg')
        ]
        
        cursor.executemany('''
            INSERT INTO products (name, description, price, category, image_url)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_products)
        
        print(" Database initialized dengan 8 produk")
    
    conn.commit()
    conn.close()