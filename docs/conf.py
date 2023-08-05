import importlib.metadata

project = "raster-footprint"
copyright = "2023, Preston Hartzell"
author = "Preston Hartzell"
version = importlib.metadata.version("raster_footprint")

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_theme_options = {"github_url": "https://github.com/pjhartzell/raster-footprint"}

intersphinx_mapping = {
    "rasterio": ("https://rasterio.readthedocs.io/en/stable", None),
    "affine": ("https://affine.readthedocs.io/en/latest", None),
}
