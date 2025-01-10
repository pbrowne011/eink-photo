import sqlite3
from pathlib import Path
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, app_config):
        self.config = app_config
        self.db_path = Path("photos/photos.db")
        self.init_db()

    @contextmanager
    def get_db(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def init_db(self):
        """Initialize database schema"""
        with self.get_db() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS photos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL UNIQUE,
                    original_path TEXT NOT NULL,
                    display_path TEXT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    converted BOOLEAN DEFAULT 0,
                    last_displayed TIMESTAMP,
                    display_count INTEGER DEFAULT 0
                )
            ''')
            logger.info("Initialized database")

    def add_photo(self, filename, original_path):
        """Add a new photo to the database"""
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO photos (filename, original_path)
                    VALUES (?, ?)
                ''', (filename, str(original_path)))
                photo_id = cursor.lastrowid
                logger.info(f"Added photo {filename} to database")
                return photo_id
        except sqlite3.IntegrityError:
            logger.error(f"Photo {filename} already exists")
            return None
        except Exception as e:
            logger.error(f"Error adding photo: {e}")
            return None

    def get_photo(self, photo_id=None, filename=None):
        """Get photo by ID or filename"""
        with self.get_db() as conn:
            cursor = conn.cursor()
            if photo_id:
                cursor.execute("SELECT * FROM photos WHERE id = ?", (photo_id,))
            elif filename:
                cursor.execute("SELECT * FROM photos WHERE filename = ?", (filename,))
            else:
                return None
            return dict(cursor.fetchone()) if cursor.fetchone() else None

    def list_photos(self):
        """List all photos"""
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM photos ORDER BY uploaded_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_next_unconverted_photo(self):
        """Get next photo that needs conversion"""
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM photos 
                WHERE converted = 0 
                ORDER BY uploaded_at ASC 
                LIMIT 1
            ''')
            result = cursor.fetchone()
            return dict(result) if result else None

    def get_next_display_photo(self):
        """Get next photo for display based on display count and time"""
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM photos 
                WHERE converted = 1 
                ORDER BY display_count ASC, last_displayed ASC NULLS FIRST
                LIMIT 1
            ''')
            result = cursor.fetchone()
            return dict(result) if result else None

    def update_photo_display(self, photo_id):
        """Update photo display count and timestamp"""
        with self.get_db() as conn:
            conn.execute('''
                UPDATE photos 
                SET display_count = display_count + 1,
                    last_displayed = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (photo_id,))
            logger.info(f"Updated display count for photo {photo_id}")

    def update_photo_converted(self, photo_id, display_path):
        """Mark photo as converted and store display path"""
        with self.get_db() as conn:
            conn.execute('''
                UPDATE photos 
                SET converted = 1,
                    display_path = ?
                WHERE id = ?
            ''', (str(display_path), photo_id))
            logger.info(f"Marked photo {photo_id} as converted")

    def delete_photo(self, photo_id=None, filename=None):
        """Delete photo from database"""
        with self.get_db() as conn:
            cursor = conn.cursor()
            if photo_id:
                cursor.execute("DELETE FROM photos WHERE id = ?", (photo_id,))
            elif filename:
                cursor.execute("DELETE FROM photos WHERE filename = ?", (filename,))
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Deleted photo {photo_id or filename}")
            return success

    def get_queue_stats(self):
        """Get statistics about the photo queue"""
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN converted = 1 THEN 1 ELSE 0 END) as converted,
                    MAX(last_displayed) as last_display
                FROM photos
            ''')
            result = cursor.fetchone()
            return {
                'total_photos': result[0],
                'converted_photos': result[1],
                'last_display': result[2]
            }
