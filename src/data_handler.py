"""
Data handler module for geospatial operations with better separation of concerns
"""
import geopandas as gpd
import numpy as np
import rasterio
from PIL import Image
import os
from typing import Optional, Tuple

import sys
import os
# Add the src directory to the path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import DataHandlerConfig, CRSConfig
from utils import find_world_file, parse_world_file, create_geospatial_transform, create_memory_dataset


class ImageLoader:
    """Handles loading of georeferenced images with proper geospatial information"""
    
    def __init__(self):
        self.image_data = None
        self.image_dataset = None  # Rasterio dataset

    def load_georef_image(self, file_path: str) -> Tuple[bool, str]:
        """Load a georeferenced image and handle world file for proper geospatial info
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # First, try to read the world file if it exists
            world_file_params = parse_world_file(find_world_file(file_path))

            # Load the image with PIL
            with Image.open(file_path) as img:
                self.image_data = np.array(img)

            # Create a virtual rasterio dataset with geospatial information from world file
            if world_file_params:
                transform = create_geospatial_transform(world_file_params)
                
                self.image_dataset = create_memory_dataset(
                    self.image_data, 
                    transform, 
                    CRSConfig.DEFAULT_CRS
                )
                
                print(f"Transform: {transform}")
                print(f"Bounds: {self.image_dataset.bounds}")

            else:
                # No world file - use the image data only
                print("No world file found, loading image without georeferencing")
                self.image_dataset = None

            return True, f"Successfully loaded image: {file_path}"

        except Exception as e:
            print(f"Error loading georeferenced image: {e}")
            # Fallback to PIL only
            try:
                with Image.open(file_path) as img:
                    self.image_data = np.array(img)
                    self.image_dataset = None
                print("Loaded image with PIL as fallback")
                return True, f"Successfully loaded image (using fallback): {file_path}"
            except Exception as e2:
                return False, f"Error loading image: {str(e2)}"

    def get_image_bounds(self) -> Optional[Tuple]:
        """Get the geospatial bounds of the image"""
        if self.image_dataset:
            return self.image_dataset.bounds  # (left, bottom, right, top)
        return None

    def get_image_crs(self) -> Optional[str]:
        """Get the coordinate reference system of the image"""
        if self.image_dataset:
            return self.image_dataset.crs
        return None


class ShapefileLoader:
    """Handles loading of shapefiles with geospatial information"""
    
    def __init__(self):
        self.gdf = None  # GeoDataFrame
        self.shapefile_path = None

    def load_shapefile(self, file_path: str) -> Tuple[bool, str]:
        """Load a shapefile and store it as a GeoDataFrame
        
        Args:
            file_path: Path to the shapefile
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            self.gdf = gpd.read_file(file_path)
            self.shapefile_path = file_path

            # Print coordinate system and bounds info
            if hasattr(self.gdf, 'crs') and self.gdf.crs is not None:
                print(f"Shapefile CRS: {self.gdf.crs}")
            else:
                print("Shapefile has no CRS specified")

            if not self.gdf.empty:
                bounds = self.gdf.total_bounds
                print(f"Shapefile bounds: minx={bounds[0]:.2f}, miny={bounds[1]:.2f}, maxx={bounds[2]:.2f}, maxy={bounds[3]:.2f}")

            return True, f"Successfully loaded {file_path} with {len(self.gdf)} features"
        except Exception as e:
            return False, f"Error loading SHP: {str(e)}"

    def get_geodataframe(self):
        """Get the current GeoDataFrame"""
        return self.gdf


class NavigationManager:
    """Manages navigation between points in the dataset"""
    
    def __init__(self):
        self.gdf = None
        self.current_index = 0

    def set_geodataframe(self, gdf):
        """Set the GeoDataFrame to navigate through"""
        self.gdf = gdf
        if gdf is not None and len(gdf) > 0:
            self.current_index = 0

    def get_current_point(self):
        """Get the current point based on the current index"""
        if self.gdf is not None and len(self.gdf) > 0:
            return self.gdf.iloc[self.current_index]
        return None

    def get_current_index(self) -> int:
        """Get the current index"""
        return self.current_index

    def set_current_index(self, index: int) -> bool:
        """Set the current index for navigation"""
        if self.gdf is not None and 0 <= index < len(self.gdf):
            self.current_index = index
            return True
        return False

    def move_next(self) -> bool:
        """Move to the next point"""
        if self.gdf is not None and len(self.gdf) > 0:
            self.current_index = (self.current_index + 1) % len(self.gdf)
            return True
        return False

    def move_previous(self) -> bool:
        """Move to the previous point"""
        if self.gdf is not None and len(self.gdf) > 0:
            self.current_index = (self.current_index - 1) % len(self.gdf)
            return True
        return False

    def move_to_index(self, index: int) -> bool:
        """Move to a specific index"""
        return self.set_current_index(index)


class DataEditor:
    """Handles editing operations on the dataset"""
    
    def update_cell_value(self, gdf, row: int, col: int, value):
        """Update a specific cell value in the GeoDataFrame with type conversion.
        
        Args:
            gdf: The GeoDataFrame to update.
            row: Row index to update.
            col: Column index to update.
            value: New value to set (will be converted to column's dtype).
            
        Returns:
            True if update was successful, False otherwise.
            
        Raises:
            ValueError: If the value cannot be converted to the column's data type.
        """
        if gdf is not None:
            col_name = gdf.columns[col]
            target_dtype = gdf[col_name].dtype

            # Attempt to convert the value to the target column's dtype
            try:
                if np.issubdtype(target_dtype, np.integer):
                    converted_value = int(value)
                elif np.issubdtype(target_dtype, np.floating):
                    converted_value = float(value)
                elif np.issubdtype(target_dtype, np.bool_):
                    converted_value = bool(value)
                else:
                    # For other types (e.g., object/string), keep as is
                    converted_value = value
            except ValueError:
                raise ValueError(f"Cannot convert '{value}' to {target_dtype} for column '{col_name}'")
            
            gdf.iloc[row, col] = converted_value
            return True
        return False


class GeospatialDataHandler:
    """
    Handles loading, processing, and manipulation of geospatial data
    """
    def __init__(self):
        self.image_loader = ImageLoader()
        self.shapefile_loader = ShapefileLoader()
        self.navigation_manager = NavigationManager()
        self.data_editor = DataEditor()
        
        self.georef_image_path = None

    def load_shapefile(self, file_path: str) -> Tuple[bool, str]:
        """Load a shapefile and store it as a GeoDataFrame"""
        result = self.shapefile_loader.load_shapefile(file_path)
        if result[0]:  # If loading was successful
            self.navigation_manager.set_geodataframe(self.shapefile_loader.get_geodataframe())
        return result

    def load_georef_image(self, file_path: str) -> Tuple[bool, str]:
        """Load a georeferenced image"""
        result = self.image_loader.load_georef_image(file_path)
        if result[0]:  # If loading was successful
            self.georef_image_path = file_path
        return result

    def get_image_bounds(self):
        """Get the geospatial bounds of the image"""
        return self.image_loader.get_image_bounds()

    def get_image_crs(self):
        """Get the coordinate reference system of the image"""
        return self.image_loader.get_image_crs()

    def get_current_point(self):
        """Get the current point based on the current index"""
        return self.navigation_manager.get_current_point()

    def get_geodataframe(self):
        """Get the current GeoDataFrame"""
        return self.shapefile_loader.get_geodataframe()

    def set_current_index(self, index: int) -> bool:
        """Set the current index for navigation"""
        return self.navigation_manager.set_current_index(index)

    def get_current_index(self) -> int:
        """Get the current index"""
        return self.navigation_manager.get_current_index()

    def move_next(self) -> bool:
        """Move to the next point"""
        return self.navigation_manager.move_next()

    def move_previous(self) -> bool:
        """Move to the previous point"""
        return self.navigation_manager.move_previous()

    def move_to_index(self, index: int) -> bool:
        """Move to a specific index"""
        return self.navigation_manager.move_to_index(index)

    def update_cell_value(self, row: int, col: int, value) -> bool:
        """Update a specific cell value in the GeoDataFrame"""
        gdf = self.get_geodataframe()
        return self.data_editor.update_cell_value(gdf, row, col, value)