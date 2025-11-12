"""
Workflow module for managing the user workflow with better separation of concerns
"""
from PyQt5.QtWidgets import QMessageBox
from typing import Optional

import sys
import os
# Add the src directory to the path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import WorkflowConfig
from utils import get_geometry_coordinates
from constants import NO_SHAPEFILE_LOADED, NO_ID_ENTERED, NO_ID_COLUMN, RECORDED_ID_MESSAGE, ERROR_ZOOMING_MESSAGE


class IDRecorder:
    """Handles recording of IDs for current points"""
    
    def __init__(self, data_handler, table_widget):
        self.data_handler = data_handler
        self.table_widget = table_widget
        self.id_field_name = WorkflowConfig.DEFAULT_ID_FIELD_NAME

    def record_id_for_current_point(self, id_value: str) -> bool:
        """
        Record an ID for the current point
        
        Args:
            id_value: The ID value to record
            
        Returns:
            True if successful, False otherwise
        """
        if self.data_handler.gdf is None or len(self.data_handler.gdf) == 0:
            return False

        current_idx = self.data_handler.get_current_index()

        # Find the ID column in the GeoDataFrame
        id_col_index = None
        for i, col_name in enumerate(self.data_handler.gdf.columns):
            if col_name.upper() == self.id_field_name.upper():
                id_col_index = i
                break

        if id_col_index is not None:
            # Update the ID value in the GeoDataFrame
            self.data_handler.update_cell_value(current_idx, id_col_index, id_value)

            # Update the table display
            self.table_widget.update_table()

            return True
        else:
            # If no ID column exists, return False
            return False


class NavigationCoordinator:
    """Coordinates navigation and zooming between map and data handler"""
    
    def __init__(self, data_handler, map_widget):
        self.data_handler = data_handler
        self.map_widget = map_widget

    def move_to_next_point(self) -> bool:
        """
        Move to the next point in the dataset
        """
        if self.data_handler.move_next():
            # Update the map display
            self.map_widget.set_current_index(self.data_handler.get_current_index())
            self.map_widget.redraw()

            # Process the GUI events to ensure the redraw is complete
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()

            # Zoom to the current point immediately
            self.zoom_to_current_point()

            return True
        return False

    def zoom_to_current_point(self):
        """
        Zoom the map to the current point
        """
        # Get the current point AFTER the index has been updated
        current_point = self.data_handler.get_current_point()
        if current_point is not None:
            try:
                # Extract coordinates from the geometry using utility function
                x, y = get_geometry_coordinates(current_point.geometry)

                # Ensure the map is updated before zooming
                self.map_widget.redraw()

                # Now zoom to the point
                self.map_widget.zoom_to_point(x, y)
            except Exception as e:
                print(ERROR_ZOOMING_MESSAGE.format(error_message=str(e)))


class WorkflowManager:
    """
    Manages the workflow of looking at points, recording IDs, and navigating
    """
    def __init__(self, data_handler, map_widget, table_widget, status_label):
        self.data_handler = data_handler
        self.map_widget = map_widget
        self.table_widget = table_widget
        self.status_label = status_label

        # Initialize specialized components
        self.id_recorder = IDRecorder(data_handler, table_widget)
        self.navigation_coordinator = NavigationCoordinator(data_handler, map_widget)

        self.current_point_recorded = False

    def record_id_for_current_point(self, id_value: str) -> bool:
        """
        Record an ID for the current point and move to the next point
        """
        if self.data_handler.gdf is None or len(self.data_handler.gdf) == 0:
            self.status_label.setText(NO_SHAPEFILE_LOADED)
            return False

        if not id_value.strip():
            self.status_label.setText(NO_ID_ENTERED)
            return False

        # Record the ID
        success = self.id_recorder.record_id_for_current_point(id_value)
        if not success:
            self.status_label.setText(NO_ID_COLUMN.format(id_field_name=WorkflowConfig.DEFAULT_ID_FIELD_NAME))
            return False

        # Move to next point
        self.navigation_coordinator.move_to_next_point()

        self.status_label.setText(
            RECORDED_ID_MESSAGE.format(
                id_value=id_value, 
                current_idx=self.data_handler.get_current_index() - 1  # Previous index
            )
        )
        self.current_point_recorded = True
        return True