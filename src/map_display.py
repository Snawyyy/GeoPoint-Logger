"""
Map display module for rendering geospatial data
"""
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class MapDisplayWidget(FigureCanvas):
    """
    Widget for displaying maps and geospatial data
    """
    def __init__(self, width=10, height=8, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.figure)
        
        self.image_data = None
        self.gdf = None
        self.current_index = 0
        
    def set_image_data(self, image_data):
        """Set the georeferenced image data to display"""
        self.image_data = image_data
        
    def set_geodataframe(self, gdf):
        """Set the GeoDataFrame to display"""
        self.gdf = gdf
        
    def set_current_index(self, index):
        """Set the current index for highlighting the current point"""
        self.current_index = index
        
    def redraw(self):
        """Redraw the map with current data"""
        # Clear the previous plot
        self.figure.clear()
        
        # Create subplot
        ax = self.figure.add_subplot(111)
        
        # Show image if available
        if self.image_data is not None:
            ax.imshow(self.image_data)
        
        # Plot shapefile if available
        if self.gdf is not None and len(self.gdf) > 0:
            # Plot all points (this will handle different geometry types)
            self.gdf.plot(ax=ax, color='red', markersize=50, alpha=0.7)
            
            # Highlight the current point if valid
            if 0 <= self.current_index < len(self.gdf):
                current_row = self.gdf.iloc[self.current_index]
                geom = current_row.geometry
                
                # Handle different geometry types
                if geom.geom_type == 'Point':
                    ax.plot(geom.x, geom.y, 'bo', markersize=8, label=f'Current: {self.current_index}')
                else:
                    # For non-point geometries, plot the centroid
                    centroid = geom.centroid
                    ax.plot(centroid.x, centroid.y, 'bo', markersize=8, label=f'Current: {self.current_index}')
                
                ax.legend()
        
        # Update the canvas
        self.figure.tight_layout()
        self.draw()
    
    def zoom_to_point(self, x, y, zoom_factor=2):
        """
        Zoom the view to a specific point
        """
        # Calculate new axes limits centered on the point
        ax = self.figure.get_axes()[0] if self.figure.get_axes() else self.figure.add_subplot(111)
        
        # Get current axis limits to determine the current range
        current_xlim = ax.get_xlim()
        current_ylim = ax.get_ylim()
        
        # Calculate range for zoom
        xlim_range = (current_xlim[1] - current_xlim[0]) / zoom_factor
        ylim_range = (current_ylim[1] - current_ylim[0]) / zoom_factor
        
        # Set new limits centered on the point
        ax.set_xlim(x - xlim_range/2, x + xlim_range/2)
        ax.set_ylim(y - ylim_range/2, y + ylim_range/2)  # Standard y-axis orientation
        self.draw()