"""
Table display module with better separation of display and data handling logic
"""
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt


class TableUpdater:
    """Handles updating the table with data from the geodataframe"""
    
    def __init__(self, table_widget):
        self.table_widget = table_widget

    def update_table(self, gdf):
        """Update the table display based on current GeoDataFrame"""
        if gdf is not None:
            try:
                self.table_widget.setRowCount(len(gdf))
                self.table_widget.setColumnCount(len(gdf.columns))

                # Set headers
                headers = list(gdf.columns)
                self.table_widget.setHorizontalHeaderLabels(headers)

                # Get geometry column name if it exists
                geometry_col_name = None
                try:
                    geometry_col_name = gdf.geometry.name
                except AttributeError:
                    # If there's no geometry column or other error, set to None
                    geometry_col_name = None

                # Populate table with data
                for i in range(len(gdf)):
                    for j, col in enumerate(headers):
                        # Handle geometry column specially
                        if geometry_col_name and col == geometry_col_name:
                            item = QTableWidgetItem("GEOMETRY")
                            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                        else:
                            # Handle potential null values
                            cell_value = gdf.iloc[i][col]
                            item = QTableWidgetItem(str(cell_value) if cell_value is not None else "")

                        self.table_widget.setItem(i, j, item)

                # Resize columns to fit content
                header = self.table_widget.horizontalHeader()
                if header:
                    header.setSectionResizeMode(QHeaderView.ResizeToContents)
            except Exception as e:
                print(f"Error updating table: {e}")
                # Still try to clear the table as a fallback
                self.table_widget.setRowCount(0)
                self.table_widget.setColumnCount(0)


class TableDataHandler:
    """Handles data-related operations for the table"""
    
    def __init__(self, data_handler):
        self.data_handler = data_handler

    def update_cell_value(self, row: int, col: int, value):
        """Update a specific cell value in the data handler"""
        if self.data_handler:
            return self.data_handler.update_cell_value(row, col, value)
        return False


class TableDisplayWidget(QTableWidget):
    """
    Widget for displaying and editing the attribute table of a shapefile
    """
    def __init__(self, data_handler=None):
        super().__init__()
        self.data_handler = data_handler
        self.table_updater = TableUpdater(self)
        self.table_data_handler = TableDataHandler(data_handler)

    def set_data_handler(self, data_handler):
        """Set the data handler to use for table operations"""
        self.data_handler = data_handler
        self.table_data_handler = TableDataHandler(data_handler)

    def update_table(self):
        """Update the table display based on current GeoDataFrame"""
        try:
            if self.data_handler:
                gdf = self.data_handler.get_geodataframe()
                self.table_updater.update_table(gdf)
        except Exception as e:
            print(f"Error in TableDisplayWidget.update_table: {e}")
            # Clear the table as a fallback
            self.setRowCount(0)
            self.setColumnCount(0)

    def itemChanged(self, item):
        """Handle item changes in the table"""
        super().itemChanged(item)

        if self.data_handler:
            row = item.row()
            col = item.column()

            # Update the corresponding value in the data handler
            self.table_data_handler.update_cell_value(row, col, item.text())