from PIL import Image
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Feature flag for hardware display - set to False for development/testing
ENABLE_HARDWARE_DISPLAY = os.getenv('ENABLE_HARDWARE_DISPLAY', 'false').lower() == 'true'

def convert_for_display(input_path, output_path, config=None):
    """Convert an image file to BMP format suitable for e-ink display."""
    try:
        img = Image.open(input_path).convert('L')
        
        # TODO: Use config for orientation
        target_size = (800, 480)  # Default to landscape
        
        img.thumbnail(target_size, Image.Resampling.LANCZOS)
        new_img = Image.new('L', target_size, 'white')
        
        # Center the image
        x = (target_size[0] - img.width) // 2
        y = (target_size[1] - img.height) // 2
        new_img.paste(img, (x, y))
        
        # Convert to 1-bit color for e-ink
        # TODO: save this image to database, not filesystem with output_path
        new_img = new_img.convert('1')
        new_img.save(output_path, 'BMP')
        
        return True
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        return False

def display_image(image_path):
    """Display an image on the e-ink display."""
    try:
        if not ENABLE_HARDWARE_DISPLAY:
            logger.info(f"MOCK: Would display image: {image_path}")
            return True
            
        # Hardware display code (only runs on Pi with ENABLE_HARDWARE_DISPLAY=true)
        from waveshare_epd import epd7in5_V2
        logger.info("Initializing display...")
        epd = epd7in5_V2.EPD()
        epd.init()
        epd.Clear()

        logger.info(f"Displaying image: {image_path}")
        image = Image.open(image_path)
        epd.display(epd.getbuffer(image))
        
        logger.info("Putting display to sleep...")
        epd.sleep()
        return True
        
    except Exception as e:
        logger.error(f"Display error: {e}")
        return False
