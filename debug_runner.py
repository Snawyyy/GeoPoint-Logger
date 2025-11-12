import sys
import traceback

# Redirect stderr to a file
stderr_file = open('stderr.log', 'w')
sys.stderr = stderr_file

try:
    sys.path.insert(0, 'src')
    from main import main
    main()
except Exception as e:
    print(f"An error occurred: {e}")
    traceback.print_exc()
finally:
    # Close the file and restore stderr
    stderr_file.close()
    sys.stderr = sys.__stderr__
