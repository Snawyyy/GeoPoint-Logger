import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test if all modules import correctly"""
    try:
        print("Testing imports...")
        from data_handler import GeospatialDataHandler
        print("PASS: data_handler imported successfully")
        
        from map_display import MapDisplayWidget
        print("PASS: map_display imported successfully")
        
        from table_display import TableDisplayWidget
        print("PASS: table_display imported successfully")
        
        from workflow import WorkflowManager
        print("PASS: workflow imported successfully")
        
        return True
    except Exception as e:
        print(f"FAIL: Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_ui():
    """Test a simple UI without the complex map widget"""
    try:
        print("\nTesting simple UI creation...")
        from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
        from table_display import TableDisplayWidget
        from data_handler import GeospatialDataHandler
        
        app = QApplication(sys.argv)
        window = QMainWindow()
        window.setWindowTitle("Simple Test")
        window.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        label = QLabel("Simple UI test - if you see this, basic UI works")
        layout.addWidget(label)
        
        # Try to create table widget
        table_widget = TableDisplayWidget()
        layout.addWidget(table_widget)
        
        window.setCentralWidget(central_widget)
        window.show()
        print("PASS: Simple UI created successfully")
        
        # Don't run exec_ to avoid the GUI popping up
        return True
    except Exception as e:
        print(f"FAIL: UI creation error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting diagnostics...")
    
    if test_imports():
        print("\nAll imports successful!")
    else:
        print("\nImport failures detected!")
        sys.exit(1)
        
    if test_simple_ui():
        print("\nBasic UI functionality works!")
    else:
        print("\nUI creation failed!")
        sys.exit(1)
        
    print("\nDiagnostics completed successfully!")
    input("\nPress Enter to continue...")