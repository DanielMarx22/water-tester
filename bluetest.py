from PIL import Image
import os

def get_pixel_rgb(image_path, x=1700, y=1200):
    """
    Get RGB values of a specific pixel in an image
    Args:
        image_path: Path to the image file
        x: X coordinate (default 1550)
        y: Y coordinate (default 750)
    Returns:
        Tuple of (R, G, B) values
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if not already in that mode
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Get pixel data
            pixel = img.getpixel((x, y))
            return pixel
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

if __name__ == "__main__":
    # Change this to your image path
    image_path = "/home/danielmarx/Desktop/CodeStuff/captured_images/image_2025-06-03_18-36-33.jpg"
    
    # Verify image exists
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        print("Please ensure the image is in the same directory as this script")
        exit(1)
    
    # Get the pixel values
    rgb = get_pixel_rgb(image_path)
    
    if rgb:
        r, g, b = rgb
        print(f"Pixel at (1700, 1200) RGB values:")
        print(f"Red: {r}")
        print(f"Green: {g}")
        print(f"Blue: {b}")
        print(f"\nHex: #{r:02x}{g:02x}{b:02x}")
    else:
        print("Failed to get pixel values")