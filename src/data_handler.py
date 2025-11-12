"""
Data handler module for geospatial operations
"""
import geopandas as gpd
import numpy as np
from PIL import Image


class GeospatialDataHandler:
    """
    Handles loading, processing, and manipulation of geospatial data
    """
    def __init__(self):
        self.shapefile_path = None
        self.georef_image_path = None
        self.gdf = None  # GeoDataFrame
        self.image_data = None
        self.current_index = 0
        
    def load_shapefile(self, file_path):
        """Load a shapefile and store it as a GeoDataFrame"""
        try:
            self.gdf = gpd.read_file(file_path)
            self.shapefile_path = file_path
            return True, f"Successfully loaded {file_path} with {len(self.gdf)} features"
        except Exception as e:
            return False, f"Error loading SHP: {str(e)}"
    
    def load_georef_image(self, file_path):
        """Load a georeferenced image"""
        try:
            self.image_data = np.array(Image.open(file_path))
            self.georef_image_path = file_path
            return True, f"Successfully loaded image: {file_path}"
        except Exception as e:
            return False, f"Error loading image: {str(e)}"
    
    def get_current_point(self):
        """Get the current point based on the current index"""
        if self.gdf is not None and len(self.gdf) > 0:
            return self.gdf.iloc[self.current_index]
        return None
    
    def get_geodataframe(self):
        """Get the current GeoDataFrame"""
        return self.gdf
    
    def set_current_index(self, index):
        """Set the current index for navigation"""
        if self.gdf is not None and 0 <= index < len(self.gdf):
            self.current_index = index
            return True
        return False
    
    def get_current_index(self):
        """Get the current index"""
        return self.current_index
    
    def move_next(self):
        """Move to the next point"""
        if self.gdf is not None and len(self.gdf) > 0:
            self.current_index = (self.current_index + 1) % len(self.gdf)
            return True
        return False
    
    def move_previous(self):
        """Move to the previous point"""
        if self.gdf is not None and len(self.gdf) > 0:
            self.current_index = (self.current_index - 1) % len(self.gdf)
            return True
        return False
    
    def move_to_index(self, index):
        """Move to a specific index"""
        return self.set_current_index(index)
    
    def update_cell_value(self, row, col, value):
        """Update a specific cell value in the GeoDataFrame"""
        if self.gdf is not None:
            col_name = self.gdf.columns[col]
            self.gdf.iloc[row, col] = value
            return True
        return False