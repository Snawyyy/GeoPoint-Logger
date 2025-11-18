import sys
import numpy as np
import rasterio
from rasterio.plot import reshape_as_image
from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QFileDialog, QMessageBox
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.transforms import Affine2D
import geopandas as gpd


def _rgb_from_raster(ds):
    """
    Return an (H,W,3 or 4) uint8 RGB(A) array from a rasterio dataset.
    Handles:
      - single-band (grayscale)
      - 3-band RGB
      - 4-band RGBA (or RGB + alpha)
    Scales to 0-255 if needed.
    """
    count = ds.count
    if count == 1:
        arr = ds.read(1)
        # normalize to 0-255
        a_min, a_max = np.nanmin(arr), np.nanmax(arr)
        if a_max == a_min:
            img = np.zeros((arr.shape[0], arr.shape[1], 3), dtype=np.uint8)
        else:
            norm = (arr - a_min) / (a_max - a_min)
            img = (norm * 255).astype(np.uint8)
            img = np.repeat(img[..., None], 3, axis=2)
        return img

    # Try to find RGB(A) bands (common convention 1=R,2=G,3=B,4=A)
    if count >= 3:
        rgb = ds.read([1, 2, 3], out_dtype="uint8", masked=True)
        img = reshape_as_image(rgb.filled(0))
        if count >= 4:
            alpha = ds.read(4, out_dtype="uint8", masked=True).filled(255)
            img = np.dstack([img, alpha])
        return img

    # Fallback: read all bands and take first three
    data = ds.read(out_dtype="uint8", masked=True).filled(0)
    img = reshape_as_image(data)
    if img.shape[2] == 1:
        img = np.repeat(img, 3, axis=2)
    if img.shape[2] > 4:
        img = img[:, :, :4]
    return img


def rotate_points(cx, cy, pts, angle_deg):
    """Rotate iterable of (x,y) around (cx,cy) by angle_deg; return list of (x',y')."""
    theta = np.deg2rad(angle_deg)
    c, s = np.cos(theta), np.sin(theta)
    out = []
    for x, y in pts:
        xr = c * (x - cx) - s * (y - cy) + cx
        yr = s * (x - cx) + c * (y - cy) + cy
        out.append((xr, yr))
    return out


class MapCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(layout="constrained")
        super().__init__(fig)
        self.setParent(parent)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_aspect("equal")
        self.image_artist = None
        self.shape_artists = []
        self.raster_bounds = None
        self.center = None
        self.rotation_deg = 0.0
        self.gdf = None
        self.raster_crs = None
        self.gdf_crs = None
        self.extent = None

    def clear_all(self):
        self.ax.clear()
        self.image_artist = None
        self.shape_artists = []
        self.raster_bounds = None
        self.center = None
        self.rotation_deg = 0.0
        self.gdf = None
        self.raster_crs = None
        self.gdf_crs = None
        self.extent = None
        self.ax.set_aspect("equal")
        self.draw_idle()

    def set_raster(self, path):
        try:
            ds = rasterio.open(path)
        except Exception as e:
            raise RuntimeError(f"Failed to open raster: {e}")

        img = _rgb_from_raster(ds)

        # georeferenced extent
        b = ds.bounds  # left, bottom, right, top
        self.extent = (b.left, b.right, b.bottom, b.top)
        self.raster_bounds = b
        self.center = ((b.left + b.right) / 2.0, (b.bottom + b.top) / 2.0)
        self.raster_crs = ds.crs

        self.ax.clear()
        self.ax.set_aspect("equal")

        # origin='upper' so row 0 is at top (usual for rasters)
        self.image_artist = self.ax.imshow(img, extent=self.extent, origin='upper')
        self.ax.set_title("Raster + Shapefile (rotates together)")
        self._apply_rotation_to_artists()
        self._autoscale_to_rotated_extent()
        self.draw_idle()
        ds.close()

    def set_shapefile(self, path):
        try:
            gdf = gpd.read_file(path)
        except Exception as e:
            raise RuntimeError(f"Failed to open shapefile: {e}")

        self.gdf = gdf
        self.gdf_crs = getattr(gdf, "crs", None)

        # Reproject shapefile to raster CRS if needed (when raster is already loaded)
        if self.raster_crs is not None and self.gdf_crs is not None and self.gdf_crs != self.raster_crs:
            try:
                gdf = gdf.to_crs(self.raster_crs)
            except Exception as e:
                raise RuntimeError(f"Failed to reproject shapefile to raster CRS: {e}")

        # Remove old artists
        for art in self.shape_artists:
            art.remove()
        self.shape_artists = []

        # Plot new (no facecolor for polygons, visible edges)
        # Keep it simple & legible by default:
        self.ax.set_aspect("equal")
        art = gdf.plot(ax=self.ax, facecolor='none', edgecolor='yellow', linewidth=1.6, zorder=10)
        # `geopandas.plot` can return an Axes; we need the artists it added:
        # easiest is to fetch the last lines/collections from the axes after plotting.
        # We'll grab all top-level collections that were just added.
        # (Pragmatic approach: just take all collections; fine for a quick tool.)
        self.shape_artists = list(self.ax.collections)

        self._apply_rotation_to_artists()
        self._autoscale_to_rotated_extent()
        self.draw_idle()

    def set_rotation(self, angle_deg: float):
        self.rotation_deg = float(angle_deg)
        self._apply_rotation_to_artists()
        self._autoscale_to_rotated_extent()
        self.draw_idle()

    def _apply_rotation_to_artists(self):
        if self.center is None:
            return
        cx, cy = self.center
        t = Affine2D().rotate_deg_around(cx, cy, self.rotation_deg)

        if self.image_artist is not None:
            self.image_artist.set_transform(t + self.ax.transData)

        for art in self.shape_artists:
            # Only apply when artist lives in data coords (most geopandas artists do)
            try:
                art.set_transform(t + self.ax.transData)
            except Exception:
                pass

    def _autoscale_to_rotated_extent(self):
        """Compute bounds of rotated raster extent and set x/ylim so everything is visible."""
        if self.raster_bounds is None:
            self.ax.relim()
            self.ax.autoscale()
            return

        l, b, r, t = self.raster_bounds.left, self.raster_bounds.bottom, self.raster_bounds.right, self.raster_bounds.top
        corners = [(l, b), (l, t), (r, t), (r, b)]
        cx, cy = self.center
        rcorners = rotate_points(cx, cy, corners, self.rotation_deg)
        xs, ys = zip(*rcorners)
        pad_x = (max(xs) - min(xs)) * 0.05 + 1e-6
        pad_y = (max(ys) - min(ys)) * 0.05 + 1e-6
        self.ax.set_xlim(min(xs) - pad_x, max(xs) + pad_x)
        self.ax.set_ylim(min(ys) - pad_y, max(ys) + pad_y)
        self.ax.figure.canvas.draw_idle()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shapefile over Rotated Raster — Rasterio + GeoPandas (PySide6)")
        self.resize(1100, 800)

        self.canvas = MapCanvas(self)
        self._build_toolbar()

        central = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(central)
        lay.addWidget(self.toolbar)
        lay.addWidget(self.canvas)
        self.setCentralWidget(central)

    def _build_toolbar(self):
        self.toolbar = QtWidgets.QWidget()
        h = QtWidgets.QHBoxLayout(self.toolbar)
        h.setContentsMargins(6, 6, 6, 6)
        h.setSpacing(12)

        btn_raster = QtWidgets.QPushButton("Open Raster…")
        btn_raster.clicked.connect(self.open_raster)

        btn_shape = QtWidgets.QPushButton("Open Shapefile…")
        btn_shape.clicked.connect(self.open_shapefile)

        lbl = QtWidgets.QLabel("Rotation (deg):")
        self.spin = QtWidgets.QDoubleSpinBox()
        self.spin.setRange(-360.0, 360.0)
        self.spin.setDecimals(1)
        self.spin.setSingleStep(1.0)
        self.spin.setValue(0.0)
        self.spin.valueChanged.connect(self.on_angle_changed)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider.setRange(-3600, 3600)  # tenths of a degree
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.on_slider_changed)

        btn_reset = QtWidgets.QPushButton("Reset View")
        btn_reset.clicked.connect(self.reset_view)

        btn_clear = QtWidgets.QPushButton("Clear")
        btn_clear.clicked.connect(self.canvas.clear_all)

        h.addWidget(btn_raster)
        h.addWidget(btn_shape)
        h.addSpacing(12)
        h.addWidget(lbl)
        h.addWidget(self.spin, 0)
        h.addWidget(self.slider, 1)
        h.addSpacing(12)
        h.addWidget(btn_reset)
        h.addWidget(btn_clear)

    # Slots
    def open_raster(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Raster",
            "",
            "Raster files (*.tif *.tiff *.vrt *.jp2 *.jpg *.jpeg *.png *.bmp);;All files (*)"
        )
        if not path:
            return
        try:
            self.canvas.set_raster(path)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def open_shapefile(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Shapefile",
            "",
            "Shapefile (*.shp);;GeoPackage (*.gpkg);;All files (*)"
        )
        if not path:
            return
        try:
            self.canvas.set_shapefile(path)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def on_angle_changed(self, val):
        # Keep slider in sync (tenths of degree)
        sval = int(round(val * 10))
        if self.slider.value() != sval:
            self.slider.blockSignals(True)
            self.slider.setValue(sval)
            self.slider.blockSignals(False)
        self.canvas.set_rotation(val)

    def on_slider_changed(self, sval):
        # tenths of degree
        val = sval / 10.0
        if self.spin.value() != val:
            self.spin.blockSignals(True)
            self.spin.setValue(val)
            self.spin.blockSignals(False)
        self.canvas.set_rotation(val)

    def reset_view(self):
        self.spin.setValue(0.0)  # this will drive slider + rotation
        self.canvas._autoscale_to_rotated_extent()


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
