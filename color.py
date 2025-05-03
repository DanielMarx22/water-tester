import os
from PIL import Image

# Define the full path to the image
image_path = "/home/danielmarx/Pictures/frog.png"

# Open the image
img = Image.open(image_path).convert("RGB")

# Print image size
print("Image size:", img.size)

# Pick a pixel location (adjust these numbers!)
x, y = 974, 339
rgb = img.getpixel((x, y))
print(f"RGB at ({x},{y}): {rgb}")
