import sqlite3
db = sqlite3.connect('quickbite.db')
cursor = db.cursor()
cursor.execute("SELECT id, item_name, image_path FROM menu WHERE item_name LIKE '%Cake%'")
print("Before:", cursor.fetchall())

# Fix all cases where item_name contains "Cake" but isn't "Cheesecake"
cursor.execute("UPDATE menu SET image_path='assets/cake.png' WHERE item_name LIKE '%Cake%' AND item_name != 'Cheesecake'")
db.commit()

cursor.execute("SELECT id, item_name, image_path FROM menu WHERE item_name LIKE '%Cake%'")
print("After:", cursor.fetchall())
db.close()
