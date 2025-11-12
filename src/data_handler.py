"""
Data handler module for geospatial operations using proper geospatial libraries
"""
import geopandas as gpd
import numpy as np
import rasterio
from rasterio.plot import show
from PIL import Image
import os


class GeospatialDataHandler:
    """
    Handles loading, processing, and manipulation of geospatial data
    """
    def __init__(self):
        self.shapefile_path = None
        self.georef_image_path = None
        self.gdf = None  # GeoDataFrame
        self.image_data = None
        self.image_dataset = None  # Rasterio dataset
        self.current_index = 0

    def load_shapefile(self, file_path):
        """Load a shapefile and store it as a GeoDataFrame"""
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

    def load_georef_image(self, file_path):
        """Load a georeferenced image and handle world file for proper geospatial info"""
        try:
            # First, try to read the world file if it exists
            world_file_params = self._load_world_file(file_path)
            
            # Load the image with PIL
            with Image.open(file_path) as img:
                self.image_data = np.array(img)
            
            # Create a virtual rasterio dataset with geospatial information from world file
            if world_file_params:
                # Create an in-memory georeferenced dataset using the world file parameters
                from rasterio.io import MemoryFile
                from rasterio.transform import from_gcps
                from rasterio.control import GroundControlPoint
                
                # Extract parameters
                pixel_width, rotation_y, rotation_x, pixel_height, top_left_x, top_left_y = world_file_params
                
                from rasterio.io import MemoryFile
                from rasterio.transform import Affine

                # A,D,B,E,C,F from the world file
                pixel_width, rotation_y, rotation_x, pixel_height, top_left_x_c, top_left_y_c = world_file_params

                # Convert center (C,F) to the corner expected by GDAL/rasterio:
                x0 = top_left_x_c - 0.5*pixel_width - 0.5*rotation_y
                y0 = top_left_y_c - 0.5*rotation_x - 0.5*pixel_height

                # Affine is [[A, D, x0], [B, E, y0], [0, 0, 1]]
                transform = Affine(pixel_width, rotation_y, x0,
                                   rotation_x,  pixel_height, y0)

                # image dimensions
                height, width = self.image_data.shape[:2]

                profile = {
                    "driver": "GTiff",
                    "width": width,
                    "height": height,
                    "count": self.image_data.shape[2] if self.image_data.ndim == 3 else 1,
                    "dtype": self.image_data.dtype,
                    "transform": transform,
                    "crs": "EPSG:2039",  # or detect from your workflow
                }

                memfile = MemoryFile()
                with memfile.open(**profile) as mem_dataset:
                    if self.image_data.ndim == 3:
                        for i in range(self.image_data.shape[2]):
                            mem_dataset.write(self.image_data[:, :, i], i + 1)
                    else:
                        mem_dataset.write(self.image_data, 1)

                self.image_dataset = memfile.open()
                print(f"Transform: {transform}")
                print(f"Bounds: {self.image_dataset.bounds}")
                
            else:
                # No world file - use the image data only
                print("No world file found, loading image without georeferencing")
                self.image_dataset = None
                
            self.georef_image_path = file_path
            return True, f"Successfully loaded image: {file_path}"
            
        except Exception as e:
            print(f"Error loading georeferenced image: {e}")
            # Fallback to PIL only
            try:
                with Image.open(file_path) as img:
                    self.image_data = np.array(img)
                    self.image_dataset = None
                    self.georef_image_path = file_path
                print("Loaded image with PIL as fallback")
                return True, f"Successfully loaded image (using fallback): {file_path}"
            except Exception as e2:
                return False, f"Error loading image: {str(e2)}"
    
    def _load_world_file(self, image_path):
        """Load georeferencing information from associated world file"""
        import os
        
        # Possible extensions for world files - comprehensive list
        world_extensions = ['.jgw', '.jgwx', '.jpgw', '.JGW', '.JGWX', '.JPGW',  # JPEG world files
                           '.pgw', '.pgwx', '.PGW', '.PGWX',                   # PNG world files  
                           '.tfw', '.tfwx', '.TFW', '.TFWX',                   # TIFF world files
                           '.wld', '.WLD']                                     # Generic world file
        
        # Get the base path without extension
        base_path = os.path.splitext(image_path)[0]
        
        # Try to find the world file using multiple strategies
        world_file_path = None
        
        # Strategy 1: Standard extension appending
        for ext in ['.jgw', '.jgwx', '.jpgw', '.pgw', '.pgwx', '.tfw', '.tfwx', '.wld']:
            potential_path = base_path + ext
            if os.path.exists(potential_path):
                world_file_path = potential_path
                break
            # Also try with case variations
            potential_path_upper = base_path + ext.upper()
            if os.path.exists(potential_path_upper):
                world_file_path = potential_path_upper
                break
        
        # Strategy 2: If not found, scan directory for any matching world file
        if not world_file_path:
            directory = os.path.dirname(image_path) or '.'
            image_basename = os.path.splitext(os.path.basename(image_path))[0]
            for file in os.listdir(directory):
                file_lower = file.lower()
                if any(file_lower.endswith(ext.lower().lstrip('.')) for ext in ['.jgw', '.jgwx', '.pgw', '.pgwx', '.tfw', '.tfwx', '.wld']):
                    # Check if this file corresponds to our image
                    file_basename = os.path.splitext(file)[0]
                    if file_basename.lower() == image_basename.lower():
                        world_file_path = os.path.join(directory, file)
                        break
        
        if world_file_path:
            try:
                with open(world_file_path, 'r') as f:
                    lines = f.read().splitlines()  # Use splitlines() instead of readlines()
                
                print(f"Found world file: {world_file_path}")
                print(f"Raw content: {'|'.join(lines[:6])}")  # Show first 6 lines
                
                # Filter out empty lines
                non_empty_lines = [line.strip() for line in lines if line.strip()]
                
                if len(non_empty_lines) >= 6:
                    values = []
                    for i in range(6):
                        try:
                            val = float(non_empty_lines[i])
                            values.append(val)
                        except ValueError:
                            print(f"Cannot parse line {i+1} as float: '{non_empty_lines[i]}'")
                            return None  # Return None if parsing fails
                    
                    # World file order: A, D, B, E, C, F
                    # A = pixel width, D = y-rotation, B = x-rotation, E = pixel height, C = x center UL, F = y center UL
                    pixel_width, rotation_y, rotation_x, pixel_height, top_left_x, top_left_y = values
                    print(f"World file successfully parsed!")
                    print(f"Parameters: A={pixel_width}, D={rotation_y}, B={rotation_x}, E={pixel_height}, C={top_left_x}, F={top_left_y}")
                    
                    # Check if coordinates are in the expected range for Israeli Grid
                    if (200000 < top_left_x < 350000 and 500000 < top_left_y < 850000):
                        print("World file coordinates appear to be in Israeli Grid system (EPSG:2039)")
                    else:
                        print("World file coordinates are outside expected Israeli Grid range")
                        
                    return (pixel_width, rotation_y, rotation_x, pixel_height, top_left_x, top_left_y)
                else:
                    print(f"World file has only {len(non_empty_lines)} lines, need at least 6")
            except Exception as e:
                print(f"Error reading world file {world_file_path}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"No world file found for {image_path}")
        return None

    def get_image_bounds(self):
        """Get the geospatial bounds of the image"""
        if self.image_dataset:
            return self.image_dataset.bounds  # (left, bottom, right, top)
        return None

    def get_image_crs(self):
        """Get the coordinate reference system of the image"""
        if self.image_dataset:
            return self.image_dataset.crs
        return None

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