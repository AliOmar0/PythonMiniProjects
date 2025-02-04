#!/usr/bin/env python3
import argparse
from PIL import Image
import sys
import os

# ASCII characters used for the conversion (from darkest to lightest)
ASCII_CHARS = "@%#*+=-:. "

def resize_image(image, new_width=100):
    """Resize image to fit the specified width while maintaining aspect ratio."""
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width * 0.55)  # Compensate for terminal font spacing
    return image.resize((new_width, new_height))

def to_grayscale(image):
    """Convert image to grayscale."""
    return image.convert("L")

def pixels_to_ascii(image):
    """Convert pixels to ASCII characters based on brightness."""
    pixels = image.getdata()
    ascii_str = ""
    for pixel in pixels:
        # Map pixel brightness (0-255) to ASCII characters
        ascii_str += ASCII_CHARS[pixel * len(ASCII_CHARS) // 256]
    return ascii_str

def image_to_ascii(image_path, width=100, save_file=None):
    """Convert image to ASCII art."""
    try:
        # Open image
        image = Image.open(image_path)
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    # Convert image to ASCII
    image = resize_image(image, width)
    image = to_grayscale(image)
    
    ascii_str = pixels_to_ascii(image)
    
    # Split the string based on width to create image rows
    img_width = image.width
    ascii_str_len = len(ascii_str)
    ascii_img = ""
    
    # Format the ASCII string into lines
    for i in range(0, ascii_str_len, img_width):
        ascii_img += ascii_str[i:i + img_width] + "\n"
    
    # Print or save the result
    if save_file:
        try:
            with open(save_file, 'w') as f:
                f.write(ascii_img)
            print(f"ASCII art saved to {save_file}")
        except Exception as e:
            print(f"Error saving file: {e}")
    
    return ascii_img

def main():
    parser = argparse.ArgumentParser(description="Convert images to ASCII art.")
    parser.add_argument("image_path", help="Path to the image file")
    parser.add_argument("--width", type=int, default=100, help="Width of ASCII art output (default: 100)")
    parser.add_argument("--save", help="Save the ASCII art to a text file")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.image_path):
        print(f"Error: Image file '{args.image_path}' not found")
        sys.exit(1)
    
    ascii_art = image_to_ascii(args.image_path, args.width, args.save)
    if ascii_art:
        print(ascii_art)

if __name__ == "__main__":
    main() 