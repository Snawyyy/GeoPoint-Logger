#!/usr/bin/env python
"""
Main entry point for GeoPoint Logger application.
This file exists to avoid relative import issues when using PyInstaller.
"""

import sys
import os

# Import and run debug logging first
from debug_log import log_debug_info, logger

# Log debug information
log_filename = log_debug_info()
logger.info(f"Debug log saved to: {log_filename}")

# Determine the executable's directory (not the script's location when in development)
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = os.path.dirname(sys.executable)
else:
    # Running as script in development
    application_path = os.path.dirname(os.path.abspath(__file__))

# Add the application root to the Python path
src_path = os.path.join(application_path, 'src')
sys.path.insert(0, application_path)
sys.path.insert(0, src_path)

logger.info(f"Application path: {application_path}")
logger.info(f"Source path: {src_path}")

# Now import and run the main application
from src.main import main

if __name__ == "__main__":
    logger.info("Starting main application...")
    main()