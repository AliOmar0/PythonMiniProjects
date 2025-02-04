# ASCII Art Generator

This Python program converts images into ASCII art. It takes an image file as input and generates a text-based representation of the image using ASCII characters.

## Requirements
- Python 3.x
- Pillow (PIL) library

## Installation
1. Clone this repository
2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage
Run the program with:
```bash
python ascii_art.py path/to/your/image.jpg
```

The program will create ASCII art from your image and display it in the console. You can also save the output to a text file by adding the --save flag:
```bash
python ascii_art.py path/to/your/image.jpg --save output.txt
```

## How it works
The program works by:
1. Loading the image and converting it to grayscale
2. Resizing the image to fit the console width
3. Converting each pixel to an ASCII character based on its brightness
4. Displaying the resulting ASCII art

## Supported Image Formats
- JPEG
- PNG
- BMP
- And other formats supported by PIL 