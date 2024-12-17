from PIL import Image
import argparse

def convert_for_eink(input_path, output_path):
    img = Image.open(input_path).convert('L')
    img.thumbnail((800, 480), Image.Resampling.LANCZOS)

    new_img = Image.new('L', (800, 480), 'white')

    x = (800 - img.width) // 2
    y = (480 - img.height) // 2
    new_img.paste(img, (x, y))
    new_img = new_img.convert('1')
    new_img.save(output_path, 'BMP')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input image")
    parser.add_argument("output", help="Output BMP image")
    args = parser.parse_args()

    convert_for_eink(args.input, args.output)
