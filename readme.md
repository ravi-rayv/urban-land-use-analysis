# Urban Land-Use Classification Using Social Media Data

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status: Active](https://img.shields.io/badge/Status-Active-brightgreen)]()

## Project Overview

This project classifies urban land-use types using **social media data** (Twitter/X) combined with **machine learning** and **geospatial analysis**. The workflow includes:

1. **Data Collection** - Scrape location-tagged tweets via Twitter API
2. **Geospatial Processing** - Extract coordinates and aggregate by geography
3. **Visualization** - Generate 12 types of geographic maps showing engagement patterns
4. **Analysis** - Identify land-use characteristics from social signals

### Key Features
- ✅ Streaming data pipeline (memory-efficient batch processing)
- ✅ Multi-authentication fallback (Bearer, X-API-Key, Direct Token)
- ✅ 12 geospatial visualization types (KDE, Voronoi, IDW, hexbin, etc.)
- ✅ City boundary overlay with customizable styling
- ✅ Modular, configurable architecture
- ✅ Production-ready error handling

---

## Installation

### Prerequisites
- Python 3.8+
- Twitter API Token ([Get one here](https://developer.twitter.com/))
- City boundary shapefile (optional, but recommended)

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/urban-land-use-analysis.git
cd urban-land-use-analysis
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Configuration

### 1. Edit `config.py`
Set your API token and file paths:
```python
TWITTER_API_TOKEN = "your_api_token_here"
SHAPEFILE_PATH = "data/shapefiles/City_Boundary.shp"
CSV_OUTPUT_FILENAME = "data/output/tweets_data.csv"
```

### 2. Edit `constants.py`
Define search locations and keywords:
```python
LOCATIONS = [
    {"geo": "19.0760,72.8777,0.5km", "name": "Mumbai_Central"},
    {"geo": "28.6139,77.2090,0.5km", "name": "Delhi_Central"},
]

KEYWORDS = ["House", "Shop", "School", "Hospital", "Park", ...]
```

---

## Usage

### Step 1: Collect Tweet Data
```bash
python src/tweet_collector.py
```
**Output:** `data/output/tweets_data.csv`

Sample columns:
```
Query | Date | Tweet by | Text Content | Like Count | Reply Count | Tweet URL | Error
```

### Step 2: Generate Geographic Visualizations
```bash
python src/geo_visualizer.py
```
**Output:** 12 PNG maps in `data/output/maps/`

**Map Types Generated:**
1. **KDE Heatmap** - Smooth kernel density estimation
2. **Engagement Contours** - Isoline maps of tweet engagement
3. **Hexagonal Grid** - Aggregated engagement by hex cells
4. **Raster Grid** - Regular rectangular cell aggregation
5. **Voronoi Diagram** - Territory-based analysis
6. **Point Transparency** - Individual tweet visibility
7. **IDW Interpolation** - Inverse distance weighting surface
8. **Hot Spot Clustering** - Geographic clusters
9. **Temporal Heatmap** - Time-based engagement patterns
10. **Sentiment Map** - Emotional content distribution
11. **Keyword Frequency** - Spatial distribution of keywords
12. **Composite Overview** - Multi-layer analysis

---


## Directory Structure

```
urban-land-use-analysis/
├── README.md                 # This file
├── requirements.txt          # Python packages
├── config.py                 # User settings (API token, paths)
├── constants.py              # Search locations & keywords
│
├── src/
│   ├── __init__.py
│   ├── tweet_collector.py    # Data collection script
│   ├── geo_visualizer.py     # Visualization script
│   └── utils.py              # Shared utilities
│
├── data/
│   ├── input/
│   │   └── shapefiles/       # Place your .shp files here
│   ├── output/
│   │   ├── tweets/           # Generated CSV files
│   │   └── maps/             # Generated PNG maps
│   └── raw/                  # Raw data before processing
│
├── notebooks/                # Jupyter analysis (optional)
│   └── analysis.ipynb
│
├── tests/                    # Unit tests (optional)
│   └── test_collector.py
│
├── .gitignore               # Git ignore file
└── LICENSE                  # MIT License
```

---

## Shapefile Setup

### Finding Shapefiles
- [Natural Earth Data](https://www.naturalearthdata.com/)
- [OpenStreetMap/Geofabrik](http://download.geofabrik.de/)
- [Local government mapping agencies](https://www.openstreetmap.org/)

### Required Files
Place all files with the same name in `data/shapefiles/`:
```
data/shapefiles/
├── City_Boundary.shp       # Main geometry file
├── City_Boundary.shx       # Index file
├── City_Boundary.dbf       # Attribute file
└── City_Boundary.prj       # Projection file (optional but recommended)
```

### If No Shapefile Available
The visualizer will use the extent of your tweet data instead:
```python
# config.py
SHAPEFILE_PATH = None  # Will skip boundary overlay
```

---

## Output Examples

### KDE Heatmap
Shows density concentration areas - useful for identifying major activity zones.

### Voronoi Diagram
Divides space into territories - good for regional analysis.

### Engagement Contours
Isolines show engagement intensity gradients across the city.

### Hexagonal Grid
Regular hexagons for consistent spatial aggregation (recommended for statistics).

---

## Troubleshooting

### Issue: "Module not found" error
```bash
pip install -r requirements.txt
```

### Issue: "Invalid API token"
- Verify token in `config.py`
- Check token hasn't expired
- Ensure Bearer prefix is included

### Issue: "No shapefiles found"
- Verify path in `config.py`
- Check all required files present (.shp, .shx, .dbf)
- Visualizer will use data extent as fallback

### Issue: "Memory error" during visualization
- Reduce `gridsize` in hexbin visualization
- Reduce `gridsize` in KDE interpolation (from 100j to 50j)
- Process data in smaller batches

### Issue: "No tweets collected"
- Check keyword list is non-empty
- Verify API token is valid
- Check location coordinates are formatted: `lat,lon,radius`
- Wait 30 minutes and retry (API rate limits)

---


## Contributing

We welcome contributions! Here's how to help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Areas for Contribution
- Additional visualization types
- Sentiment analysis integration
- Real-time streaming improvements
- BERTopic integration for topic modeling
- Unit test coverage
- Documentation improvements

---

## Bug Reports

Found a bug? [Open an issue](../../issues) with:
- Python version & OS
- Error message & traceback
- Steps to reproduce
- Your `config.py` (with token removed)

---

## Contact & Support

**Author:** Ravi Satyappa Dabbanavar, Dr. Arindam Biswas 
**Institution:** Indian Institute of Technology Roorkee (IITR)  
**Email:** rs_dabbanavar@ar.iitr.ac.in  
**Research Area:** Geospatial Analysis, Social Media Mining, Urban Computing, Big data


