"""
Test script to create a sample shapefile for testing the application
"""
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd

# Create sample data
data = {
    'id': [1, 2, 3, 4, 5],
    'name': ['Point A', 'Point B', 'Point C', 'Point D', 'Point E'],
    'value': [10, 20, 30, 40, 50]
}

# Create points (for testing purposes, using simple coordinates)
geometry = [
    Point(1, 1),
    Point(2, 2), 
    Point(3, 3),
    Point(4, 4),
    Point(5, 5)
]

# Create GeoDataFrame
gdf = gpd.GeoDataFrame(data, geometry=geometry)

# Save as shapefile
gdf.to_file('test_points.shp')

print("Sample shapefile 'test_points.shp' created successfully!")
print("Features:")
print(gdf)