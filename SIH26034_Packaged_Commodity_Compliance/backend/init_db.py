"""
Run this once (or every time — it's idempotent) to create the SQLite
database, tables, and demo login accounts.

Usage:  python init_db.py
"""
from database.db import init_db, get_connection
from auth.auth import hash_password


def seed_demo_users():
    conn = get_connection()
    cur = conn.cursor()

    demo_users = [
        ("admin", "admin123", "System Administrator", "admin"),
        ("officer1", "officer123", "Inspection Officer - R. Sharma", "officer"),
    ]

    for username, password, full_name, role in demo_users:
        existing = cur.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if existing is None:
            cur.execute(
                "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                (username, hash_password(password), full_name, role),
            )
            print(f"Created demo user: {username} / {password} (role: {role})")
        else:
            print(f"Demo user already exists: {username}")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    print("Initializing database schema...")
    init_db()
    print("Seeding demo accounts...")
    seed_demo_users()
    print("\nDone. Demo login credentials:")
    print("  Admin:    admin / admin123")
    print("  Officer:  officer1 / officer123")
