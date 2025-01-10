import threading
import queue
import random
import time
import logging
from pathlib import Path
from .waveshare_utils import convert_for_display, display_image
from .database import Database

logger = logging.getLogger(__name__)

class DisplayController:
    def __init__(self, app_config):
        self.config = app_config
        self.db = Database(app_config)
        self.process_queue = queue.Queue()
        
        # Time settings for display rotation (in seconds)
        self.min_display_time = 8 * 3600  # 8 hours
        self.max_display_time = 12 * 3600  # 12 hours
        
        # Start background tasks
        self.start_display_thread()
    
    def convert_next_photo(self):
        """Convert next unconverted photo in queue"""
        try:
            # Get next unconverted photo from DB
            photo = self.db.get_next_unconverted_photo()
            if not photo:
                return False
                
            input_path = Path(photo['original_path'])
            output_path = Path("photos/display") / f"{input_path.stem}.bmp"
            
            if convert_for_display(input_path, output_path, self.config):
                self.db.update_photo_converted(photo['id'], str(output_path))
                logger.info(f"Converted {photo['filename']} successfully")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error converting photo: {e}")
            return False

    def display_next_photo(self):
        """Display next photo in rotation"""
        try:
            photo = self.db.get_next_display_photo()
            if not photo:
                logger.info("No photos available to display")
                return False
            
            if display_image(photo['display_path']):
                self.db.update_photo_display(photo['id'])
                logger.info(f"Displayed {photo['filename']}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error displaying photo: {e}")
            return False

    def display_manager(self):
        """Main display loop"""
        while True:
            try:
                # Convert any unconverted photos
                while self.convert_next_photo():
                    pass
                
                # Display next photo
                if self.display_next_photo():
                    # Wait random time before next display
                    sleep_time = random.uniform(
                        self.min_display_time,
                        self.max_display_time
                    )
                    logger.info(f"Sleeping for {sleep_time/3600:.1f} hours")
                    time.sleep(sleep_time)
                else:
                    # No photos to display, check again in a minute
                    time.sleep(60)
                    
            except Exception as e:
                logger.error(f"Error in display manager: {e}")
                time.sleep(60)  # Wait a bit before retrying

    def start_display_thread(self):
        """Start the background display thread"""
        display_thread = threading.Thread(
            target=self.display_manager,
            daemon=True
        )
        display_thread.start()
        logger.info("Started display manager thread")

    def get_status(self):
        """Get current display queue status"""
        try:
            return {
                'queue_size': self.process_queue.qsize(),
                'photos': self.db.get_queue_stats()
            }
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return None
