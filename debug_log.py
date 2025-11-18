import logging
import os
from datetime import datetime

# Configure logging
log_filename = f"debug_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, mode='w'),
        logging.StreamHandler()  # Also print to console
    ]
)

logger = logging.getLogger(__name__)

def log_debug_info():
    """Log comprehensive debug information about the environment"""
    logger.info(f"=== DEBUG LOG START ===")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Files in current directory: {os.listdir('.')}")
    
    # Check for testing folder
    if os.path.exists('testing'):
        logger.info(f"Testing folder exists, contents: {os.listdir('testing')}")
    else:
        logger.info("Testing folder does NOT exist in current directory")
    
    # Check if running as executable
    import sys
    if getattr(sys, 'frozen', False):
        logger.info(f"Running as executable from: {sys.executable}")
        logger.info(f"Executable directory: {os.path.dirname(sys.executable)}")
    else:
        logger.info("Running as script")
        
    # Log sys.path
    logger.info(f"sys.path: {sys.path}")
    
    # Check for src directory
    if os.path.exists('src'):
        logger.info(f"src directory exists, contents: {os.listdir('src')}")
    else:
        logger.info("src directory does NOT exist")
    
    logger.info(f"=== END DEBUG LOG ===")
    
    return log_filename