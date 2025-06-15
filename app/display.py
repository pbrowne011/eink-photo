import logging
from pathlib import Path
from .waveshare_utils import convert_for_display, display_image

logger = logging.getLogger(__name__)

class DisplayController:
    def __init__(self, app_config):
        self.config = app_config
        self.photos_dir = Path("photos")
        self.originals_dir = self.photos_dir / "originals"
        self.display_dir = self.photos_dir / "display"
        
        # Ensure directories exist
        self.display_dir.mkdir(parents=True, exist_ok=True)
    
    def convert_photo(self, filename):
        """Convert a single photo from originals to display format"""
        try:
            input_path = self.originals_dir / filename
            if not input_path.exists():
                logger.error(f"Original photo not found: {filename}")
                return False
                
            output_path = self.display_dir / f"{input_path.stem}.bmp"
            
            if convert_for_display(input_path, output_path, self.config):
                logger.info(f"Converted {filename} successfully")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error converting photo {filename}: {e}")
            return False

    def display_photo(self, filename):
        """Display a specific photo"""
        try:
            # Check if display version exists, if not convert it
            display_path = self.display_dir / f"{Path(filename).stem}.bmp"
            
            if not display_path.exists():
                if not self.convert_photo(filename):
                    return False
            
            if display_image(display_path):
                logger.info(f"Displayed {filename}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error displaying photo {filename}: {e}")
            return False

    def get_available_photos(self):
        """Get list of available photos in originals directory"""
        try:
            photos = []
            for file_path in self.originals_dir.glob("*"):
                if file_path.is_file() and file_path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.heif', '.heic', '.bmp', '.pdf'}:
                    display_path = self.display_dir / f"{file_path.stem}.bmp"
                    photos.append({
                        'filename': file_path.name,
                        'converted': display_path.exists()
                    })
            return photos
        except Exception as e:
            logger.error(f"Error getting available photos: {e}")
            return []

    def get_status(self):
        """Get current status"""
        try:
            photos = self.get_available_photos()
            return {
                'total_photos': len(photos),
                'converted_photos': sum(1 for p in photos if p['converted']),
                'photos': photos
            }
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return None
