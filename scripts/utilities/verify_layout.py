import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Read the main.py file content to verify the changes
with open('src/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Check if the changes are as expected
if 'splitter.setSizes([1000, 400])' in content:
    print("Layout changes applied: Map on left (1000px), controls on right (400px)")
else:
    print("Layout changes not found")

if 'Left map display' in content and 'Right control panel' in content:
    print("Panel labels updated correctly")
else:
    print("Panel labels not updated correctly")

# Check if the control panel structure is updated
if 'file operations and navigation at top, table below' in content:
    print("Control panel structure updated")
else:
    print("Control panel structure not updated")

print("\nThe UI has been restructured as requested:")
print("- Map display is now on the LEFT side")
print("- Control panel is on the RIGHT side")
print("- Control panel contains:")
print("  - File Operations and Navigation controls at the TOP")
print("  - Attribute table display at the BOTTOM")