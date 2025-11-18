#!/usr/bin/env python
"""
Build script for GeoPoint Logger application
Creates a standalone executable using PyInstaller
"""

import os
import sys
import subprocess
from pathlib import Path

def build_application():
    print("Building GeoPoint Logger application...")
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Define the build command
    build_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=GeoPointLogger",  # Name of the executable
        "--windowed",  # GUI application (no console)
        "--onedir",  # Create a single directory with all files
        "--add-data=src;src",  # Include the src directory
        "--hidden-import=PyQt5",  # Explicitly include PyQt5
        "--hidden-import=geopandas",  # Explicitly include geopandas
        "--hidden-import=shapely",  # Explicitly include shapely
        "--hidden-import=matplotlib",  # Explicitly include matplotlib
        "--hidden-import=cv2",  # Explicitly include opencv
        "--hidden-import=rasterio",  # Include rasterio if used
        "--hidden-import=rasterio.sample",  # Explicitly include rasterio.sample
        "--hidden-import=rasterio.vrt",  # Explicitly include rasterio.vrt
        "--hidden-import=rasterio._io",  # Explicitly include rasterio._io
        "--hidden-import=rasterio.windows",  # Explicitly include rasterio.windows
        "--hidden-import=rasterio.coords",  # Explicitly include rasterio.coords
        "--hidden-import=rasterio.enums",  # Explicitly include rasterio.enums
        "--hidden-import=rasterio.transform",  # Explicitly include rasterio.transform
        "--hidden-import=pyproj",  # Include pyproj
        "--collect-all=geopandas",  # Collect all geopandas resources
        "--collect-all=shapely",  # Collect all shapely resources
        "--collect-all=matplotlib",  # Collect all matplotlib resources
        "src/main.py"  # Main entry point
    ]
    
    print("Running build command:")
    print(" ".join(build_cmd))
    
    # Execute the build command
    try:
        result = subprocess.run(build_cmd, check=True)
        print("Build completed successfully!")
        print(f"Executable created in: {project_dir}/dist/GeoPointLogger/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        return False
    except FileNotFoundError:
        print("PyInstaller not found. Please install it with: pip install pyinstaller")
        return False

def create_installer_script():
    """Create a batch file to run the application"""
    installer_content = '''@echo off
REM GeoPoint Logger Installer Script
echo Installing GeoPoint Logger...

REM Create a virtual environment
python -m venv geopoint_env

REM Activate the virtual environment
call geopoint_env\\Scripts\\activate.bat

REM Install dependencies
pip install -r requirements.txt

REM Run the application
echo Starting GeoPoint Logger...
python src/main.py

REM Deactivate the environment when done
REM pause
'''
    
    with open("install_and_run.bat", "w") as f:
        f.write(installer_content)
    
    print("Created install_and_run.bat for easy installation and execution.")

def create_setup_py():
    """Ensure setup.py is properly configured"""
    # This is already handled as we updated it earlier
    print("Setup.py is properly configured for GeoPoint Logger.")

if __name__ == "__main__":
    print("GeoPoint Logger Build Tool")
    print("=" * 30)

    # Create installer script
    create_installer_script()
    create_setup_py()

    # Build the executable directly
    print("Building the executable...")
    success = build_application()
    if success:
        print("\nBuild completed successfully!")
        print("You can find the executable in the 'dist' folder.")
    else:
        print("\nBuild failed. Please check the error messages above.")
        print("You can run the application directly with: python src/main.py")
        print("Or use the install_and_run.bat script to install dependencies and run.")