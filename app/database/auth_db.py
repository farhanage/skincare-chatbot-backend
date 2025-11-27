# app/database/auth_db.py
import sqlite3
import hashlib
import secrets
from typing import Optional, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Use absolute path relative to backend folder
from pathlib import Path
DB_DIR = Path(__file__).parent.parent.parent
DB_PATH = DB_DIR / "users.db"

def init_auth_db():
    """Initialize authentication database"""
    # Ensure directory exists
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'user',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    # Add role column if not exists (for existing databases)
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN role TEXT DEFAULT "user"')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Shopping cart table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            added_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_price REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Order items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info(" Auth database initialized")

def hash_password(password: str) -> str:
    """Hash password with SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username: str, email: str, password: str, full_name: str = "") -> Dict:
    """Create new user"""
    try:
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, role, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, email, password_hash, full_name, 'user', now, now))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "user_id": user_id,
            "username": username,
            "email": email,
            "full_name": full_name
        }
    except sqlite3.IntegrityError as e:
        return {"success": False, "error": "Username atau email sudah terdaftar"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def verify_user(username: str, password: str) -> Optional[Dict]:
    """Verify user credentials"""
    try:
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        
        cursor.execute('''
            SELECT id, username, email, full_name, role FROM users
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "full_name": user[3],
                "role": user[4] if len(user) > 4 else "user"
            }
        return None
    except Exception as e:
        logger.error(f"Verify user error: {e}")
        return None

def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    try:
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, full_name, role FROM users
            WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "full_name": user[3],
                "role": user[4] if len(user) > 4 else "user"
            }
        return None
    except Exception as e:
        logger.error(f"Get user error: {e}")
        return None

# Cart functions
def add_to_cart(user_id: int, product_id: str, quantity: int = 1) -> Dict:
    """Add product to cart"""
    try:
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        cursor = conn.cursor()
        
        # Check if item already in cart
        cursor.execute('''
            SELECT id, quantity FROM cart_items
            WHERE user_id = ? AND product_id = ?
        ''', (user_id, product_id))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update quantity
            new_quantity = existing[1] + quantity
            cursor.execute('''
                UPDATE cart_items SET quantity = ?
                WHERE id = ?
            ''', (new_quantity, existing[0]))
        else:
            # Insert new item
            now = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO cart_items (user_id, product_id, quantity, added_at)
                VALUES (?, ?, ?, ?)
            ''', (user_id, product_id, quantity, now))
        
        conn.commit()
        conn.close()
        return {"success": True, "message": "Produk ditambahkan ke keranjang"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_cart_items(user_id: int) -> list:
    """Get user's cart items"""
    try:
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT product_id, quantity, added_at
            FROM cart_items
            WHERE user_id = ?
            ORDER BY added_at DESC
        ''', (user_id,))
        
        items = cursor.fetchall()
        conn.close()
        
        return [
            {
                "product_id": item[0],
                "quantity": item[1],
                "added_at": item[2]
            }
            for item in items
        ]
    except Exception as e:
        logger.error(f"Get cart error: {e}")
        return []

def update_cart_item(user_id: int, product_id: str, quantity: int) -> Dict:
    """Update cart item quantity"""
    try:
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        cursor = conn.cursor()
        
        if quantity <= 0:
            # Remove item if quantity is 0 or negative
            cursor.execute('''
                DELETE FROM cart_items
                WHERE user_id = ? AND product_id = ?
            ''', (user_id, product_id))
        else:
            cursor.execute('''
                UPDATE cart_items SET quantity = ?
                WHERE user_id = ? AND product_id = ?
            ''', (quantity, user_id, product_id))
        
        conn.commit()
        conn.close()
        return {"success": True, "message": "Keranjang diperbarui"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def clear_cart(user_id: int) -> Dict:
    """Clear user's cart"""
    try:
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM cart_items WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        return {"success": True, "message": "Keranjang dikosongkan"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_admin_if_not_exists():
    """Create default admin account if not exists"""
    try:
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        cursor = conn.cursor()
        
        # Check if admin exists
        cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
        if cursor.fetchone():
            logger.info("Admin account already exists")
            conn.close()
            return
        
        # Create admin
        password_hash = hash_password('admin')
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, role, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('admin', 'admin@skincare.com', password_hash, 'Administrator', 'admin', now, now))
        
        conn.commit()
        conn.close()
        logger.info("✅ Admin account created (username: admin, password: admin)")
    except Exception as e:
        logger.error(f"Failed to create admin: {e}")

# Initialize database on import
init_auth_db()
create_admin_if_not_exists()
