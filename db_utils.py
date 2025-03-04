import sqlite3
import shutil
import datetime
import schedule
import time
import os
import threading
def create_connection(db_file='passwords.db'):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
    return conn
def setup_db():
    conn = create_connection()
    if conn is not None:
        with conn:
            cursor = conn.cursor()
            # Add last_changed column if it does not exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS passwords (
                    id INTEGER PRIMARY KEY,
                    service TEXT,
                    username TEXT,
                    password TEXT,
                    last_changed DATE DEFAULT (DATE('now'))
                )
            ''')
def add_last_changed_column():
    conn = create_connection()
    if conn is not None:
        try:
            with conn:
                cursor = conn.cursor()
                # Add last_changed column if it does not exist
                cursor.execute('''
                    ALTER TABLE passwords
                    ADD COLUMN last_changed DATE DEFAULT (DATE('now'));
                ''')
        except sqlite3.Error as e:
            print(f"Failed to add last_changed column: {e}")
        finally:
            if conn:
                conn.close()

            
def use_connection(func):
    def wrapper(*args, **kwargs):
        conn = create_connection()
        try:
            with conn:
                return func(conn, *args, **kwargs)
        finally:
            if conn:
                conn.close()
    return wrapper

@use_connection
def store_password(conn, service, username, encrypted_password):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO passwords (service, username, password) VALUES (?, ?, ?)",
                       (service, username, encrypted_password))
    except sqlite3.Error as e:
        print(f"Failed to store password: {e}")


@use_connection
def retrieve_passwords(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, service, username, password FROM passwords")
    return cursor.fetchall()

def update_password(record_id, new_password):
    conn = create_connection()
    if conn is not None:
        with conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE passwords SET password = ? WHERE id = ?", (new_password, record_id))
            conn.commit()

def delete_password(record_id):
    conn = create_connection()
    if conn is not None:
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM passwords WHERE id = ?", (record_id,))
            conn.commit()
def backup_database():
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = f"backups/passwords_backup_{current_time}.db"
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)  # Ensure the backup directory exists
    shutil.copyfile('passwords.db', backup_path)
    print("Database backed up to:", backup_path)

def start_backup_schedule():
    backup_thread = threading.Thread(target=schedule_backups)
    backup_thread.daemon = True
    backup_thread.start()

def restore_database(backup_path):
    try:
        shutil.copyfile(backup_path, 'passwords.db')
        print("Database restored successfully.")
    except IOError as e:
        print(f"Could not restore the database: {e}")
def schedule_backups():
    schedule.every().day.at("01:00").do(backup_database)

    while True:
        schedule.run_pending()
        time.sleep(1)
def check_password_expiry():
    conn = create_connection()
    if conn is not None:
        with conn:
            cursor = conn.cursor()
            # Assuming password expiry is set to 90 days
            cursor.execute("SELECT service FROM passwords WHERE DATE(last_changed) < DATE('now', '-90 days')")
            expired_services = [row[0] for row in cursor.fetchall()]
            return ', '.join(expired_services) if expired_services else None

