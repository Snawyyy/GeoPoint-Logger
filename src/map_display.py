"""
Map display module with separated visualization and coordinate handling logic
"""
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from rasterio.plot import show
import rasterio
import cv2
from typing import Optional

from .config import DataHandlerConfig
from .utils import get_geometry_coordinates, calculate_zoom_range


class CoordinateTransformer:
    """Handles coordinate transformations and projections"""
    
    def __init__(self):
        self.image_dataset = None
        self.gdf = None
    
    def set_image_dataset(self, image_dataset):
        """Set the image dataset for coordinate transformations"""
        self.image_dataset = image_dataset
    
    def set_geodataframe(self, gdf):
        """Set the geodataframe for coordinate transformations"""
        self.gdf = gdf
    
    def get_image_bounds(self):
        """Get the bounds of the image dataset"""
        if self.image_dataset:
            return self.image_dataset.bounds
        return None
    
    def get_shapefile_bounds(self):
        """Get the bounds of the shapefile"""
        if self.gdf is not None and not self.gdf.empty:
            return self.gdf.total_bounds
        return None


class MapVisualizer:
    """Handles the actual visualization of the map"""
    
    def __init__(self, width=DataHandlerConfig.DEFAULT_IMAGE_WIDTH, 
                 height=DataHandlerConfig.DEFAULT_IMAGE_HEIGHT, 
                 dpi=DataHandlerConfig.DEFAULT_IMAGE_DPI):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.image_datas = []
        self.original_image_datas = []
        self.image_datasets = []  # List of Rasterio datasets
        self.image_filenames = []
        self.image_visibility = {}
        self.gdf = None
        self.current_index = 0
        self.coordinate_transformer = CoordinateTransformer()

        # Image settings
        self.interpolation = "nearest"
        self.brightness = 50
        self.contrast = 50
        self.saturation = 50
        self.threshold = 0

    def set_image_data(self, image_datas, image_datasets=None, image_filenames=None):
        """Set the georeferenced image data and dataset from the data handler"""
        self.original_image_datas = image_datas
        self.image_datas = image_datas
        self.image_datasets = image_datasets
        self.image_filenames = image_filenames
        if image_datasets:
            self.coordinate_transformer.set_image_dataset(image_datasets[0])
        if image_filenames:
            for filename in image_filenames:
                self.image_visibility[filename] = True

    def set_geodataframe(self, gdf):
        """Set the GeoDataFrame to display"""
        self.gdf = gdf
        self.coordinate_transformer.set_geodataframe(gdf)
        
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

    def _apply_image_settings(self, img):
        """Apply the current image settings to the given image"""
        if img is None:
            return None

        img = img.copy().astype(np.float32)

        # Brightness and Contrast
        if self.brightness != 50 or self.contrast != 50:
            brightness = (self.brightness - 50) * 2
            contrast = self.contrast / 50.0
            img = img * contrast + brightness
            img = np.clip(img, 0, 255)

        img = img.astype(np.uint8)

        # Saturation
        if self.saturation != 50:
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
            h, s, v = cv2.split(hsv)
            saturation_factor = self.saturation / 50.0
            s = s * saturation_factor
            s = np.clip(s, 0, 255)
            final_hsv = cv2.merge((h, s, v))
            img = cv2.cvtColor(final_hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

        # Threshold
        if self.threshold > 0:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, img = cv2.threshold(gray, self.threshold, 255, cv2.THRESH_BINARY)
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) # Convert back to BGR to keep color channels

        return img

    def set_interpolation(self, interpolation: str):
        """Set the interpolation method"""
        self.interpolation = interpolation.lower()
        self.redraw()

    def set_brightness(self, value: int):
        """Set the brightness level"""
        self.brightness = value
        self.redraw()

    def set_contrast(self, value: int):
        """Set the contrast level"""
        self.contrast = value
        self.redraw()

    def set_saturation(self, value: int):
        """Set the saturation level"""
        self.saturation = value
        self.redraw()

    def set_threshold(self, value: int):
        """Set the threshold level"""
        self.threshold = value
        self.redraw()

    def set_image_visibility(self, filename: str, visible: bool):
        """Set the visibility of an image layer."""
        self.image_visibility[filename] = visible
        self.redraw()

    def draw_image(self, ax):
        """Draw the georeferenced images on the given axes"""
        if not self.image_datasets:
            return

        for i, image_dataset in enumerate(self.image_datasets):
            filename = self.image_filenames[i]
            if not self.image_visibility.get(filename, True):
                continue

            if image_dataset is not None:
                img = self._apply_image_settings(self.original_image_datas[i])
                if img is None:
                    continue

                h, w = img.shape[:2]
                t = image_dataset.transform
                from matplotlib.transforms import Affine2D
                M = Affine2D.from_values(t.a, t.b, t.d, t.e, t.c, t.f)
                ax.imshow(
                    img,
                    origin="upper",
                    interpolation=self.interpolation,
                    transform=M + ax.transData,
                    resample=True,
                )
                corners_px = [(0, 0), (w, 0), (w, h), (0, h)]
                corners_xy = [t * (x, y) for (x, y) in corners_px]
                xs, ys = zip(*corners_xy)
                ax.set_xlim(min(xs), max(xs))
                ax.set_ylim(min(ys), max(ys))
            elif self.image_datas[i] is not None:
                ax.imshow(self.image_datas[i])

    def draw_shapefile(self, ax):
        """Draw the shapefile data on the given axes"""
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
            if self.image_datasets and self.image_datasets[0] and hasattr(self.image_datasets[0], 'crs') and self.image_datasets[0].crs:
                img_crs = self.image_datasets[0].crs
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

    def redraw(self):
        """Redraw the map with current data"""
        ax = self.figure.get_axes()[0] if self.figure.get_axes() else None
        if ax:
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()

        # Clear the previous plot
        self.figure.clear()

        # Create subplot
        ax = self.figure.add_subplot(111)

        # Show georeferenced image if available
        self.draw_image(ax)

        # Plot shapefile if available
        self.draw_shapefile(ax)

        # Set equal aspect ratio to prevent stretching
        ax.set_aspect('equal', adjustable='box')

        if 'xlim' in locals() and 'ylim' in locals():
            ax.set_xlim(xlim)
            ax.set_ylim(ylim)

        # Update the canvas
        self.figure.tight_layout()
        self.figure.canvas.draw()

    def zoom_to_point(self, x: float, y: float, zoom_factor: float = 2.0):
        """
        Zoom the view to a specific point, maintaining proper coordinate system alignment
        """
        ax = self.figure.get_axes()[0] if self.figure.get_axes() else self.figure.add_subplot(111)

        # Calculate an appropriate zoom range based on the coordinate system
        base_range_x = 500.0  # 500 meters default for Israeli Grid
        base_range_y = 500.0  # 500 meters default for Israeli Grid

        # Calculate ranges based on zoom factor using utility function
        xlim_range, ylim_range = calculate_zoom_range(
            base_range_x, 
            base_range_y, 
            zoom_factor, 
            min_range=1.0
        )

        # Set new limits centered on the point
        ax.set_xlim(x - xlim_range/2, x + xlim_range/2)
        ax.set_ylim(y - ylim_range/2, y + ylim_range/2)  # Standard y-axis orientation
        self.figure.canvas.draw()


class MapDisplayWidget(FigureCanvas):
    """
    Widget for displaying maps and geospatial data with proper coordinate alignment
    """
    def __init__(self, width=DataHandlerConfig.DEFAULT_IMAGE_WIDTH, 
                 height=DataHandlerConfig.DEFAULT_IMAGE_HEIGHT, 
                 dpi=DataHandlerConfig.DEFAULT_IMAGE_DPI):
        self.map_visualizer = MapVisualizer(width, height, dpi)
        self.figure = self.map_visualizer.figure
        super().__init__(self.figure)

    def set_image_data(self, image_datas, image_datasets=None, image_filenames=None):
        """Set the georeferenced image data and dataset from the data handler"""
        self.map_visualizer.set_image_data(image_datas, image_datasets, image_filenames)

    def set_geodataframe(self, gdf):
        """Set the GeoDataFrame to display"""
        self.map_visualizer.set_geodataframe(gdf)

    def set_current_index(self, index):
        """Set the current index for highlighting the current point"""
        self.map_visualizer.set_current_index(index)

    def redraw(self):
        """Redraw the map with current data"""
        self.map_visualizer.redraw()

    def zoom_to_point(self, x: float, y: float, zoom_factor: float = 2.0):
        """Zoom the map to a specific point"""
        self.map_visualizer.zoom_to_point(x, y, zoom_factor)

    def set_interpolation(self, interpolation: str):
        """Set the interpolation method"""
        self.map_visualizer.set_interpolation(interpolation)

    def set_brightness(self, value: int):
        """Set the brightness level"""
        self.map_visualizer.set_brightness(value)

    def set_contrast(self, value: int):
        """Set the contrast level"""
        self.map_visualizer.set_contrast(value)

    def set_saturation(self, value: int):
        """Set the saturation level"""
        self.map_visualizer.set_saturation(value)

    def set_threshold(self, value: int):
        """Set the threshold level"""
        self.map_visualizer.set_threshold(value)

    def set_image_visibility(self, filename: str, visible: bool):
        """Set the visibility of an image layer."""
        self.map_visualizer.set_image_visibility(filename, visible)