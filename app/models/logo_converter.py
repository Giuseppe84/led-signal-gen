from PIL import Image
import numpy as np
from typing import Tuple

class LogoConverter:
    def __init__(self, max_colors: int = 5):
        self.max_colors = max_colors
    
    def process_image(self, image: Image.Image, num_colors: int = 4) -> Image.Image:
        """
        Process the input image to reduce it to the specified number of colors
        suitable for MMU printing (up to 4 colors plus background)
        """
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize image to appropriate dimensions for processing
        img_array = np.array(image)
        
        # Apply k-means clustering to reduce colors
        reduced_img = self._reduce_colors_kmeans(img_array, num_colors)
        
        # Convert back to PIL Image
        processed_image = Image.fromarray(reduced_img.astype('uint8'), 'RGB')
        
        return processed_image
    
    def _reduce_colors_kmeans(self, img_array: np.ndarray, k: int) -> np.ndarray:
        """
        Reduce colors in image using k-means clustering algorithm
        """
        from sklearn.cluster import KMeans
        
        # Reshape image array to 2D for k-means
        h, w, c = img_array.shape
        img_reshaped = img_array.reshape(h * w, c)
        
        # Apply k-means clustering
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(img_reshaped)
        centers = kmeans.cluster_centers_
        
        # Replace each pixel with its cluster center color
        segmented_img = centers[labels].astype('uint8')
        
        # Reshape back to original image dimensions
        segmented_img = segmented_img.reshape(h, w, c)
        
        return segmented_img
    
    def validate_color_count(self, image: Image.Image, max_colors: int = 5) -> bool:
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