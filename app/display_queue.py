from pathlib import Path
import sqlite3
import threading
import queue
import random
import time
import logging
import subprocess
from datetime import datetime

logger = logging.getLogger(__name__)

class DisplayQueue:
    def __init__(self, app_config):
        self.config = app_config
        self.base_dir = Path(__file__).resolve().parent.parent
        self.db_path = self.base_dir / "photos" / "queue.db"
        self.process_queue = queue.Queue()
        
        # Time settings for display rotation (in seconds)
        self.min_display_time = 8 * 3600  # 8 hours
        self.max_display_time = 12 * 3600  # 12 hours
        
        self.init_db()
        self.start_background_tasks()
    
    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS display_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    converted BOOLEAN DEFAULT 0,
                    last_displayed TIMESTAMP,
                    display_count INTEGER DEFAULT 0
                )
            ''')
    
    def convert_image(self, input_path, output_path):
        """Convert image using convert.py script"""
        try:
            subprocess.run(
                ['python', self.base_dir / 'convert.py', input_path, output_path], 
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Conversion failed: {e}")
            return False

    def display_image(self, image_path):
        """Display image using display_img.py script"""
        try:
            subprocess.run(
                ['python', self.base_dir / 'display_img.py', image_path], 
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Display failed: {e}")
            return False

    def process_queue_worker(self):
        """Background worker to process the upload queue"""
        while True:
            try:
                file_id = self.process_queue.get()
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT filename FROM display_queue WHERE id = ?", (file_id,))
                    filename = cursor.fetchone()[0]
                    
                    input_path = self.base_dir / "photos" / "originals" / filename
                    output_path = self.base_dir / "photos" / "display" / f"{Path(filename).stem}.bmp"
                    
                    if self.convert_image(input_path, output_path):
                        cursor.execute(
                            "UPDATE display_queue SET converted = 1 WHERE id = ?",
                            (file_id,)
                        )
                        conn.commit()
                        logger.info(f"Converted {filename} successfully")
                    
                self.process_queue.task_done()
            except Exception as e:
                logger.error(f"Error in queue processing: {e}")
                continue

    def display_manager(self):
        """Manage the display rotation of images"""
        while True:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT id, filename 
                        FROM display_queue 
                        WHERE converted = 1 
                        ORDER BY display_count, last_displayed
                        LIMIT 1
                    """)
                    result = cursor.fetchone()
                    
                    if result:
                        photo_id, filename = result
                        bmp_path = self.base_dir / "photos" / "display" / f"{Path(filename).stem}.bmp"
                        
                        if self.display_image(bmp_path):
                            cursor.execute("""
                                UPDATE display_queue 
                                SET display_count = display_count + 1,
                                    last_displayed = CURRENT_TIMESTAMP 
                                WHERE id = ?
                            """, (photo_id,))
                            conn.commit()
                            
                            sleep_time = random.uniform(self.min_display_time, self.max_display_time)
                            time.sleep(sleep_time)
                        else:
                            time.sleep(60)
                    else:
                        time.sleep(60)
                        
            except Exception as e:
                logger.error(f"Error in display manager: {e}")
                time.sleep(60)

    def add_to_queue(self, filename):
        """Add a new file to the display queue"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO display_queue (filename) VALUES (?)",
                    (filename,)
                )
                file_id = cursor.lastrowid
                conn.commit()
            
            self.process_queue.put(file_id)
            return True
        except Exception as e:
            logger.error(f"Error adding to queue: {e}")
            return False

    def get_queue_status(self):
        """Get current status of the display queue"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN converted = 1 THEN 1 ELSE 0 END) as converted,
                        MAX(last_displayed) as last_display
                    FROM display_queue
                """)
                total, converted, last_display = cursor.fetchone()
                
                return {
                    'total_photos': total,
                    'converted_photos': converted,
                    'last_display': last_display,
                    'queue_size': self.process_queue.qsize()
                }
        except Exception as e:
            logger.error(f"Error getting queue status: {e}")
            return None

    def start_background_tasks(self):
        """Start the background processing threads"""
        queue_thread = threading.Thread(target=self.process_queue_worker, daemon=True)
        queue_thread.start()
        
        display_thread = threading.Thread(target=self.display_manager, daemon=True)
        display_thread.start()
