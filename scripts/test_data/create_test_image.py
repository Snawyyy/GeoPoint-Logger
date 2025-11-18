"""
Test script to create a simple test image
"""
from PIL import Image, ImageDraw
import numpy as np

# Create a simple test image
width, height = 400, 400
image = Image.new('RGB', (width, height), color='lightblue')

# Draw some basic features to make it recognizable
draw = ImageDraw.Draw(image)

# Draw a border
draw.rectangle([10, 10, width-10, height-10], outline='black', width=2)

# Draw some grid lines
for i in range(0, width, 50):
    draw.line([(i, 0), (i, height)], fill='gray', width=1)
for i in range(0, height, 50):
    draw.line([(0, i), (width, i)], fill='gray', width=1)

# Draw some landmarks
draw.ellipse([100, 100, 120, 120], fill='red', outline='black')
draw.ellipse([200, 200, 220, 220], fill='green', outline='black')
draw.ellipse([300, 100, 320, 120], fill='yellow', outline='black')

# Save the image
image.save('test_georef.jpg')

print("Test georeferenced image 'test_georef.jpg' created successfully!")