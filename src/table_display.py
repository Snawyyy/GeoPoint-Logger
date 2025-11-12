"""
Table display module for showing and editing geospatial data tables
"""
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt


class TableDisplayWidget(QTableWidget):
    """
    Widget for displaying and editing the attribute table of a shapefile
    """
    def __init__(self, data_handler=None):
        super().__init__()
        self.data_handler = data_handler
        
    def set_data_handler(self, data_handler):
        """Set the data handler to use for table operations"""
        self.data_handler = data_handler
        
    def update_table(self):
        """Update the table display based on current GeoDataFrame"""
        if self.data_handler and self.data_handler.get_geodataframe() is not None:
            gdf = self.data_handler.get_geodataframe()
            
            self.setRowCount(len(gdf))
            self.setColumnCount(len(gdf.columns))
            
            # Set headers
            headers = list(gdf.columns)
            self.setHorizontalHeaderLabels(headers)
            
            # Populate table with data
            for i in range(len(gdf)):
                for j, col in enumerate(headers):
                    # Handle geometry column specially
                    if col == gdf.geometry.name:
                        item = QTableWidgetItem("GEOMETRY")
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    else:
                        item = QTableWidgetItem(str(gdf.iloc[i][col]))
                    
                    self.setItem(i, j, item)
            
            # Resize columns to fit content
            self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    
    def itemChanged(self, item):
        """Handle item changes in the table"""
        super().itemChanged(item)
        
        if self.data_handler:
            row = item.row()
            col = item.column()
            
            # Update the corresponding value in the data handler
            self.data_handler.update_cell_value(row, col, item.text())