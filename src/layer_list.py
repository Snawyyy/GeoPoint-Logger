"""
Layer list widget for the Geospatial Data Viewer
"""
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal


class LayerListWidget(QListWidget):
    """
    A QListWidget subclass for displaying layers with checkboxes to control visibility.
    """
    layer_visibility_changed = pyqtSignal(str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.itemChanged.connect(self._on_item_changed)

    def populate_layers(self, filenames):
        """
        Populate the list with layer names from a list of filenames.
        """
        print(f"Populating layers with: {filenames}")
        self.clear()
        for filename in filenames:
            item = QListWidgetItem(filename, self)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            self.addItem(item)

    def _on_item_changed(self, item):
        """
        Emit a signal when a layer's visibility changes.
        """
        filename = item.text()
        is_visible = item.checkState() == Qt.Checked
        self.layer_visibility_changed.emit(filename, is_visible)
