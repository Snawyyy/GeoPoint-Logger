#!/usr/bin/env python
"""
Simple build script that adds required environment variable setup for GDAL/PROJ
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

    # Build the PyInstaller command
    build_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=GeoPointLogger",  # Name of the executable
        "--windowed",  # GUI application (no console)
        "--onedir",  # Create a single directory with all files
        "--add-data=src;src",  # Include the src directory
        # Add the other necessary files
        "--add-data=main_runner.py;.",  # Include the main runner
        "--add-data=debug_log.py;.",  # Include debug logging
        # Add hidden imports for geospatial libraries
        "--hidden-import=PyQt5",
        "--hidden-import=geopandas",
        "--hidden-import=shapely",
        "--hidden-import=matplotlib",
        "--hidden-import=cv2",
        "--hidden-import=rasterio",
        "--hidden-import=rasterio.sample",
        "--hidden-import=rasterio.vrt",
        "--hidden-import=rasterio._io",
        "--hidden-import=rasterio.windows",
        "--hidden-import=rasterio.coords",
        "--hidden-import=rasterio.enums",
        "--hidden-import=rasterio.transform",
        "--hidden-import=pyproj",
        "--collect-all=geopandas",
        "--collect-all=shapely",
        "--collect-all=matplotlib",
        "--collect-all=fiona",
        "--collect-all=rasterio",
        "main_runner.py"  # Main entry point that handles relative imports correctly
    ]

    print("Running build command:")
    print(" ".join(build_cmd))

    # Execute the build command
    try:
        result = subprocess.run(build_cmd, check=True)
        print("Build completed successfully!")
        
        # Create a batch file that sets the required environment variables
        dist_dir = project_dir / "dist" / "GeoPointLogger"
        if dist_dir.exists():
            # Create a batch file to set environment variables before running
            bat_content = '''@echo off
REM Set GDAL and PROJ environment variables for geospatial operations

REM First, try to find the gdal_data and proj_data directories that fiona includes
set "SCRIPT_DIR=%~dp0"

REM Look for gdal_data in the standard installed location within the executable
for /d %%i in ("%SCRIPT_DIR%\\fiona.libs*") do (
    if exist "%%i\\gdal-data" (
        set "GDAL_DATA=%%i\\gdal-data"
        goto :found_gdal
    )
)

REM Look in the main executable directory or common subdirectories
if exist "%SCRIPT_DIR%\\_internal\\fiona\\gdal_data" (
    set "GDAL_DATA=%SCRIPT_DIR%\\_internal\\fiona\\gdal_data"
) else if exist "%SCRIPT_DIR%\\gdal_data" (
    set "GDAL_DATA=%SCRIPT_DIR%\\gdal_data"
) else if exist "%SCRIPT_DIR%\\_internal\\gdal_data" (
    set "GDAL_DATA=%SCRIPT_DIR%\\_internal\\gdal_data"
)

:found_gdal
if defined GDAL_DATA (
    echo Using GDAL data from: %GDAL_DATA%
    set "GDAL_DATA=%GDAL_DATA%"
)

REM Look for PROJ data
if exist "%SCRIPT_DIR%\\_internal\\fiona\\proj_data" (
    set "PROJ_LIB=%SCRIPT_DIR%\\_internal\\fiona\\proj_data"
) else if exist "%SCRIPT_DIR%\\proj_data" (
    set "PROJ_LIB=%SCRIPT_DIR%\\proj_data"
) else if exist "%SCRIPT_DIR%\\_internal\\proj_data" (
    set "PROJ_LIB=%SCRIPT_DIR%\\_internal\\proj_data"
)

if defined PROJ_LIB (
    echo Using PROJ data from: %PROJ_LIB%
    set "PROJ_LIB=%PROJ_LIB%"
)

REM Suppress GDAL logging to avoid console output
set "CPL_LOG=OFF"
set "CPL_DEBUG=OFF"

echo Starting GeoPoint Logger with geospatial support...
echo.

REM Run the executable
"%SCRIPT_DIR%\\GeoPointLogger.exe" %*

REM If there was an error, pause to see the message (uncomment for debugging)
REM if errorlevel 1 pause
'''

            bat_path = dist_dir / "GeoPointLogger_Run.bat"
            with open(bat_path, 'w') as f:
                f.write(bat_content)
            print(f"Created run script with environment setup: {bat_path}")
            
            # Create a simple batch file that just runs the exe without setting environment
            # (in case the libraries find the data automatically)
            simple_bat_content = '''@echo off
REM Simple run script for GeoPoint Logger
echo Starting GeoPoint Logger...
"GeoPointLogger.exe" %*
'''
            simple_bat_path = dist_dir / "GeoPointLogger_Simple_Run.bat"
            with open(simple_bat_path, 'w') as f:
                f.write(simple_bat_content)
            print(f"Created simple run script: {simple_bat_path}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        return False
    except FileNotFoundError:
        print("PyInstaller not found. Please install it with: pip install pyinstaller")
        return False


def main():
    print("GeoPoint Logger Build Tool (Simple version with environment setup)")
    print("=" * 60)

    # Build the executable
    print("Building the executable...")
    success = build_application()
    if success:
        print("\nBuild completed successfully!")
        print("You can find the executable in the 'dist' folder.")
        print("\nUse 'GeoPointLogger_Run.bat' to run with proper environment variables,")
        print("or 'GeoPointLogger_Simple_Run.bat' for a direct run.")
        print("\nThe executable should now properly render geospatial images.")
    else:
        print("\nBuild failed. Please check the error messages above.")
        print("You can run the application directly with: python src/main.py")


if __name__ == "__main__":
    main()