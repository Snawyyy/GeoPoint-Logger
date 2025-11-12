"""Configuration module for the Geospatial Data Viewer application.

This module contains all configuration values to avoid magic numbers
and make the application more maintainable.
"""

# UI Configuration
class UIConfig:
    """UI-related configuration values."""
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 900
    WINDOW_X_POSITION = 100
    WINDOW_Y_POSITION = 100
    
    # Splitter sizes (in pixels)
    MAP_PANEL_SIZE = 1000
    CONTROL_PANEL_SIZE = 400
    
    # Default zoom settings
    DEFAULT_ZOOM_LEVEL = 5
    MIN_ZOOM_LEVEL = 1
    MAX_ZOOM_LEVEL = 20
    
    # Zoom range for map display
    BASE_ZOOM_RANGE_X = 500.0  # meters
    BASE_ZOOM_RANGE_Y = 500.0  # meters
    MIN_ZOOM_RANGE = 1.0       # minimum meters range
    MINIMUM_ZOOM_FACTOR = 0.1  # minimum zoom factor allowed


# File Extensions Configuration
class FileExtensionsConfig:
    """File extension configuration values."""
    # Supported shapefile extensions
    SHAPEFILE_EXTENSIONS = "Shapefiles (*.shp);;All Files (*)"
    
    # Supported image extensions
    IMAGE_EXTENSIONS = "Image Files (*.jpg *.jpeg *.tiff *.tif);;All Files (*)"
    
    # Possible world file extensions
    WORLD_FILE_EXTENSIONS = [
        '.jgw', '.jgwx', '.jpgw', '.JGW', '.JGWX', '.JPGW',  # JPEG world files
        '.pgw', '.pgwx', '.PGW', '.PGWX',                   # PNG world files
        '.tfw', '.tfwx', '.TFW', '.TFWX',                   # TIFF world files
        '.wld', '.WLD'                                     # Generic world file
    ]


# Coordinate Reference System Configuration
class CRSConfig:
    """Coordinate Reference System configuration values."""
    DEFAULT_CRS = "EPSG:2039"  # Israeli Grid system
    ISRAELI_GRID_X_MIN = 200000
    ISRAELI_GRID_X_MAX = 350000
    ISRAELI_GRID_Y_MIN = 500000
    ISRAELI_GRID_Y_MAX = 850000


# Data Handler Configuration
class DataHandlerConfig:
    """Data handler configuration values."""
    # Default image display parameters
    DEFAULT_IMAGE_DPI = 100
    DEFAULT_IMAGE_WIDTH = 10
    DEFAULT_IMAGE_HEIGHT = 8

# Workflow Configuration
class WorkflowConfig:
    """Workflow-related configuration values."""
    DEFAULT_ID_FIELD_NAME = "ID"