from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="geospatial-viewer",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for viewing and editing geospatial shapefiles with georeferenced images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/geospatial-viewer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt5>=5.15.0",
        "geopandas>=0.10.0",
        "shapely>=1.8.0",
        "fiona>=1.8.0",
        "matplotlib>=3.5.0",
        "opencv-python>=4.5.0",
        "numpy>=1.20.0",
        "pandas>=1.3.0",
    ],
    entry_points={
        "console_scripts": [
            "geospatial-viewer=src.main:main",
        ],
    },
)