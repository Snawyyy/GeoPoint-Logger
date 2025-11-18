import os

def check_world_file(image_path):
    # Possible extensions for world files
    world_extensions = ['.jgw', '.jpgw', '.JGW', '.JPGW', '.pgw', '.tfw', '.wld']
    
    # Get the base path without extension
    base_path = os.path.splitext(image_path)[0]
    
    print(f"Looking for world file for: {image_path}")
    print(f"Base path: {base_path}")
    
    # List all files in the directory
    directory = os.path.dirname(image_path) or "."
    print(f"Directory contents: {os.listdir(directory)}")
    
    # Try to find the world file with case-insensitive matching
    world_file_path = None
    for ext in world_extensions:
        potential_path = base_path + ext
        potential_path_lower = base_path + ext.lower()
        potential_path_upper = base_path + ext.upper()
        
        if os.path.exists(potential_path):
            world_file_path = potential_path
            break
        elif os.path.exists(potential_path_lower):
            world_file_path = potential_path_lower
            break
        elif os.path.exists(potential_path_upper):
            world_file_path = potential_path_upper
            break
    
    if world_file_path:
        print(f"Found world file: {world_file_path}")
        with open(world_file_path, 'r') as f:
            content = f.read()
        print(f"World file content: {content}")
        
        # Try to parse the values
        lines = content.splitlines()
        if len(lines) >= 6:
            values = []
            for i, line in enumerate(lines[:6]):
                try:
                    val = float(line.strip())
                    values.append(val)
                except ValueError:
                    print(f"Could not parse line {i+1}: '{line}'")
                    return
            
            print(f"Parsed values: A={values[0]}, D={values[1]}, B={values[2]}, E={values[3]}, C={values[4]}, F={values[5]}")
    else:
        print("No world file found with standard extensions")
        # Check for any file that might be a world file
        for file in os.listdir(directory):
            if file.lower().endswith(('jgw', 'pgw', 'tfw', 'wld')) and base_path in file:
                print(f"Possible world file found: {file}")

# If you provide the exact path to your image, I can help debug:
# check_world_file('path/to/your/image.jpg')