#!/usr/bin/env python
"""
Build script for GeoPoint Logger application with proper GDAL data inclusion
Creates a standalone executable using PyInstaller
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil


def find_gdal_data():
    """Find GDAL data directory to include in the executable"""
    try:
        import osgeo
        # Try to locate GDAL data
        gdal_data_dir = os.path.join(osgeo.__path__[0], 'data')
        if os.path.exists(gdal_data_dir):
            print(f"Found GDAL data at: {gdal_data_dir}")
            return gdal_data_dir
    except:
        pass

    try:
        # Try using gdal-config if available
        import subprocess
        result = subprocess.run(['gdal-config', '--datadir'], capture_output=True, text=True)
        if result.returncode == 0:
            gdal_data_dir = result.stdout.strip()
            if os.path.exists(gdal_data_dir):
                print(f"Found GDAL data at: {gdal_data_dir}")
                return gdal_data_dir
    except:
        pass

    # Try common locations
    possible_paths = [
        os.path.join(sys.prefix, 'share', 'gdal'),
        os.path.join(sys.prefix, 'Library', 'share', 'gdal'),
        os.path.join(os.path.dirname(sys.executable), 'share', 'gdal'),
        os.path.join(os.path.dirname(sys.executable), 'Library', 'share', 'gdal'),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found GDAL data at: {path}")
            return path

    print("Warning: Could not find GDAL data directory")
    return None


def find_proj_data():
    """Find PROJ data directory to include in the executable"""
    try:
        import pyproj
        # Get PROJ data directory
        proj_data_dir = pyproj.datadir.get_data_dir()
        if proj_data_dir and os.path.exists(proj_data_dir):
            print(f"Found PROJ data at: {proj_data_dir}")
            return proj_data_dir
    except:
        pass

    # Try to find it manually
    import pyproj
    try:
        # Alternative method for newer pyproj versions
        import pyproj.database
        db_path = pyproj.database.get_proj_database_connection()
        # The proj directory is typically one level up from the database file
        proj_dir = os.path.dirname(os.path.dirname(db_path))
        if os.path.exists(proj_dir):
            print(f"Found PROJ data at: {proj_dir}")
            return proj_dir
    except:
        pass

    print("Warning: Could not find PROJ data directory")
    return None


def build_application():
    print("Building GeoPoint Logger application with GDAL/PROJ data...")

    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)

    # Find GDAL and PROJ data directories
    gdal_data_dir = find_gdal_data()
    proj_data_dir = find_proj_data()

    # Build the PyInstaller command
    build_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=GeoPointLogger",  # Name of the executable
        "--windowed",  # GUI application (no console)
        "--onedir",  # Create a single directory with all files
        "--add-data=src;src",  # Include the src directory
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
        # Add data directories if found
    ]

    # Add GDAL data if found
    if gdal_data_dir:
        build_cmd.extend([f"--add-data={gdal_data_dir};gdal_data"])
    
    # Add PROJ data if found
    if proj_data_dir:
        build_cmd.extend([f"--add-data={proj_data_dir};proj_data"])

    build_cmd.append("src/main.py")  # Main entry point

    print("Running build command:")
    print(" ".join(build_cmd))

    # Execute the build command
    try:
        result = subprocess.run(build_cmd, check=True)
        print("Build completed successfully!")
        
        # Post-build configuration: Create a hook to set environment variables
        dist_dir = project_dir / "dist" / "GeoPointLogger"
        if dist_dir.exists():
            # Create a batch file to set environment variables before running the executable
            bat_content = f'''@echo off
set GDAL_DATA="{dist_dir}\\gdal_data"
set PROJ_LIB="{dist_dir}\\proj_data"
set CPL_LOG=OFF
"GeoPointLogger.exe" %*
'''
            bat_path = dist_dir.parent / "GeoPointLogger_with_env.bat"
            with open(bat_path, 'w') as f:
                f.write(bat_content)
            print(f"Created environment setup batch file: {bat_path}")

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


def main():
    print("GeoPoint Logger Build Tool (Fixed version)")
    print("=" * 45)

    # Create installer script
    create_installer_script()

    # Build the executable directly
    print("Building the executable...")
    success = build_application()
    if success:
        print("\nBuild completed successfully!")
        print("You can find the executable in the 'dist' folder.")
        print("The GDAL and PROJ data should now be properly included.")
    else:
        print("\nBuild failed. Please check the error messages above.")
        print("You can run the application directly with: python src/main.py")
        print("Or use the install_and_run.bat script to install dependencies and run.")


if __name__ == "__main__":
    main()