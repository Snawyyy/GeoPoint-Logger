#!/usr/bin/env python
"""
Build script for GeoPoint Logger application with proper GDAL/PROJ environment setup
Creates a standalone executable using PyInstaller with proper geospatial data inclusion
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil


def find_and_copy_gdal_proj_data():
    """Find and copy GDAL/PROJ data to a local directory for inclusion"""
    print("Looking for GDAL and PROJ data...")
    
    # Create local directory for geospatial data
    geospatial_dir = Path("geodata")
    if geospatial_dir.exists():
        import shutil
        shutil.rmtree(geospatial_dir)
    geospatial_dir.mkdir(exist_ok=True)
    
    # Try to find GDAL data
    gdal_found = False
    try:
        import osgeo
        gdal_data_dir = os.path.join(osgeo.__path__[0], 'data')
        if os.path.exists(gdal_data_dir):
            print(f"Found GDAL data at: {gdal_data_dir}")
            shutil.copytree(gdal_data_dir, geospatial_dir / "gdal_data", dirs_exist_ok=True)
            gdal_found = True
    except:
        pass

    if not gdal_found:
        # Try using gdal-config if available
        try:
            import subprocess
            result = subprocess.run(['gdal-config', '--datadir'], capture_output=True, text=True)
            if result.returncode == 0:
                gdal_data_dir = result.stdout.strip()
                if os.path.exists(gdal_data_dir):
                    print(f"Found GDAL data at: {gdal_data_dir}")
                    shutil.copytree(gdal_data_dir, geospatial_dir / "gdal_data", dirs_exist_ok=True)
                    gdal_found = True
        except:
            pass

    # Try common locations for GDAL data
    if not gdal_found:
        possible_paths = [
            os.path.join(sys.prefix, 'Library', 'share', 'gdal'),
            os.path.join(os.path.dirname(sys.executable), 'Library', 'share', 'gdal'),
            os.path.join(sys.prefix, 'share', 'gdal'),
            os.path.join(os.path.dirname(sys.executable), 'share', 'gdal'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"Found GDAL data at: {path}")
                shutil.copytree(path, geospatial_dir / "gdal_data", dirs_exist_ok=True)
                gdal_found = True
                break

    # Try to find PROJ data
    proj_found = False
    try:
        import pyproj
        # Get PROJ data directory
        proj_data_dir = pyproj.datadir.get_data_dir()
        if proj_data_dir and os.path.exists(proj_data_dir):
            print(f"Found PROJ data at: {proj_data_dir}")
            shutil.copytree(proj_data_dir, geospatial_dir / "proj_data", dirs_exist_ok=True)
            proj_found = True
    except:
        pass

    if not proj_found:
        print("Warning: Could not find PROJ data directory automatically")
        # Look for it in common places
        common_proj_paths = [
            os.path.join(sys.prefix, 'share', 'proj'),
            os.path.join(sys.prefix, 'Library', 'share', 'proj'),
            os.path.join(os.path.dirname(sys.executable), 'Library', 'share', 'proj'),
            os.path.join(os.path.dirname(sys.executable), 'share', 'proj'),
            # Based on the error output, try this specific path
            os.path.join(os.path.dirname(sys.executable), 'Library', 'share', 'proj'),
            # Check if it's in the pyproj installation
            os.path.join(os.path.dirname(__import__('pyproj').__file__), 'proj_dir', 'share', 'proj'),
        ]

        for path in common_proj_paths:
            if os.path.exists(path):
                print(f"Found PROJ data at: {path}")
                shutil.copytree(path, geospatial_dir / "proj_data", dirs_exist_ok=True)
                proj_found = True
                break

    if not gdal_found:
        print("Warning: Could not find GDAL data. The executable may not work properly with geospatial operations.")
    if not proj_found:
        print("Warning: Could not find PROJ data. The executable may not work properly with geospatial operations.")
    
    return gdal_found or proj_found


def build_application():
    print("Building GeoPoint Logger application with geospatial data...")
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Find and copy geospatial data
    has_geodata = find_and_copy_gdal_proj_data()
    
    # Build the PyInstaller command
    build_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=GeoPointLogger",  # Name of the executable
        "--windowed",  # GUI application (no console)
        "--onedir",  # Create a single directory with all files
        "--add-data=src;src",  # Include the src directory
    ]
    
    # Add geospatial data if found
    if has_geodata:
        build_cmd.extend(["--add-data=geodata;."])
    
    # Add hidden imports for geospatial libraries
    hidden_imports = [
        "PyQt5", "geopandas", "shapely", "matplotlib", "cv2", "rasterio", 
        "rasterio.sample", "rasterio.vrt", "rasterio._io", "rasterio.windows", 
        "rasterio.coords", "rasterio.enums", "rasterio.transform", "pyproj"
    ]
    
    for imp in hidden_imports:
        build_cmd.extend([f"--hidden-import={imp}"])
    
    build_cmd.extend([
        "--collect-all=geopandas",
        "--collect-all=shapely", 
        "--collect-all=matplotlib",
        "src/main.py"  # Main entry point
    ])
    
    print("Running build command:")
    print(" ".join(build_cmd))
    
    # Execute the build command
    try:
        result = subprocess.run(build_cmd, check=True)
        print("Build completed successfully!")
        
        # Clean up temporary geodata directory
        geospatial_dir = Path("geodata")
        if geospatial_dir.exists():
            import shutil
            shutil.rmtree(geospatial_dir)
            print("Cleaned up temporary geodata directory")
        
        # Create a batch file that sets the required environment variables
        dist_dir = project_dir / "dist" / "GeoPointLogger"
        if dist_dir.exists():
            # Create a batch file to set environment variables before running
            bat_content = '''@echo off
REM Set GDAL and PROJ environment variables for geospatial operations
if exist "gdal_data" (
    set GDAL_DATA=%~dp0gdal_data
    echo Using GDAL data from: %GDAL_DATA%
)

if exist "proj_data" (
    set PROJ_LIB=%~dp0proj_data
    echo Using PROJ data from: %PROJ_LIB%
)

REM Suppress GDAL logging to avoid console output
set CPL_LOG_ERRORS=OFF
set CPL_LOG=OFF

REM Run the executable
"GeoPointLogger.exe" %*

REM Pause if there was an error to see any messages (uncomment for debugging)
REM if errorlevel 1 pause
'''
            
            bat_path = dist_dir / "GeoPointLogger_Run.bat"
            with open(bat_path, 'w') as f:
                f.write(bat_content)
            print(f"Created run script with environment setup: {bat_path}")
            
            # Also create an executable that automatically sets up the environment
            # by creating a small wrapper script
            wrapper_content = '''#!/usr/bin/env python
import os
import sys
import subprocess
from pathlib import Path

# Set up environment variables
script_dir = Path(__file__).parent.absolute()

# Set GDAL data directory
gdal_data_dir = script_dir / "gdal_data"
if gdal_data_dir.exists():
    os.environ["GDAL_DATA"] = str(gdal_data_dir)

# Set PROJ data directory  
proj_data_dir = script_dir / "proj_data"
if proj_data_dir.exists():
    os.environ["PROJ_LIB"] = str(proj_data_dir)

# Suppress GDAL logging
os.environ["CPL_LOG"] = "OFF"
os.environ["CPL_LOG_ERRORS"] = "OFF"

# Run the main executable
exe_path = script_dir / "GeoPointLogger.exe"
try:
    result = subprocess.run([str(exe_path)] + sys.argv[1:])
    sys.exit(result.returncode)
except Exception as e:
    print(f"Error running executable: {e}")
    input("Press Enter to continue...")
    sys.exit(1)
'''

            wrapper_path = dist_dir / "GeoPointLogger_EnvWrapper.py"
            with open(wrapper_path, 'w') as f:
                f.write(wrapper_content)
            print(f"Created environment wrapper: {wrapper_path}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        # Clean up temporary directory even if build fails
        geospatial_dir = Path("geodata")
        if geospatial_dir.exists():
            import shutil
            shutil.rmtree(geospatial_dir)
        return False
    except FileNotFoundError:
        print("PyInstaller not found. Please install it with: pip install pyinstaller")
        # Clean up temporary directory
        geospatial_dir = Path("geodata")
        if geospatial_dir.exists():
            import shutil
            shutil.rmtree(geospatial_dir)
        return False


def main():
    print("GeoPoint Logger Build Tool (Final version with proper GDAL/PROJ support)")
    print("=" * 70)

    # Build the executable
    print("Building the executable...")
    success = build_application()
    
    if success:
        print("\n" + "="*70)
        print("BUILD COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("You can find the executable in: dist/GeoPointLogger/")
        print("\nTo run the application:")
        print("1. Use 'GeoPointLogger_Run.bat' in the dist/GeoPointLogger folder")
        print("2. This batch file will set up required environment variables")
        print("\nThe executable now includes GDAL/PROJ data needed for geospatial operations.")
        print("Images should now render properly in the executable.")
    else:
        print("\nBuild failed. Please check the error messages above.")
        print("You can run the application directly with: python src/main.py")


if __name__ == "__main__":
    main()