import sys
import os
# TODO: add necessary lib files to config as a submodule
# or as standalone code (or rewrite)
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5_V2
import time
from PIL import Image
import argparse

logging.basicConfig(level=logging.INFO)


def display_image(image_path):
    try:
        # init display
        logging.info("Initializing display...")
        epd = epd7in5_V2.EPD()
        epd.init()
        epd.Clear()

        logging.info(f"Displaying image: {image_path}")
        image = Image.open(image_path)
        epd.display(epd.getbuffer(image))
        logging.info("Putting display to sleep...")
        epd.sleep()

    except Exception as e:
        logging.error(f"Error: {e}")
        if 'epd' in locals():
            epd7in5_V2.epdconfig.module_exit(cleanup=True)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Display img on e-Paper")
    parser.add_argument('image', help="Image file to display")
    args = parser.parse_args()
