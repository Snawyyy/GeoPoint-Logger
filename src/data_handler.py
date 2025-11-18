"""
Data handler module for geospatial operations with better separation of concerns
"""
import geopandas as gpd
import numpy as np
import rasterio
from PIL import Image
import os
from typing import Optional, Tuple

from .config import DataHandlerConfig, CRSConfig
from .utils import find_world_file, parse_world_file, create_geospatial_transform, create_memory_dataset


class ImageLoader:
    """Handles loading of georeferenced images with proper geospatial information"""
    
    def __init__(self):
        self.image_datas = []
        self.image_datasets = []  # List of Rasterio datasets
        self.image_filenames = []

    def load_georef_images(self, file_paths: list) -> Tuple[bool, str]:
        """Load multiple georeferenced images."""
        self.image_datas.clear()
        self.image_datasets.clear()
        self.image_filenames.clear()
        for file_path in file_paths:
            success, message = self._load_single_georef_image(file_path)
            if not success:
                return False, message
        return True, f"Successfully loaded {len(file_paths)} images."

    def _load_single_georef_image(self, file_path: str) -> Tuple[bool, str]:
        """Load a single georeferenced image and handle world file for proper geospatial info"""
        try:
            world_file_params = parse_world_file(find_world_file(file_path))
            with Image.open(file_path) as img:
                image_data = np.array(img)

            if world_file_params:
                transform = create_geospatial_transform(world_file_params)
                image_dataset = create_memory_dataset(image_data, transform, CRSConfig.DEFAULT_CRS)
                self.image_datas.append(image_data)
                self.image_datasets.append(image_dataset)
                self.image_filenames.append(os.path.basename(file_path))
            else:
                self.image_datas.append(image_data)
                self.image_datasets.append(None)
                self.image_filenames.append(os.path.basename(file_path))
                print(f"No world file found for {file_path}, loading without georeferencing")

            return True, f"Successfully loaded image: {file_path}"
        except Exception as e:
            return False, f"Error loading image {file_path}: {str(e)}"

    def get_image_bounds(self) -> Optional[Tuple]:
        """Get the geospatial bounds of the first image"""
        if self.image_datasets and self.image_datasets[0]:
            return self.image_datasets[0].bounds
        return None

    def get_image_crs(self) -> Optional[str]:
        """Get the coordinate reference system of the first image"""
        if self.image_datasets and self.image_datasets[0]:
            return self.image_datasets[0].crs
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

    def load_georef_images(self, file_paths: list) -> Tuple[bool, str]:
        """Load multiple georeferenced images."""
        return self.image_loader.load_georef_images(file_paths)

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