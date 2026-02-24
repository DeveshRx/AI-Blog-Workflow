from PIL import Image
import os

def convert_png_to_webp(input_path, output_path, quality=80):
    try:
        # Open the PNG image
        with Image.open(input_path) as img:
            # Convert to RGB if necessary (WebP supports RGBA, but 
            # some older viewers prefer RGB if there's no transparency)
            image_rgb = img.convert("RGBA")
            
            # Save as WebP
            image_rgb.save(output_path, "webp", quality=quality)
            
        print(f"Success! Saved to: {output_path}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

# Usage
#convert_png_to_webp("example.png", "example.webp")