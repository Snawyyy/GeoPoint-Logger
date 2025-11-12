"""Utility functions for the Geospatial Data Viewer application.

This module contains common utility functions used throughout the application.
"""

import os
from typing import Optional, Tuple
import numpy as np
from rasterio.transform import Affine


def find_world_file(image_path: str) -> Optional[str]:
    """Find the associated world file for an image.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Path to the world file if found, None otherwise
    """
    # Possible extensions for world files - comprehensive list
    world_extensions = [
        '.jgw', '.jgwx', '.jpgw', '.JGW', '.JGWX', '.JPGW',  # JPEG world files
        '.pgw', '.pgwx', '.PGW', '.PGWX',                   # PNG world files
        '.tfw', '.tfwx', '.TFW', '.TFWX',                   # TIFF world files
        '.wld', '.WLD'                                     # Generic world file
    ]

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

    return world_file_path


def parse_world_file(world_file_path: str) -> Optional[Tuple[float, float, float, float, float, float]]:
    """Parse a world file and return the transformation parameters.
    
    Args:
        world_file_path: Path to the world file
        
    Returns:
        Tuple of (pixel_width, rotation_y, rotation_x, pixel_height, top_left_x, top_left_y) or None if parsing fails
    """
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

            return (pixel_width, rotation_y, rotation_x, pixel_height, top_left_x, top_left_y)
        else:
            print(f"World file has only {len(non_empty_lines)} lines, need at least 6")
    except Exception as e:
        print(f"Error reading world file {world_file_path}: {e}")
        import traceback
        traceback.print_exc()

    return None


def create_geospatial_transform(world_file_params: Tuple[float, float, float, float, float, float]) -> Affine:
    """Create a geospatial transform from world file parameters.
    
    Args:
        world_file_params: Tuple of (pixel_width, rotation_y, rotation_x, pixel_height, top_left_x, top_left_y)
        
    Returns:
        Rasterio Affine transform object
    """
    # Extract parameters
    pixel_width, rotation_y, rotation_x, pixel_height, top_left_x_c, top_left_y_c = world_file_params

    # Convert center (C,F) to the corner expected by GDAL/rasterio:
    x0 = top_left_x_c - 0.5*pixel_width - 0.5*rotation_y
    y0 = top_left_y_c - 0.5*rotation_x - 0.5*pixel_height

    # Affine is [[A, D, x0], [B, E, y0], [0, 0, 1]]
    return Affine(pixel_width, rotation_y, x0, rotation_x, pixel_height, y0)


def get_geometry_coordinates(geom) -> Tuple[float, float]:
    """Extract coordinates from a geometry object.
    
    Args:
        geom: A Shapely geometry object
        
    Returns:
        Tuple of (x, y) coordinates
    """
    if hasattr(geom, 'x') and hasattr(geom, 'y'):
        # It's a point geometry
        return geom.x, geom.y
    else:
        # Get the centroid for other geometry types
        centroid = geom.centroid
        return centroid.x, centroid.y


def validate_coordinates(x: float, y: float, min_x: float = None, max_x: float = None, 
                       min_y: float = None, max_y: float = None) -> bool:
    """Validate that coordinates are within acceptable ranges.
    
    Args:
        x: X coordinate
        y: Y coordinate
        min_x: Minimum acceptable X value
        max_x: Maximum acceptable X value
        min_y: Minimum acceptable Y value
        max_y: Maximum acceptable Y value
        
    Returns:
        True if coordinates are within ranges, False otherwise
    """
    if min_x is not None and x < min_x:
        return False
    if max_x is not None and x > max_x:
        return False
    if min_y is not None and y < min_y:
        return False
    if max_y is not None and y > max_y:
        return False
    return True


def calculate_zoom_range(base_range_x: float, base_range_y: float, zoom_factor: float, 
                        min_range: float = 1.0) -> Tuple[float, float]:
    """Calculate the appropriate zoom range based on zoom factor.
    
    Args:
        base_range_x: Base X range when zoom factor is 1
        base_range_y: Base Y range when zoom factor is 1
        zoom_factor: Current zoom factor (higher = closer zoom)
        min_range: Minimum allowed range
        
    Returns:
        Tuple of (xlim_range, ylim_range)
    """
    # Calculate ranges based on zoom factor (higher zoom_factor = closer zoom, smaller range)
    xlim_range = base_range_x / zoom_factor
    ylim_range = base_range_y / zoom_factor

    # Ensure minimum zoom range to avoid excessive zooming
    xlim_range = max(xlim_range, min_range)
    ylim_range = max(ylim_range, min_range)

    return xlim_range, ylim_range


def create_memory_dataset(image_data: np.ndarray, transform: Affine, crs: str = "EPSG:2039"):
    """Create a memory rasterio dataset from image data and transform.
    
    Args:
        image_data: Numpy array representing image data
        transform: Rasterio Affine transform
        crs: Coordinate reference system
        
    Returns:
        Memory file dataset
    """
    from rasterio.io import MemoryFile
    
    # image dimensions
    height, width = image_data.shape[:2]

    profile = {
        "driver": "GTiff",
        "width": width,
        "height": height,
        "count": image_data.shape[2] if image_data.ndim == 3 else 1,
        "dtype": image_data.dtype,
        "transform": transform,
        "crs": crs,
    }

    memfile = MemoryFile()
    with memfile.open(**profile) as mem_dataset:
        if image_data.ndim == 3:
            for i in range(image_data.shape[2]):
                mem_dataset.write(image_data[:, :, i], i + 1)
        else:
            mem_dataset.write(image_data, 1)
    
    return memfile.open()