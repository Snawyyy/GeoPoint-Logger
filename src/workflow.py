"""
Workflow module for managing the user workflow of looking at points,
recording IDs, and navigating to next points
"""
from PyQt5.QtWidgets import QMessageBox


class WorkflowManager:
    """
    Manages the workflow of looking at points, recording IDs, and navigating
    """
    def __init__(self, data_handler, map_widget, table_widget, status_label):
        self.data_handler = data_handler
        self.map_widget = map_widget
        self.table_widget = table_widget
        self.status_label = status_label
        
        # Store the ID field name to update
        self.id_field_name = "ID"  # Default, may be configurable later
        self.current_point_recorded = False
        
    def record_id_for_current_point(self, id_value):
        """
        Record an ID for the current point and move to the next point
        """
        if self.data_handler.gdf is None or len(self.data_handler.gdf) == 0:
            self.status_label.setText("No data loaded")
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
            
            # Move to next point
            self.move_to_next_point()
            
            self.status_label.setText(f"Recorded ID {id_value} for point {current_idx}, moved to next point")
            self.current_point_recorded = True
            return True
        else:
            # If no ID column exists, notify user
            self.status_label.setText(f"No '{self.id_field_name}' column found in data")
            return False
    
    def move_to_next_point(self):
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
                # Extract coordinates from the geometry
                # Handle both point and other geometry types
                if hasattr(current_point.geometry, 'x') and hasattr(current_point.geometry, 'y'):
                    # It's a point geometry
                    x, y = current_point.geometry.x, current_point.geometry.y
                else:
                    # Get the centroid for other geometry types
                    centroid = current_point.geometry.centroid
                    x, y = centroid.x, centroid.y
                
                # Ensure the map is updated before zooming
                self.map_widget.redraw()
                
                # Now zoom to the point
                self.map_widget.zoom_to_point(x, y)
            except Exception as e:
                self.status_label.setText(f"Error zooming to point: {str(e)}")