import os

# ==========================
# TWITTER API CONFIGURATION
# ==========================
# Replace with your actual API token from developer.twitter.com
TWITTER_API_TOKEN = os.getenv("TWITTER_API_TOKEN", "YOUR_API_TOKEN_HERE")
API_BASE_URL = "https://api.twitterapi.io/twitter/tweet/advanced_search"

# ==========================
# FILE PATHS (Relative for Portability)
# ==========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data Collection Output
CSV_OUTPUT_FILENAME = os.path.join(BASE_DIR, "data", "output", "tweets", "tweets_data.csv")

# Visualization Input & Output
INPUT_DATA_CSV = CSV_OUTPUT_FILENAME  # Uses collector output by default

# Path to Shapefile for city boundary overlay
# Place shapefile in: data/shapefiles/Your_City.shp
SHAPEFILE_PATH = os.path.join(BASE_DIR, "data", "input", "shapefiles", "City_Boundary.shp")

# Output directory for generated maps
VISUALIZATION_OUTPUT_DIR = os.path.join(BASE_DIR, "data", "output", "maps")

# ==========================
# COLLECTION PARAMETERS
# ==========================
COLLECTION_CONFIG = {
    "batch_size": 200,              # Write to CSV every N tweets
    "sleep_seconds": 0.25,          # Delay between API calls (rate limiting)
    "timeout": 30,                  # API request timeout (seconds)
    "verbose_every": 250,           # Print progress every N queries
    "max_locations": None,          # Limit locations (None = all)
    "max_keywords": None,           # Limit keywords (None = all)
    "max_queries": None,            # Limit total queries (None = all)
}

# ==========================
# VISUALIZATION PARAMETERS
# ==========================
VISUALIZATION_CONFIG = {
    "figure_dpi": 300,              # Output resolution
    "figure_size": (18, 14),        # Figure dimensions (width, height)
    "style": "seaborn-v0_8-whitegrid",  # Matplotlib style
    
    # Color maps for different visualizations
    "colormaps": {
        "kde": "YlOrRd",            # KDE heatmap
        "engagement": "viridis",    # Engagement intensity
        "hexbin": "RdYlGn_r",       # Hexagonal binning
        "raster": "hot",            # Raster grid
    },
    
    # Boundary styling
    "boundary_color": "black",
    "boundary_width": 2.5,
    "boundary_glow_width": 2.0,
    "boundary_glow_alpha": 0.3,
    
    # Grid parameters
    "kde_grid_points": 100,         # KDE interpolation resolution
    "hexbin_gridsize": 30,          # Hexagon size
    "raster_bins": 25,              # Number of raster cells per dimension
    "idw_power": 2,                 # IDW interpolation power
    "idw_smoothing": 0.0001,        # IDW smoothing parameter
    
    # Extent settings
    "extent_padding": 0.005,        # Margin around map (degrees)
}

# ==========================
# LOGGING & OUTPUT
# ==========================
LOG_LEVEL = "INFO"                  # DEBUG, INFO, WARNING, ERROR
SAVE_INTERMEDIATE = False           # Save intermediate processing files
