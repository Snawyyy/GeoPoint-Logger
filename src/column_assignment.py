"""
Column assignment feature for the Geospatial Data Viewer
"""
import sys
import os
import logging
# Add the src directory to the path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QComboBox, QLineEdit, QPushButton, QFormLayout, QGroupBox
from PyQt5.QtCore import pyqtSignal, QObject
from constants import *

# Set up logging
logging.basicConfig(
    filename='column_assignment.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)


class ColumnAssignmentFeature(QObject):
    """
    Handles the functionality for assigning data to specific columns
    """
    # Define a signal for when we need to move to the next point
    next_point_requested = pyqtSignal()

    def __init__(self, data_handler, table_widget, status_label):
        super().__init__()  # Call parent constructor
        self.data_handler = data_handler
        self.table_widget = table_widget  # May be None if table UI is removed
        self.status_label = status_label

        # Initialize UI components
        self.column_selector = None
        self.data_input = None
        self.assign_button = None

        self._setup_ui()
        self._setup_connections()

        # Refresh columns in case a shapefile was already loaded
        self.refresh_columns()

    def _setup_ui(self):
        """Set up the UI components for column assignment"""
        self.column_selector = QComboBox()
        self.data_input = QLineEdit()
        self.assign_button = QPushButton(ASSIGN_DATA_BUTTON_TEXT)

    def _setup_connections(self):
        """Set up signal connections"""
        # Connect to handle Enter key press in the data input field
        self.data_input.returnPressed.connect(self.assign_data_and_move_next)
        # Connect the button click to the same function
        self.assign_button.clicked.connect(self.assign_data_and_move_next)
        # Connect column selection change to update the input field with current value
        self.column_selector.currentTextChanged.connect(self.update_input_with_current_value)
        # Connect the editingFinished signal to save the data
        self.data_input.editingFinished.connect(self.save_current_data)

    def get_control_group(self):
        """Get a group box containing all the column assignment controls"""
        group = QGroupBox("Column Assignment")
        layout = QFormLayout(group)

        layout.addRow(COLUMN_LABEL, self.column_selector)
        layout.addRow(DATA_LABEL, self.data_input)
        layout.addRow(self.assign_button)

        return group

    def refresh_columns(self):
        """Refresh the column list when a new shapefile is loaded"""
        # Check if UI components are initialized
        if self.column_selector is None:
            return

        # Clear the current items
        self.column_selector.clear()

        # Get the current geodataframe
        gdf = self.data_handler.get_geodataframe()
        if gdf is not None and not gdf.empty:
            try:
                # Get column names excluding the geometry column
                geometry_col_name = gdf.geometry.name
                columns = [str(col) for col in gdf.columns if col != geometry_col_name]
                self.column_selector.addItems(columns)
            except Exception as e:
                # If there's an issue getting column names, just return
                print(f"Error refreshing columns: {e}")
                return

    def update_input_with_current_value(self, selected_column):
        """Update the input field with the current value from the selected column"""
        if not selected_column:
            return

        gdf = self.data_handler.get_geodataframe()
        if gdf is None or len(gdf) == 0:
            return

        current_index = self.data_handler.get_current_index()
        if current_index < 0 or current_index >= len(gdf):
            return

        # Check if the selected column exists in the gdf
        if selected_column in gdf.columns:
            try:
                current_value = gdf.iloc[current_index][selected_column]
                # Only update if the field is empty or if we want to always update
                # Here we'll always update to show current value
                self.data_input.setText(str(current_value) if current_value is not None else "")
            except Exception as e:
                logger.warning(f"Could not get current value for column {selected_column}: {e}")

    def update_current_value_display(self):
        """Update the input field to show the current value at the current index for the selected column"""
        selected_column = self.column_selector.currentText()
        if not selected_column:
            return
        
        self.update_input_with_current_value(selected_column)

    def assign_data_and_move_next(self, move_next=True):
        """Assign data to the selected column and optionally move to the next point"""
        logger.debug(f"Starting assign_data_and_move_next method with move_next={move_next}")
        
        # Check if we have a valid index
        current_index = self.data_handler.get_current_index()
        gdf = self.data_handler.get_geodataframe()

        logger.debug(f"Current index: {current_index}")
        logger.debug(f"GDF is None: {gdf is None}")
        if gdf is not None:
            logger.debug(f"GDF length: {len(gdf) if gdf is not None else 'N/A'}")
            logger.debug(f"GDF columns: {list(gdf.columns) if gdf is not None else 'N/A'}")

        if gdf is None or len(gdf) == 0:
            logger.warning("No data loaded")
            self.status_label.setText("No data loaded")
            return

        if current_index < 0 or current_index >= len(gdf):
            logger.warning(f"Invalid index: {current_index}, GDF length: {len(gdf)}")
            self.status_label.setText("Invalid index")
            return

        # Get the selected column and data
        selected_column = self.column_selector.currentText()
        data_value = self.data_input.text().strip()

        logger.debug(f"Selected column: '{selected_column}'")
        logger.debug(f"Data value: '{data_value}'")
        logger.debug(f"Column in GDF columns: {selected_column in gdf.columns if gdf is not None else 'N/A'}")

        # Validate that a column is selected
        if not selected_column:
            logger.warning("No column selected")
            self.status_label.setText("Please select a column")
            return

        # Check if the selected column exists in the current gdf
        if selected_column not in gdf.columns:
            logger.error(f"Selected column '{selected_column}' not found in current GDF columns: {list(gdf.columns)}")
            self.status_label.setText(f"Column '{selected_column}' not found in current data")
            return

        try:
            # Get the column position
            col_pos = gdf.columns.get_loc(selected_column)
            logger.debug(f"Column position for '{selected_column}': {col_pos}")
            
            # Update the cell value in the data handler
            success = self.data_handler.update_cell_value(current_index, col_pos, data_value)
            logger.debug(f"Update cell value success: {success}")
            
            if success:
                message = f"Assigned '{data_value}' to column '{selected_column}' for point {current_index}"
                if move_next:
                    # Move to the next point
                    logger.debug("About to emit next_point_requested signal")
                    self.next_point_requested.emit()
                    logger.debug("Next point requested signal emitted")
                    message += ", moved to next point"
                
                logger.info(message)
                logger.debug("About to set status label text")
                self.status_label.setText(message)
                logger.debug("Status label text set successfully")
            else:
                error_msg = "Failed to update cell value"
                logger.error(error_msg)
                self.status_label.setText(error_msg)
        except Exception as e:
            error_msg = f"Error updating cell: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.status_label.setText(error_msg)

    def save_current_data(self):
        """Save the data in the input field without moving to the next point."""
        logger.debug("save_current_data called")
        self.assign_data_and_move_next(move_next=False)