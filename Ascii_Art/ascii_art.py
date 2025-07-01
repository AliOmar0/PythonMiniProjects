#!/usr/bin/env python3
import argparse
from PIL import Image
import sys
import os
import streamlit as st
import numpy as np
import io

# ASCII characters used for the conversion (from darkest to lightest)
ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

def resize_image(image, new_width=100):
    """Resize image to fit the specified width while maintaining aspect ratio."""
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width)
    resized_image = image.resize((new_width, new_height))
    return resized_image

def grayscale(image):
    """Convert image to grayscale."""
    return image.convert("L")

def pixels_to_ascii(image):
    """Convert pixels to ASCII characters based on brightness."""
    pixels = np.array(image)
    ascii_str = ""
    for row in pixels:
        for pixel in row:
            index = pixel * (len(ASCII_CHARS) - 1) // 255
            ascii_str += ASCII_CHARS[index]
        ascii_str += "\n"
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
    image = grayscale(image)
    
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
    st.title("ASCII Art Generator")
    st.write("Convert your images into ASCII art!")

    # File uploader
    uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png", "bmp"])
    
    if uploaded_file is not None:
        # Display original image
        image = Image.open(uploaded_file)
        st.image(image, caption="Original Image", use_container_width=True)
        
        # Settings
        st.sidebar.header("Settings")
        width = st.sidebar.slider("Output Width", 20, 200, 100, 10)
        font_size = st.sidebar.slider("ASCII Art Size", 8, 24, 14, 2)
        
        # Convert to ASCII
        new_image = resize_image(image, width)
        new_image = grayscale(new_image)
        ascii_str = pixels_to_ascii(new_image)
        
        # Escape HTML special characters in ASCII art
        escaped_ascii = ascii_str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # Create styled ASCII art display
        st.markdown("### ASCII Art Output")
        st.markdown(
            f"""
            <div style="
                font-family: monospace;
                font-size: {font_size}px;
                white-space: pre;
                overflow-x: auto;
                background-color: #0e1117;
                color: #ffffff;
                padding: 15px;
                border-radius: 5px;
                border: 1px solid #333;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">{escaped_ascii}</div>
            """,
            unsafe_allow_html=True
        )
        
        # Download options
        st.markdown("### Download Options")
        col1, col2 = st.columns(2)
        
        with col1:
            # Download as text
            ascii_bytes = ascii_str.encode()
            bio = io.BytesIO(ascii_bytes)
            st.download_button(
                label="Download as Text",
                data=bio,
                file_name="ascii_art.txt",
                mime="text/plain"
            )
        
        with col2:
            # Download as HTML (for preserving formatting)
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{
                        background-color: #0e1117;
                        margin: 0;
                        padding: 20px;
                    }}
                    .ascii-art {{
                        font-family: monospace;
                        font-size: {font_size}px;
                        white-space: pre;
                        line-height: 1;
                        color: #ffffff;
                        background-color: #0e1117;
                        padding: 20px;
                        border-radius: 5px;
                        border: 1px solid #333;
                    }}
                </style>
            </head>
            <body>
                <div class="ascii-art">{escaped_ascii}</div>
            </body>
            </html>
            """
            bio_html = io.BytesIO(html_content.encode())
            st.download_button(
                label="Download as HTML",
                data=bio_html,
                file_name="ascii_art.html",
                mime="text/html"
            )

if __name__ == "__main__":
    main() 