"""
Image settings feature for the Geospatial Data Viewer
"""
import sys
import os
from PyQt5.QtWidgets import QComboBox, QSlider, QFormLayout, QGroupBox, QLabel
from PyQt5.QtCore import pyqtSignal, QObject, Qt

# Add the src directory to the path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import *


class ImageSettingsFeature(QObject):
    """
    Handles the functionality for adjusting image settings.
    """
    # Define signals for when settings change
    interpolation_changed = pyqtSignal(str)
    brightness_changed = pyqtSignal(int)
    contrast_changed = pyqtSignal(int)
    saturation_changed = pyqtSignal(int)
    threshold_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        # Initialize UI components
        self.interpolation_selector = None
        self.brightness_slider = None
        self.contrast_slider = None
        self.saturation_slider = None
        self.threshold_slider = None

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        """Set up the UI components for image settings"""
        self.interpolation_selector = QComboBox()
        self.interpolation_selector.addItems(["Nearest", "Bilinear", "Bicubic"])

        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(50)

        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(0, 100)
        self.contrast_slider.setValue(50)

        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setRange(0, 100)
        self.saturation_slider.setValue(50)

        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(0, 255)
        self.threshold_slider.setValue(0)

    def _setup_connections(self):
        """Set up signal connections"""
        self.interpolation_selector.currentTextChanged.connect(self.interpolation_changed.emit)
        self.brightness_slider.valueChanged.connect(self.brightness_changed.emit)
        self.contrast_slider.valueChanged.connect(self.contrast_changed.emit)
        self.saturation_slider.valueChanged.connect(self.saturation_changed.emit)
        self.threshold_slider.valueChanged.connect(self.threshold_changed.emit)

    def get_control_group(self):
        """Get a group box containing all the image settings controls"""
        group = QGroupBox("Image Settings")
        layout = QFormLayout(group)

        layout.addRow("Interpolation:", self.interpolation_selector)
        layout.addRow("Brightness:", self.brightness_slider)
        layout.addRow("Contrast:", self.contrast_slider)
        layout.addRow("Saturation:", self.saturation_slider)
        layout.addRow("Threshold:", self.threshold_slider)

        return group
