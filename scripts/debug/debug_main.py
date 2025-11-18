import sys
import os
import traceback

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from PyQt5.QtWidgets import QApplication
    from src.main import GeospatialViewer
    
    print("Starting application...")
    
    app = QApplication(sys.argv)
    viewer = GeospatialViewer()
    viewer.show()
    print("UI displayed. Starting event loop...")
    
    # Execute the application and keep it running
    exit_code = app.exec_()
    print(f"Application exited with code: {exit_code}")
    
except ImportError as e:
    print(f"Import error: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"Error running application: {e}")
    traceback.print_exc()
    
# Keep the console open so we can see any errors
input("\nPress Enter to exit...")