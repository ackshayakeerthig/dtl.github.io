import sqlite3

# Initialize the database
def initialize_db():
    conn = sqlite3.connect('instance/donor_data.db')
    cursor = conn.cursor()

    # Create table for users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        category TEXT NOT NULL CHECK(category IN ('individual', 'orphanage', 'fashiondesigner')),
        emailid TEXT UNIQUE NOT NULL,
        phone_number TEXT
    )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_db()