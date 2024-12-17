# app/converter.py
import os
from PIL import Image
import logging
from pathlib import Path
import time

class PhotoConverter:
    def __init__(self, config):
        self.originals_dir = Path(config['paths']['originals'])
        self.display_dir = Path(config['paths']['display'])
        self.display_width = config['display']['width']
        self.display_height = config['display']['height']
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('PhotoConverter')

    def convert_photo(self, filename: str) -> bool:
        """Convert a single photo to e-ink display format"""
        try:
            input_path = self.originals_dir / filename
            output_path = self.display_dir / f"converted_{filename}"
            
            # Open and convert image
            with Image.open(input_path) as img:
                # Convert to grayscale
                img_gray = img.convert('L')
                
                # Resize maintaining aspect ratio
                img_gray.thumbnail((self.display_width, self.display_height))
                
                # Apply dithering for better e-ink display
                img_dither = img_gray.convert('1', dither=Image.FLOYDSTEINBERG)
                
                # Save converted image
                img_dither.save(output_path)
                
            self.logger.info(f"Successfully converted {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error converting {filename}: {str(e)}")
            return False

    def process_new_photos(self):
        """Check for and convert any new photos"""
        # Get list of files already converted
        converted = {p.name.replace('converted_', '') for p in self.display_dir.glob('converted_*')}
        
        # Check originals directory for new files
        for photo_path in self.originals_dir.glob('*'):
            if photo_path.name not in converted:
                self.convert_photo(photo_path.name)

    def run_conversion_loop(self, check_interval: int = 30):
        """Run continuous conversion process"""
        self.logger.info("Starting photo conversion monitoring...")
        while True:
            self.process_new_photos()
            time.sleep(check_interval)

def main():
    # For testing/direct execution
    from config import load_config
    config = load_config()
    converter = PhotoConverter(config)
    converter.run_conversion_loop()

if __name__ == "__main__":
    main()
