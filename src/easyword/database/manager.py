import sqlite3
import os
import json
import uuid
from .schema import INIT_STATEMENTS

class DatabaseManager:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.db_path = None
        return cls._instance

    def init_db(self, data_path):
        """Initialize database connection and create tables"""
        # Ensure path is a string, Toga paths might be Path objects
        data_path = str(data_path)
        
        if not os.path.exists(data_path):
            try:
                os.makedirs(data_path)
            except OSError as e:
                print(f"Error creating data directory: {e}")
                # Fallback to internal storage or temp if needed, but usually app data path is writable
                pass
            
        self.db_path = os.path.join(data_path, 'easyword.db')
        print(f"Database path: {self.db_path}")
        
        # Create tables
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                for statement in INIT_STATEMENTS:
                    cursor.execute(statement)
                
                # Check for schema updates (Migration)
                # 1. Check if 'libraries' table exists, if not, schema created it above
                # 2. Check if 'words' table has 'library_id' column
                try:
                    cursor.execute("SELECT library_id FROM words LIMIT 1")
                except sqlite3.OperationalError:
                    print("Migrating: Adding library_id to words table")
                    # Add column
                    try:
                        cursor.execute("ALTER TABLE words ADD COLUMN library_id INTEGER DEFAULT 1 REFERENCES libraries(id)")
                    except sqlite3.OperationalError as e:
                        print(f"Migration error (add column): {e}")
                    
                    # Add unique constraint? SQLite ALTER TABLE is limited.
                    # It's hard to add UNIQUE(library_id, word) to existing table without recreating.
                    # For now, we just add the column to make it work.
                    # Ideally we should recreate the table, but that risks data loss.
                    # Let's just add the column so the app doesn't crash.

                # 2. uid
                try:
                    cursor.execute("SELECT uid FROM words LIMIT 1")
                except sqlite3.OperationalError:
                    print("Migrating: Adding uid to words table")
                    try:
                        # SQLite does not support adding UNIQUE constraints via ALTER TABLE ADD COLUMN
                        # We must add column first, then populate, then ideally recreate table to enforce unique
                        # For simplicity/safety, we add column without UNIQUE constraint first, or ignore error if strict
                        # Actually, just adding TEXT is fine, we enforce uniqueness in logic or future inserts
                        cursor.execute("ALTER TABLE words ADD COLUMN uid TEXT")
                        
                        # Backfill existing words with UUIDs
                        cursor.execute("SELECT id FROM words WHERE uid IS NULL")
                        ids = cursor.fetchall()
                        for row in ids:
                            new_uid = str(uuid.uuid4())
                            cursor.execute("UPDATE words SET uid = ? WHERE id = ?", (new_uid, row[0]))
                            
                        # If we really want unique index:
                        try:
                            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_words_uid ON words(uid)")
                        except Exception as e:
                            print(f"Index creation error: {e}")
                            
                    except sqlite3.OperationalError as e:
                        print(f"Migration error (add uid): {e}")
                
                conn.commit()
        except Exception as e:
            print(f"Database initialization error: {e}")
            raise

    def get_connection(self):
        """Get a connection to the SQLite database"""
        if not self.db_path:
            raise ValueError("Database not initialized. Call init_db() first.")
        return sqlite3.connect(self.db_path)

    # --- Library Management ---

    def create_library(self, name, description=""):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO libraries (name, description) VALUES (?, ?)
                """, (name, description))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_libraries(self):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM libraries ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_library_word_count(self, library_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM words WHERE library_id = ?", (library_id,))
            return cursor.fetchone()[0]

    # --- Word Management ---
    
    def add_word(self, word, definition_cn, phonetic="", definition_en="", example="", category="General", library_id=1):
        try:
            new_uid = str(uuid.uuid4())
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO words (uid, library_id, word, definition_cn, phonetic, definition_en, example, category)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (new_uid, library_id, word, definition_cn, phonetic, definition_en, example, category))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Word already exists in this library
            return None
        except Exception as e:
            print(f"Database Error in add_word: {e}")
            return None

    def get_words_by_library(self, library_id, search_query=None):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if search_query:
                query = "SELECT * FROM words WHERE library_id = ? AND word LIKE ? ORDER BY word ASC"
                cursor.execute(query, (library_id, f"%{search_query}%"))
            else:
                query = "SELECT * FROM words WHERE library_id = ? ORDER BY word ASC"
                cursor.execute(query, (library_id,))
            return [dict(row) for row in cursor.fetchall()]

    def search_libraries(self, query):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            sql = "SELECT * FROM libraries WHERE name LIKE ? ORDER BY created_at DESC"
            cursor.execute(sql, (f"%{query}%",))
            return [dict(row) for row in cursor.fetchall()]

    def get_all_words(self):
        # Default to library 1 for backward compatibility if needed, or get all
        # For now, let's just return all words from all libraries for simple stats
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM words ORDER BY word ASC")
            return [dict(row) for row in cursor.fetchall()]

    def update_word(self, word_id, word, definition_cn, phonetic, definition_en, example, category):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE words 
                SET word = ?, definition_cn = ?, phonetic = ?, definition_en = ?, example = ?, category = ?
                WHERE id = ?
            """, (word, definition_cn, phonetic, definition_en, example, category, word_id))
            conn.commit()
            return cursor.rowcount > 0

    def delete_words(self, word_ids):
        if not word_ids:
            return False
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Dynamic placeholder generation
            placeholders = ','.join('?' * len(word_ids))
            sql = f"DELETE FROM words WHERE id IN ({placeholders})"
            cursor.execute(sql, word_ids)
            conn.commit()
            return cursor.rowcount > 0

    def get_word_count(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM words")
            return cursor.fetchone()[0]

db_manager = DatabaseManager()
