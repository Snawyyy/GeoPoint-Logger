"""
Map display module from scratch using rasterio for proper geospatial alignment
"""
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from rasterio.plot import show
import rasterio


class MapDisplayWidget(FigureCanvas):
    """
    Widget for displaying maps and geospatial data with proper coordinate alignment
    """
    def __init__(self, width=10, height=8, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.figure)
        
        self.image_data = None
        self.image_dataset = None  # Rasterio dataset
        self.gdf = None
        self.current_index = 0

    def set_image_data(self, image_data, image_dataset=None):
        """Set the georeferenced image data and dataset from the data handler"""
        # The image data is already processed by the data handler
        self.image_data = image_data
        # The dataset is passed from the data handler if available
        self.image_dataset = image_dataset

    def set_geodataframe(self, gdf):
        """Set the GeoDataFrame to display"""
        self.gdf = gdf
        # Print coordinate system info if available
        if hasattr(gdf, 'crs') and gdf.crs is not None:
            print(f"SHP Coordinate System: {gdf.crs}")
        
        # Print bounds of the shapefile
        if gdf is not None and not gdf.empty:
            bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
            print(f"SHP Bounds: minx={bounds[0]:.2f}, miny={bounds[1]:.2f}, maxx={bounds[2]:.2f}, maxy={bounds[3]:.2f}")

    def set_current_index(self, index):
        """Set the current index for highlighting the current point"""
        self.current_index = index

    def redraw(self):
        """Redraw the map with current data"""
        # Clear the previous plot
        self.figure.clear()

        # Create subplot
        ax = self.figure.add_subplot(111)

        # Show georeferenced image if available
        if self.image_dataset is not None:
            # Use the image array you already keep
            img = self.image_data
            h, w = img.shape[:2]

            # Rasterio affine (maps (col,row) -> (x,y))
            t = self.image_dataset.transform

            # Build a Matplotlib data-space transform
            from matplotlib.transforms import Affine2D
            M = Affine2D.from_values(t.a, t.b, t.d, t.e, t.c, t.f)  # [[a b c],[d e f],[0 0 1]]

            # Draw with rotation/shear applied in map coordinates
            ax.imshow(
                img,
                origin="upper",
                interpolation="nearest",
                transform=M + ax.transData,
                resample=True,
            )

            # Ensure axes cover the rotated footprint (four corners in map coords)
            corners_px = [(0, 0), (w, 0), (w, h), (0, h)]
            corners_xy = [t * (x, y) for (x, y) in corners_px]
            xs, ys = zip(*corners_xy)
            ax.set_xlim(min(xs), max(xs))
            ax.set_ylim(min(ys), max(ys))
            
            # Print image CRS and bounds for debugging
            print(f"Image CRS: {self.image_dataset.crs}")
            print(f"Image Bounds: {self.image_dataset.bounds}")
        elif self.image_data is not None:
            # Fallback to regular imshow if no dataset
            # This will show the image at 0,0 without georeferencing
            ax.imshow(self.image_data)
            print("Displaying image without georeferencing (no dataset)")

        # Plot shapefile if available
        if self.gdf is not None and len(self.gdf) > 0:
            # Print shapefile bounds for comparison
            if self.gdf.crs:
                print(f"Shapefile CRS: {self.gdf.crs}")
            bounds = self.gdf.total_bounds
            print(f"Shapefile bounds: minx={bounds[0]:.2f}, miny={bounds[1]:.2f}, maxx={bounds[2]:.2f}, maxy={bounds[3]:.2f}")
            
            # Plot in the same coordinate system as the image
            # Reproject shapefile to match image CRS if needed
            gdf_to_plot = self.gdf
            
            # If both image and shapefile have CRS, try to align them
            if self.image_dataset and hasattr(self.image_dataset, 'crs') and self.image_dataset.crs:
                img_crs = self.image_dataset.crs
                if self.gdf.crs and self.gdf.crs != img_crs:
                    # Reproject shapefile to match image CRS
                    try:
                        gdf_to_plot = self.gdf.to_crs(img_crs)
                        print(f"Reprojected shapefile from {self.gdf.crs} to {img_crs}")
                    except Exception as e:
                        print(f"Could not reproject shapefile: {e}")
                        print(f"Using original shapefile CRS: {self.gdf.crs}")
                        gdf_to_plot = self.gdf  # Use original if reprojection fails
                else:
                    print(f"Image and shapefile both use CRS: {img_crs}")
            else:
                print("No valid CRS found for image or shapefile")
            
            # Plot the shapefile data
            gdf_to_plot.plot(ax=ax, color='red', markersize=50, alpha=0.7)

            # Highlight the current point if valid
            if 0 <= self.current_index < len(gdf_to_plot):
                current_row = gdf_to_plot.iloc[self.current_index]
                geom = current_row.geometry

                # Handle different geometry types
                if geom.geom_type == 'Point':
                    ax.plot(geom.x, geom.y, 'bo', markersize=8, label=f'Current: {self.current_index}')
                else:
                    # For non-point geometries, plot the centroid
                    centroid = geom.centroid
                    ax.plot(centroid.x, centroid.y, 'bo', markersize=8, label=f'Current: {self.current_index}')

                ax.legend()

        # Set equal aspect ratio to prevent stretching
        ax.set_aspect('equal', adjustable='box')
        
        # Update the canvas
        self.figure.tight_layout()
        self.draw()

    def zoom_to_point(self, x, y, zoom_factor=2):
        """
        Zoom the view to a specific point, maintaining proper coordinate system alignment
        """
        ax = self.figure.get_axes()[0] if self.figure.get_axes() else self.figure.add_subplot(111)

        # Calculate an appropriate zoom range based on the coordinate system
        base_range_x = 500.0  # 500 meters default for Israeli Grid
        base_range_y = 500.0  # 500 meters default for Israeli Grid

        # Calculate ranges based on zoom factor (higher zoom_factor = closer zoom, smaller range)
        xlim_range = base_range_x / zoom_factor
        ylim_range = base_range_y / zoom_factor

        # Ensure minimum zoom range to avoid excessive zooming
        min_range = 1.0  # Minimum 1 meter range
        xlim_range = max(xlim_range, min_range)
        ylim_range = max(ylim_range, min_range)

        # Set new limits centered on the point
        ax.set_xlim(x - xlim_range/2, x + xlim_range/2)
        ax.set_ylim(y - ylim_range/2, y + ylim_range/2)  # Standard y-axis orientation
        self.draw()