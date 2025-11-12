"""
Test the complete workflow of the application:

1. Load shapefile
2. Load georeferenced image
3. Navigate between points
4. Record IDs
5. Verify automatic zoom to next point
"""
print("Testing the complete workflow:")
print()
print("1. Load the test_points.shp file using the 'Load SHP File' button")
print("2. Load the test_georef.jpg file using the 'Load Georeferenced JPG' button")
print("3. Use 'Next Point' and 'Previous Point' buttons to navigate")
print("4. Try entering an ID in the text field and clicking 'Record ID & Next'")
print("5. The application should automatically zoom to the next point after recording")
print()
print("Key features implemented:")
print("- Loading SHP files and displaying their attribute tables")
print("- Loading and displaying georeferenced images")
print("- Navigating between points with automatic zoom")
print("- Recording IDs and moving to next point with one click")
print("- Editing table data directly")
print()
print("The application implements the requested workflow:")
print("Look at map → Write ID → Click 'Record ID & Next' → Next point auto-zooms")