# Geospatial Data Viewer

A Python application for viewing and editing shapefiles (SHP) with georeferenced images (JPG).

## Features

- Load and display SHP files
- Overlay georeferenced JPG images
- View and edit attribute tables
- Navigate between points (Next/Previous)
- Workflow: Look at map → Write ID → Enter → Next point (with automatic zoom)
- Record ID and move to next point with single button click
- Automatic zoom to each point during navigation

## Project Structure

```
Tree_Log/
├── requirements.txt          # Python dependencies
├── setup.py                 # Setup configuration
├── README.md               # Project documentation
├── TESTING.md              # Testing instructions
├── create_test_data.py     # Script to create test shapefile
├── create_test_image.py    # Script to create test image
└── src/
    ├── __init__.py
    ├── main.py             # Main application entry point
    ├── data_handler.py     # Geospatial data operations
    ├── map_display.py      # Map visualization
    ├── table_display.py    # Attribute table display
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

### Workflow:
1. Load a SHP file using the "Load SHP File" button
2. Load a georeferenced JPG using the "Load Georeferenced JPG" button
3. Navigate between points using the "Next Point" and "Previous Point" buttons
4. Edit attributes directly in the table
5. Use the "Go to ID" function to navigate to specific points
6. To use the main workflow: Look at the map → Enter an ID in the text field → Click "Record ID & Next" → The application will record the ID and automatically zoom to the next point

## Architecture

The application follows a modular architecture:

- **data_handler.py**: Manages loading, processing, and manipulation of geospatial data
- **map_display.py**: Handles visualization of maps and geospatial data with zoom capabilities  
- **table_display.py**: Displays and allows editing of attribute tables
- **workflow.py**: Manages the user workflow (record ID, move to next point, zoom)
- **main.py**: Orchestrates the UI components and overall application flow

## Key Features Implemented

1. **File Loading**: Load shapefiles and georeferenced images
2. **Data Visualization**: Display points on a map with optional image background
3. **Table Editing**: Edit attribute data directly in the UI table
4. **Navigation**: Move between points with automatic zoom
5. **Workflow Automation**: Single-click ID recording with automatic movement to next point and zoom

## Testing

Sample test files are provided:
- `test_points.shp` - Sample shapefile with points
- `test_georef.jpg` - Sample georeferenced image

Run `python create_test_data.py` and `python create_test_image.py` to regenerate these files.