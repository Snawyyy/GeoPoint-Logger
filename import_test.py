import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from data_handler import GeospatialDataHandler
    from map_display import MapDisplayWidget
    from table_display import TableDisplayWidget
    from workflow import WorkflowManager
    print("All imports successful")
except Exception as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()