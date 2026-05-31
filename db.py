import sqlite3

DB_NAME = 'quickbite.db'


def get_conn():
    """Returns a connection to the SQLite database with foreign keys enabled."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def setup_db():
    """Initializes the database schema and seeds initial data if empty."""
    conn = get_conn()
    c = conn.cursor()

    # Creating tables
    c.execute('''CREATE TABLE IF NOT EXISTS menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        stock INTEGER DEFAULT 10,
        is_active INTEGER DEFAULT 1,
        image_path TEXT)''')

    # Migration: Add image_path column if it doesn't exist (for existing DBs)
    try:
        c.execute("ALTER TABLE menu ADD COLUMN image_path TEXT")
    except sqlite3.OperationalError:
        pass # Column already exists

    c.execute('''CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT NOT NULL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id TEXT PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        total_amount REAL NOT NULL,
        payment_method TEXT NOT NULL,
        coupon_used TEXT,
        date_time TEXT NOT NULL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT NOT NULL,
        menu_id INTEGER NOT NULL,
        item_name TEXT,
        quantity INTEGER NOT NULL,
        price_at_order REAL)''')

    try:
        c.execute("ALTER TABLE order_items ADD COLUMN item_name TEXT")
    except sqlite3.OperationalError:
        pass

    c.execute('''CREATE TABLE IF NOT EXISTS coupons (
        code TEXT PRIMARY KEY,
        discount_percentage REAL NOT NULL,
        expires_on TEXT,
        max_uses INTEGER DEFAULT 100,
        used_count INTEGER DEFAULT 0)''')

    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT NOT NULL,
        rating INTEGER,
        comment TEXT,
        review_date TEXT NOT NULL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL)''')

    # Seed Users
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        users = [
            ('admin', 'admin123', 'admin'),
            ('user', 'user123', 'user')
        ]
        c.executemany("INSERT INTO users (username, password, role) VALUES (?,?,?)", users)

    # Creating Views
    c.execute("DROP VIEW IF EXISTS sales_report")
    c.execute('''CREATE VIEW sales_report AS
        SELECT m.item_name, m.category, m.price,
               SUM(oi.quantity) AS total_qty_sold,
               SUM(oi.quantity * oi.price_at_order) AS total_revenue
        FROM order_items oi JOIN menu m ON oi.menu_id = m.id
        GROUP BY m.id ORDER BY total_revenue DESC''')

    # Seed Menu
    c.execute("SELECT COUNT(*) FROM menu")
    if c.fetchone()[0] == 0:
        items = [
            ('Pizza', 'Main Course', 150, 20, 'assets/pizza.png'),
            ('Burger', 'Main Course', 80, 50, 'assets/burger.png'),
            ('Sandwich', 'Snacks', 60, 30, 'assets/sandwich.png'),
            ('Coffee', 'Beverages', 40, 100, 'assets/coffee.png'),
            ('Pasta', 'Main Course', 120, 15, 'assets/pasta.png'),
            ('French Fries', 'Snacks', 50, 40, 'assets/fries.png'),
            ('Cold Drink', 'Beverages', 30, 60, 'assets/drink.png'),
            ('Cheesecake', 'Desserts', 90, 10, 'assets/cheesecake.png')]
        c.executemany("INSERT INTO menu (item_name, category, price, stock, image_path) VALUES (?,?,?,?,?)", items)
    else:
        # Update existing items with default paths if they are empty
        default_images = {
            'Pizza': 'assets/pizza.png',
            'Burger': 'assets/burger.png',
            'Sandwich': 'assets/sandwich.png',
            'Coffee': 'assets/coffee.png',
            'Pasta': 'assets/pasta.png',
            'French Fries': 'assets/fries.png',
            'Cold Drink': 'assets/drink.png',
            'Cheesecake': 'assets/cheesecake.png'
        }
        for name, path in default_images.items():
            c.execute("UPDATE menu SET image_path = ? WHERE item_name = ? AND (image_path IS NULL OR image_path = '')", (path, name))

    # Seed Coupons
    c.execute("SELECT COUNT(*) FROM coupons")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO coupons (code, discount_percentage, expires_on) VALUES (?,?,?)",
                      [('SAVE10', 10, '2026-12-31'), ('SAVE20', 20, '2026-12-31')])

    conn.commit()
    conn.close()
