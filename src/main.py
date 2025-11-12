"""
Main application module for the Geospatial Data Viewer with improved modularity
"""
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFileDialog, QGroupBox, QFormLayout,
                             QLineEdit, QMessageBox, QSlider, QSplitter)
from PyQt5.QtCore import Qt

import sys
import os
# Add the src directory to the path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import UIConfig, FileExtensionsConfig
from constants import *
from data_handler import GeospatialDataHandler
from map_display import MapDisplayWidget
from table_display import TableDisplayWidget
from workflow import WorkflowManager


class FileLoader:
    """Handles file loading operations"""
    
    def __init__(self, data_handler, status_label, table_widget, map_widget):
        self.data_handler = data_handler
        self.status_label = status_label
        self.table_widget = table_widget
        self.map_widget = map_widget

    def load_shp_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Open SHP File", "", FileExtensionsConfig.SHAPEFILE_EXTENSIONS
        )

        if file_path:
            success, message = self.data_handler.load_shapefile(file_path)
            if success:
                # Update the table display
                self.table_widget.update_table()

                # Update the map display
                self._update_map_display()

                self.status_label.setText(message)
            else:
                self.status_label.setText(message)

    def load_georef_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Open Georeferenced JPG", "", FileExtensionsConfig.IMAGE_EXTENSIONS
        )

        if file_path:
            success, message = self.data_handler.load_georef_image(file_path)
            if success:
                # Update the map display to show the image
                self._update_map_display()

                self.status_label.setText(message)
            else:
                self.status_label.setText(message)
    
    def _update_map_display(self):
        """Update the map display with current data"""
        self.map_widget.set_geodataframe(self.data_handler.get_geodataframe())
        # Pass both the image data and the dataset for proper georeferencing
        self.map_widget.set_image_data(self.data_handler.image_loader.image_data, 
                                      self.data_handler.image_loader.image_dataset)
        self.map_widget.set_current_index(self.data_handler.get_current_index())
        self.map_widget.redraw()


class NavigationManager:
    """Manages navigation between points with automatic zooming"""
    
    def __init__(self, data_handler, map_widget, status_label, id_input, update_map_func):
        self.data_handler = data_handler
        self.map_widget = map_widget
        self.status_label = status_label
        self.id_input = id_input
        self.update_map_func = update_map_func

    def goto_id(self, zoom_level):
        """Navigate to a specific ID"""
        try:
            target_id = int(self.id_input.text())
            if self.data_handler.move_to_index(target_id):
                # Update map display
                self.update_map_func(self.map_widget, self.data_handler)
                
                self.status_label.setText(NAVIGATED_TO_INDEX.format(target_id=target_id))

                # Zoom to the point with current zoom level
                current_point = self.data_handler.get_current_point()
                if current_point is not None:
                    try:
                        if hasattr(current_point.geometry, 'x') and hasattr(current_point.geometry, 'y'):
                            x, y = current_point.geometry.x, current_point.geometry.y
                        else:
                            centroid = current_point.geometry.centroid
                            x, y = centroid.x, centroid.y
                        # Use the actual zoom level
                        self.map_widget.zoom_to_point(x, y, zoom_level)
                    except:
                        pass  # If zoom fails, just continue
            else:
                self.status_label.setText(INDEX_OUT_OF_RANGE.format(target_id=target_id))
        except ValueError:
            self.status_label.setText(INVALID_INDEX)

    def next_point(self, zoom_level):
        """Navigate to the next point"""
        if self.data_handler.move_next():
            # Update map display
            self.update_map_func(self.map_widget, self.data_handler)
            
            self.status_label.setText(MOVED_TO_POINT.format(point_index=self.data_handler.get_current_index()))

            # Update ID field to show current index
            self.id_input.setText(str(self.data_handler.get_current_index()))

            # Zoom to the current point using the selected zoom level
            current_point = self.data_handler.get_current_point()
            if current_point is not None:
                try:
                    if hasattr(current_point.geometry, 'x') and hasattr(current_point.geometry, 'y'):
                        x, y = current_point.geometry.x, current_point.geometry.y
                    else:
                        centroid = current_point.geometry.centroid
                        x, y = centroid.x, centroid.y
                    self.map_widget.zoom_to_point(x, y, zoom_level)
                except:
                    pass  # If zoom fails, just continue

    def previous_point(self, zoom_level):
        """Navigate to the previous point"""
        if self.data_handler.move_previous():
            # Update map display
            self.update_map_func(self.map_widget, self.data_handler)
            
            self.status_label.setText(MOVED_TO_POINT.format(point_index=self.data_handler.get_current_index()))

            # Update ID field to show current index
            self.id_input.setText(str(self.data_handler.get_current_index()))

            # Zoom to the current point using the selected zoom level
            current_point = self.data_handler.get_current_point()
            if current_point is not None:
                try:
                    if hasattr(current_point.geometry, 'x') and hasattr(current_point.geometry, 'y'):
                        x, y = current_point.geometry.x, current_point.geometry.y
                    else:
                        centroid = current_point.geometry.centroid
                        x, y = centroid.x, centroid.y
                    self.map_widget.zoom_to_point(x, y, zoom_level)
                except:
                    pass  # If zoom fails, just continue


def update_map_display(map_widget, data_handler):
    """Helper function to update the map display with current data"""
    map_widget.set_geodataframe(data_handler.get_geodataframe())
    # Pass both the image data and the dataset for proper georeferencing
    map_widget.set_image_data(
        data_handler.image_loader.image_data, 
        data_handler.image_loader.image_dataset
    )
    map_widget.set_current_index(data_handler.get_current_index())
    map_widget.redraw()


class GeospatialViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setGeometry(
            UIConfig.WINDOW_X_POSITION, 
            UIConfig.WINDOW_Y_POSITION, 
            UIConfig.WINDOW_WIDTH, 
            UIConfig.WINDOW_HEIGHT
        )

        # Initialize data handler
        self.data_handler = GeospatialDataHandler()

        # Initialize UI components
        self.map_widget = None
        self.table_widget = None
        self.status_label = None
        self.id_input = None

        # Initialize workflow manager
        self.workflow_manager = None

        # Initialize zoom level
        self.current_zoom_level = UIConfig.DEFAULT_ZOOM_LEVEL  # Default zoom level

        self.file_loader = None
        self.navigation_manager = None

        self.init_ui()

    def init_ui(self):
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Create splitter for left map display and right control panel
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left map display
        left_panel = self.create_map_display()
        splitter.addWidget(left_panel)

        # Right control panel (contains file operations at top and table below)
        right_panel = self.create_control_panel()
        splitter.addWidget(right_panel)

        # Set the sizes using configuration
        splitter.setSizes([UIConfig.MAP_PANEL_SIZE, UIConfig.CONTROL_PANEL_SIZE])

    def create_control_panel(self):
        # Right panel for controls (file operations and navigation at top, table below)
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)

        # Create a vertical layout for the top section (file operations and navigation)
        top_section = QWidget()
        top_layout = QVBoxLayout(top_section)

        # File loading buttons
        file_group = QGroupBox(FILE_OPERATIONS_GROUP_TITLE)
        file_layout = QVBoxLayout(file_group)

        self.load_shp_btn = QPushButton(LOAD_SHP_BUTTON_TEXT)
        file_layout.addWidget(self.load_shp_btn)

        self.load_image_btn = QPushButton(LOAD_IMAGE_BUTTON_TEXT)
        file_layout.addWidget(self.load_image_btn)

        top_layout.addWidget(file_group)

        # Navigation controls
        nav_group = QGroupBox(NAVIGATION_GROUP_TITLE)
        nav_layout = QFormLayout(nav_group)

        self.id_input = QLineEdit()
        nav_layout.addRow("Current ID:", self.id_input)

        # Button to record the ID and move to next point
        self.record_id_btn = QPushButton(RECORD_ID_BUTTON_TEXT)
        nav_layout.addRow(self.record_id_btn)

        self.goto_btn = QPushButton(GOTO_BUTTON_TEXT)
        nav_layout.addRow(self.goto_btn)

        self.next_btn = QPushButton(NEXT_BUTTON_TEXT)
        nav_layout.addRow(self.next_btn)

        self.prev_btn = QPushButton(PREV_BUTTON_TEXT)
        nav_layout.addRow(self.prev_btn)

        # Zoom level control
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(UIConfig.MIN_ZOOM_LEVEL)
        self.zoom_slider.setMaximum(UIConfig.MAX_ZOOM_LEVEL)
        self.zoom_slider.setValue(UIConfig.DEFAULT_ZOOM_LEVEL)
        nav_layout.addRow("Zoom Level:", self.zoom_slider)

        # Zoom level label
        self.zoom_label = QLabel(ZOOM_DISPLAY_FORMAT.format(zoom_level=self.zoom_slider.value()))
        nav_layout.addRow(self.zoom_label)

        # Workflow instructions
        self.workflow_label = QLabel(WORKFLOW_INSTRUCTIONS)
        self.workflow_label.setWordWrap(True)
        nav_layout.addRow(self.workflow_label)

        top_layout.addWidget(nav_group)

        # Add the top section (file ops and navigation) to the main control layout
        control_layout.addWidget(top_section)

        # SHP table display (lower section)
        table_group = QGroupBox(SHP_TABLE_GROUP_TITLE)
        table_layout = QVBoxLayout(table_group)

        self.table_widget = TableDisplayWidget()
        self.table_widget.set_data_handler(self.data_handler)
        table_layout.addWidget(self.table_widget)

        control_layout.addWidget(table_group)

        # Initialize the file loader after components are created
        self.file_loader = FileLoader(self.data_handler, self.status_label, self.table_widget, self.map_widget)
        
        # Initialize navigation manager after components are available
        self.navigation_manager = NavigationManager(
            self.data_handler, 
            self.map_widget, 
            self.status_label, 
            self.id_input,
            update_map_display
        )
        
        # Connect signals
        self.load_shp_btn.clicked.connect(self.file_loader.load_shp_file)
        self.load_image_btn.clicked.connect(self.file_loader.load_georef_image)
        self.goto_btn.clicked.connect(lambda: self.navigation_manager.goto_id(self.current_zoom_level))
        self.next_btn.clicked.connect(lambda: self.navigation_manager.next_point(self.current_zoom_level))
        self.prev_btn.clicked.connect(lambda: self.navigation_manager.previous_point(self.current_zoom_level))
        
        # Connect record ID button after workflow manager is initialized
        self.record_id_btn.clicked.connect(self.record_id_and_next)
        
        # Connect zoom level changes
        self.zoom_slider.valueChanged.connect(self.zoom_level_changed)

        return control_panel

    def create_map_display(self):
        # Left panel for map display
        map_panel = QWidget()
        map_layout = QVBoxLayout(map_panel)

        # Create map display widget
        self.map_widget = MapDisplayWidget()

        # Add widget to layout
        map_layout.addWidget(self.map_widget)

        # Add status label
        self.status_label = QLabel(READY_STATUS)
        map_layout.addWidget(self.status_label)

        return map_panel

    def zoom_level_changed(self, value):
        """Update the zoom level when the slider changes"""
        self.current_zoom_level = value
        self.zoom_label.setText(ZOOM_DISPLAY_FORMAT.format(zoom_level=self.current_zoom_level))

    def record_id_and_next(self):
        """
        Record the ID for the current point and automatically move to the next point with zoom
        """
        if self.workflow_manager is None:
            self.status_label.setText(NO_SHAPEFILE_LOADED)
            return

        id_value = self.id_input.text().strip()
        if not id_value:
            self.status_label.setText(NO_ID_ENTERED)
            return

        self.workflow_manager.record_id_for_current_point(id_value)

    def load_shp_file(self):
        """Load a shapefile - wrapper method for UI connection"""
        self.file_loader.load_shp_file()
        # Initialize the workflow manager after data is loaded
        if self.data_handler.get_geodataframe() is not None:
            self.workflow_manager = WorkflowManager(
                self.data_handler,
                self.map_widget,
                self.table_widget,
                self.status_label
            )

    def load_georef_image(self):
        """Load a georeferenced image - wrapper method for UI connection"""
        self.file_loader.load_georef_image()


def main():
    app = QApplication(sys.argv)
    viewer = GeospatialViewer()
    viewer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()