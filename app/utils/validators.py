from PIL import Image
from typing import Tuple

def validate_image(image: Image.Image) -> bool:
    """
    Validate that the image is in a supported format
    """
    supported_formats = ['JPEG', 'PNG', 'BMP', 'TIFF']
    return image.format in supported_formats

def validate_dimensions(
    width: float, 
    height: float, 
    max_width: float = 21.0, 
    max_height: float = 21.0
) -> bool:
    """
    Validate that the dimensions are within acceptable limits
    """
    return width <= max_width and height <= max_height and width > 0 and height > 0

def validate_color_count(image: Image.Image, max_colors: int = 5) -> bool:
    """
    Validate that the image doesn't exceed the maximum number of colors
    """
    # Convert to palette mode to count unique colors
    if image.mode != 'P':
        temp_image = image.convert('P', palette=Image.ADAPTIVE)
    else:
        temp_image = image

    # Get histogram to count unique colors
    hist = temp_image.histogram()
    unique_colors = sum(1 for count in hist if count > 0)

    return unique_colors <= max_colors