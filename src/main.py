"""
Main application module for the Geospatial Data Viewer
"""
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFileDialog, QGroupBox, QFormLayout,
                             QLineEdit, QMessageBox, QSlider)
from PyQt5.QtCore import Qt

from data_handler import GeospatialDataHandler
from map_display import MapDisplayWidget
from table_display import TableDisplayWidget
from workflow import WorkflowManager


class GeospatialViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Geospatial Data Viewer")
        self.setGeometry(100, 100, 1400, 900)

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
        self.current_zoom_level = 5  # Default zoom level

        self.init_ui()

    def init_ui(self):
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Create splitter for left control panel and right map display
        from PyQt5.QtWidgets import QSplitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left control panel
        left_panel = self.create_control_panel()
        splitter.addWidget(left_panel)

        # Right map display
        right_panel = self.create_map_display()
        splitter.addWidget(right_panel)

        # Set the stretch factors
        splitter.setSizes([400, 1000])  # Left panel gets 400px, right gets remaining space

    def create_control_panel(self):
        # Left panel for controls
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)

        # File loading buttons
        file_group = QGroupBox("File Operations")
        file_layout = QVBoxLayout(file_group)

        self.load_shp_btn = QPushButton("Load SHP File")
        self.load_shp_btn.clicked.connect(self.load_shp_file)
        file_layout.addWidget(self.load_shp_btn)

        self.load_image_btn = QPushButton("Load Georeferenced JPG")
        self.load_image_btn.clicked.connect(self.load_georef_image)
        file_layout.addWidget(self.load_image_btn)

        control_layout.addWidget(file_group)

        # SHP table display
        table_group = QGroupBox("SHP Table Data")
        table_layout = QVBoxLayout(table_group)

        self.table_widget = TableDisplayWidget()
        self.table_widget.set_data_handler(self.data_handler)
        table_layout.addWidget(self.table_widget)

        control_layout.addWidget(table_group)

        # Navigation controls
        nav_group = QGroupBox("Navigation")
        nav_layout = QFormLayout(nav_group)

        self.id_input = QLineEdit()
        nav_layout.addRow("Current ID:", self.id_input)

        # Button to record the ID and move to next point
        self.record_id_btn = QPushButton("Record ID & Next")
        self.record_id_btn.clicked.connect(self.record_id_and_next)
        nav_layout.addRow(self.record_id_btn)

        self.goto_btn = QPushButton("Go to ID")
        self.goto_btn.clicked.connect(self.goto_id)
        nav_layout.addRow(self.goto_btn)

        self.next_btn = QPushButton("Next Point")
        self.next_btn.clicked.connect(self.next_point)
        nav_layout.addRow(self.next_btn)

        self.prev_btn = QPushButton("Previous Point")
        self.prev_btn.clicked.connect(self.previous_point)
        nav_layout.addRow(self.prev_btn)

        # Zoom level control
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(1)  # Will represent 0.1x (divided by 10)
        self.zoom_slider.setMaximum(50)  # Will represent 5.0x (divided by 10)
        self.zoom_slider.setValue(10)  # Default zoom level of 1.0x (10/10)
        self.zoom_slider.valueChanged.connect(self.zoom_level_changed)
        nav_layout.addRow("Zoom Level:", self.zoom_slider)

        # Zoom level label
        self.zoom_label = QLabel(f"Zoom: {self.zoom_slider.value()/10.0:.1f}x")
        nav_layout.addRow(self.zoom_label)

        # Workflow instructions
        self.workflow_label = QLabel("Workflow: Look at map → Write ID in field → Click 'Record ID & Next' → Next point auto-zooms")
        self.workflow_label.setWordWrap(True)
        nav_layout.addRow(self.workflow_label)

        control_layout.addWidget(nav_group)

        # Add stretch to push everything up
        control_layout.addStretch()

        return control_panel

    def create_map_display(self):
        # Right panel for map display
        map_panel = QWidget()
        map_layout = QVBoxLayout(map_panel)

        # Create map display widget
        self.map_widget = MapDisplayWidget()

        # Add widget to layout
        map_layout.addWidget(self.map_widget)

        # Add status label
        self.status_label = QLabel("Ready to load files")
        map_layout.addWidget(self.status_label)

        return map_panel

    def zoom_level_changed(self, value):
        """Update the zoom level when the slider changes"""
        # Convert slider value (1-50) to actual zoom (0.1x - 5.0x)
        self.current_zoom_level = value / 10.0
        self.zoom_label.setText(f"Zoom: {self.current_zoom_level:.1f}x")
        
    def load_shp_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open SHP File", "", "Shapefiles (*.shp);;All Files (*)"
        )

        if file_path:
            success, message = self.data_handler.load_shapefile(file_path)
            if success:
                # Initialize the workflow manager after data is loaded
                self.workflow_manager = WorkflowManager(
                    self.data_handler,
                    self.map_widget,
                    self.table_widget,
                    self.status_label
                )

                # Update the table display
                self.table_widget.update_table()

                # Update the map display
                self.update_map_display()

                self.status_label.setText(message)
            else:
                self.status_label.setText(message)

    def load_georef_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Georeferenced JPG", "", "Image Files (*.jpg *.jpeg *.tiff *.tif);;All Files (*)"
        )

        if file_path:
            success, message = self.data_handler.load_georef_image(file_path)
            if success:
                # Update the map display to show the image
                self.update_map_display()

                self.status_label.setText(message)
            else:
                self.status_label.setText(message)

    def update_map_display(self):
        # Update the map display
        self.map_widget.set_geodataframe(self.data_handler.get_geodataframe())
        # Pass both the image data and the dataset for proper georeferencing
        self.map_widget.set_image_data(self.data_handler.image_data, self.data_handler.image_dataset)
        self.map_widget.set_current_index(self.data_handler.get_current_index())
        self.map_widget.redraw()

    def record_id_and_next(self):
        """
        Record the ID for the current point and automatically move to the next point with zoom
        """
        if self.workflow_manager is None:
            self.status_label.setText("Please load a shapefile first")
            return

        id_value = self.id_input.text().strip()
        if not id_value:
            self.status_label.setText("Please enter an ID value")
            return

        self.workflow_manager.record_id_for_current_point(id_value)

    def goto_id(self):
        # Function to navigate to a specific ID
        # This would need to look up the row based on a specific ID field
        # For now, let's assume we're using the index as ID
        try:
            target_id = int(self.id_input.text())
            if self.data_handler.move_to_index(target_id):
                self.update_map_display()
                self.status_label.setText(f"Navigated to index {target_id}")
                
                # Zoom to the point with current zoom level
                current_point = self.data_handler.get_current_point()
                if current_point is not None:
                    try:
                        if hasattr(current_point.geometry, 'x') and hasattr(current_point.geometry, 'y'):
                            x, y = current_point.geometry.x, current_point.geometry.y
                        else:
                            centroid = current_point.geometry.centroid
                            x, y = centroid.x, centroid.y
                        # Use the actual zoom level (already converted in zoom_level_changed)
                        self.map_widget.zoom_to_point(x, y, self.current_zoom_level)
                    except:
                        pass  # If zoom fails, just continue
            else:
                self.status_label.setText(f"Index {target_id} is out of range")
        except ValueError:
            self.status_label.setText("Please enter a valid integer index")

    def next_point(self):
        if self.data_handler.move_next():
            self.update_map_display()
            self.status_label.setText(f"Moved to point {self.data_handler.get_current_index()}")

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
                    self.map_widget.zoom_to_point(x, y, self.current_zoom_level)
                except:
                    pass  # If zoom fails, just continue

    def previous_point(self):
        if self.data_handler.move_previous():
            self.update_map_display()
            self.status_label.setText(f"Moved to point {self.data_handler.get_current_index()}")

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
                    self.map_widget.zoom_to_point(x, y, self.current_zoom_level)
                except:
                    pass  # If zoom fails, just continue


def main():
    app = QApplication(sys.argv)
    viewer = GeospatialViewer()
    viewer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()