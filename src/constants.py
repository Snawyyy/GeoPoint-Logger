"""Constants module for the Geospatial Data Viewer application.

This module contains string constants and other non-configurable values.
"""

# Application constants
APP_NAME = "Geospatial Data Viewer"
APP_VERSION = "0.1.0"

# UI Labels
LOAD_SHP_BUTTON_TEXT = "Load SHP File"
LOAD_IMAGE_BUTTON_TEXT = "Load Georeferenced JPG"
RECORD_ID_BUTTON_TEXT = "Record ID & Next"
GOTO_BUTTON_TEXT = "Go to ID"
NEXT_BUTTON_TEXT = "Next Point"
PREV_BUTTON_TEXT = "Previous Point"

# Group box titles
FILE_OPERATIONS_GROUP_TITLE = "File Operations"
NAVIGATION_GROUP_TITLE = "Navigation"
SHP_TABLE_GROUP_TITLE = "SHP Table Data"

# Status messages
READY_STATUS = "Ready to load files"
SUCCESS_SHAPEFILE_LOADED = "Successfully loaded {file_path} with {feature_count} features"
ERROR_SHAPEFILE_LOADED = "Error loading SHP: {error_message}"
SUCCESS_IMAGE_LOADED = "Successfully loaded image: {file_path}"
SUCCESS_IMAGE_LOADED_FALLBACK = "Successfully loaded image (using fallback): {file_path}"
ERROR_IMAGE_LOADED = "Error loading image: {error_message}"
NO_SHAPEFILE_LOADED = "Please load a shapefile first"
NO_ID_ENTERED = "Please enter an ID value"
INDEX_OUT_OF_RANGE = "Index {target_id} is out of range"
INVALID_INDEX = "Please enter a valid integer index"
NAVIGATED_TO_INDEX = "Navigated to index {target_id}"
MOVED_TO_POINT = "Moved to point {point_index}"
NO_ID_COLUMN = "No '{id_field_name}' column found in data"
RECORDED_ID_MESSAGE = "Recorded ID {id_value} for point {current_idx}, moved to next point"
ERROR_ZOOMING_MESSAGE = "Error zooming to point: {error_message}"

# Workflow instructions
WORKFLOW_INSTRUCTIONS = "Workflow: Look at map → Write ID in field → Click 'Record ID & Next' → Next point auto-zooms"

# Zoom display format
ZOOM_DISPLAY_FORMAT = "Zoom: {zoom_level:.1f}x"