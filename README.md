# GeoPoint Logger

A Python application for efficiently logging raster values at specific points by navigating point-to-point on a map.

## Features

- Load and display SHP files with point locations
- Overlay georeferenced images
- View and edit attribute tables
- Navigate between points (Next/Previous) with automatic zoom
- Quickly record raster values at each point with simple keyboard input
- Workflow: Look at map → Enter raster value → Press Enter → Navigate to next point
- Record values and move to next point with single button click
- Efficient alternative to manual zoom-view-record-repeat process

## Project Structure

```
GeoPoint Logger/
├── requirements.txt          # Python dependencies
├── setup.py                 # Setup configuration
├── README.md               # Project documentation
├── TESTING.md              # Testing instructions
├── scripts/                # Utility scripts
│   ├── debug/              # Debugging scripts
│   ├── test_data/          # Test data creation scripts
│   └── utilities/          # Utility scripts
├── logs/                   # Log files
└── src/
    ├── __init__.py
    ├── main.py             # Main application entry point
    ├── data_handler.py     # Geospatial data operations
    ├── map_display.py      # Map visualization
    ├── table_display.py    # Attribute table display
    ├── column_assignment.py # Column assignment functionality
    ├── image_settings.py   # Image display settings
    ├── layer_list.py       # Layer visibility controls
    ├── utils.py            # Utility functions
    ├── config.py           # Configuration settings
    ├── constants.py        # Constant values
    └── workflow.py         # Workflow management
```

## Technologies Used

- **Python 3.8+**
- **PyQt5** - Desktop GUI framework
- **GeoPandas** - Geospatial data processing
- **Matplotlib** - Plotting and visualization
- **Shapely** - Geometric operations
- **Fiona** - File access for geospatial formats
- **OpenCV** - Image processing
- **NumPy/Pandas** - Data manipulation

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python src/main.py
```

Or use the batch file:
```bash
run_app.bat
```

### Workflow:
1. Load a project folder containing ymishnep.shp and associated JPG images using the "Load Project Folder" button
2. Navigate between points using the "Next Point" and "Previous Point" buttons
3. View the raster value at each point on the map
4. Enter the observed value in the text field
5. Click "Record ID & Next" or press Enter to record the value and move to the next point
6. The application will automatically zoom to the next point after recording
7. Use the "Go to ID" function to navigate to specific points

## Architecture

The application follows a modular architecture:

- **data_handler.py**: Manages loading, processing, and manipulation of geospatial data
- **map_display.py**: Handles visualization of maps, images, and geospatial data with zoom capabilities
- **table_display.py**: Displays and allows editing of attribute tables
- **workflow.py**: Manages the user workflow (record values, move to next point, zoom)
- **column_assignment.py**: Handles column mapping functionality
- **image_settings.py**: Manages image display parameters (brightness, contrast, etc.)
- **layer_list.py**: Controls visibility of multiple image layers
- **main.py**: Orchestrates the UI components and overall application flow

## Key Features Implemented

1. **Project Loading**: Load project folders containing shapefiles and associated images
2. **Multi-layer Visualization**: Display multiple georeferenced images with layer controls
3. **Value Logging**: Efficiently record raster values at specific points
4. **Navigation**: Move between points with automatic zoom
5. **Workflow Automation**: Single-entry logging with automatic movement to next point
6. **Image Controls**: Adjust brightness, contrast, saturation, and threshold
7. **Layer Management**: Toggle visibility of different image layers

## Testing

Sample test files are organized in subdirectories:
- `testing/shapefiles/` - Shapefile components
- `testing/images/` - Georeferenced images and metadata
- `testing/data/` - Geospatial parameter files

Use scripts in `scripts/test_data/` to create new test data as needed.