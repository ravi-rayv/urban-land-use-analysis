

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import warnings
import os
import re
from scipy.stats import gaussian_kde
from scipy.spatial import Voronoi
from matplotlib.patches import Polygon
from scipy.interpolate import griddata

import config

warnings.filterwarnings('ignore')

# =============================================================================
# SETUP & CONFIGURATION
# =============================================================================

print("\n" + "="*80)
print("GEOGRAPHIC VISUALIZATION - SETUP")
print("="*80 + "\n")

# Set plotting style
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.size'] = 11
plt.rcParams['figure.figsize'] = (16, 12)
plt.style.use('seaborn-v0_8-whitegrid')

# =============================================================================
# LOAD DATA
# =============================================================================

print("[1/7] Loading data...\n")

gdf = None
shapefile_bounds = None

# Load shapefile if available
try:
    if os.path.exists(config.SHAPEFILE_PATH):
        gdf = gpd.read_file(config.SHAPEFILE_PATH)
        shapefile_bounds = gdf.total_bounds
        print(f"[✓] Shapefile loaded: {config.SHAPEFILE_PATH}")
        print(f"[✓] CRS: {gdf.crs}")
        print(f"[✓] Features: {len(gdf)}")
    else:
        print(f"[!] Shapefile not found at {config.SHAPEFILE_PATH}")
        print("[!] Maps will use data extent only")
except Exception as e:
    print(f"[!] Error loading shapefile: {e}")

# Load tweet data
try:
    df = pd.read_csv(config.INPUT_DATA_CSV)
    print(f"\n[✓] Data loaded: {len(df)} records")
    print(f"[✓] Columns: {list(df.columns)}\n")
except Exception as e:
    print(f"[ERROR] Could not load CSV: {e}")
    exit(1)

# =============================================================================
# EXTRACT COORDINATES
# =============================================================================

print("[2/7] Extracting coordinates...\n")


def extract_coordinates(query_str):
    """Extract latitude and longitude from geocode string."""
    if not isinstance(query_str, str):
        return None, None
    try:
        pattern = r'geocode:([-+]?\d+\.\d+),([-+]?\d+\.\d+)'
        match = re.search(pattern, query_str)
        if match:
            return float(match.group(1)), float(match.group(2))
    except:
        pass
    return None, None


df[['latitude', 'longitude']] = df['Query'].apply(
    lambda x: pd.Series(extract_coordinates(x))
)
df_geo = df.dropna(subset=['latitude', 'longitude']).copy()

print(f"[✓] Coordinates extracted: {len(df_geo)} valid records")
print(f"[✓] Latitude range: [{df_geo['latitude'].min():.6f}, {df_geo['latitude'].max():.6f}]")
print(f"[✓] Longitude range: [{df_geo['longitude'].min():.6f}, {df_geo['longitude'].max():.6f}]\n")

# =============================================================================
# DATA PROCESSING
# =============================================================================

print("[3/7] Processing data...\n")

# Convert to numeric
df_geo['Reply Count'] = pd.to_numeric(df_geo['Reply Count'], errors='coerce').fillna(0)
df_geo['Like Count'] = pd.to_numeric(df_geo['Like Count'], errors='coerce').fillna(0)

# Parse dates
try:
    df_geo['DateTime'] = pd.to_datetime(df_geo['Date'], errors='coerce')
    df_geo['hour'] = df_geo['DateTime'].dt.hour
except:
    print("[!] Warning: Could not parse dates")
    df_geo['hour'] = 0

# Calculate engagement
df_geo['total_engagement'] = df_geo['Reply Count'] + df_geo['Like Count']

print(f"[✓] Engagement - Min: {df_geo['total_engagement'].min():.0f}, "
      f"Max: {df_geo['total_engagement'].max():.0f}, "
      f"Mean: {df_geo['total_engagement'].mean():.2f}")
print(f"[✓] Likes - Min: {df_geo['Like Count'].min():.0f}, "
      f"Max: {df_geo['Like Count'].max():.0f}")
print(f"[✓] Replies - Min: {df_geo['Reply Count'].min():.0f}, "
      f"Max: {df_geo['Reply Count'].max():.0f}\n")

# =============================================================================
# SET GEOGRAPHIC EXTENT
# =============================================================================

print("[4/7] Setting geographic extent...\n")

if shapefile_bounds is not None:
    extent_minx, extent_miny, extent_maxx, extent_maxy = shapefile_bounds
    margin = 0.005
    extent_minx -= margin
    extent_miny -= margin
    extent_maxx += margin
    extent_maxy += margin
    print("[✓] Using shapefile bounds")
else:
    extent_minx = df_geo['longitude'].min() - 0.01
    extent_maxx = df_geo['longitude'].max() + 0.01
    extent_miny = df_geo['latitude'].min() - 0.01
    extent_maxy = df_geo['latitude'].max() + 0.01
    print("[✓] Using data extent")

print(f"[✓] Latitude: [{extent_miny:.6f}, {extent_maxy:.6f}]")
print(f"[✓] Longitude: [{extent_minx:.6f}, {extent_maxx:.6f}]\n")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def plot_boundary(ax, gdf, zorder_glow=9, zorder_main=10):
    """Plot geospatial boundary with glow effect."""
    if gdf is not None:
        # Glow effect
        gdf.boundary.plot(
            ax=ax, edgecolor='white', linewidth=2.0,
            zorder=zorder_glow, alpha=0.3, label='_nolegend_'
        )
        # Main boundary
        gdf.boundary.plot(
            ax=ax, edgecolor='black', linewidth=2.5,
            zorder=zorder_main, label='City Boundary'
        )

# =============================================================================
# VISUALIZATIONS
# =============================================================================

print("[5/7] Creating visualizations...\n")

os.makedirs(config.VISUALIZATION_OUTPUT_DIR, exist_ok=True)

# ========== VISUALIZATION 1: KDE HEATMAP ==========
print("[1/3] Creating KDE Heatmap...")

fig, ax = plt.subplots(figsize=(18, 14), dpi=300)

x = df_geo['longitude'].values
y = df_geo['latitude'].values

# Create grid
xx, yy = np.mgrid[extent_minx:extent_maxx:100j, extent_miny:extent_maxy:100j]

# Perform KDE
positions = np.vstack([xx.ravel(), yy.ravel()])
kernel = gaussian_kde(np.vstack([x, y]))
f = np.reshape(kernel(positions).T, xx.shape)

# Plot
contourf = ax.contourf(xx, yy, f, levels=20, cmap='YlOrRd', alpha=0.80, zorder=2)
contour = ax.contour(xx, yy, f, levels=10, colors='black', linewidths=0.5, alpha=0.3, zorder=3)

plot_boundary(ax, gdf)

ax.set_xlim(extent_minx, extent_maxx)
ax.set_ylim(extent_miny, extent_maxy)

cbar = plt.colorbar(contourf, ax=ax, label='Density', pad=0.02)
ax.set_title('Kernel Density Estimation (KDE) - Tweet Density', fontsize=14, fontweight='bold', pad=20)
ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, zorder=0)
ax.legend(loc='upper left', fontsize=11, framealpha=0.95)

plt.tight_layout()
output_path = os.path.join(config.VISUALIZATION_OUTPUT_DIR, '01_kde_heatmap.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"    [✓] Saved: {output_path}")
plt.close()

# ========== VISUALIZATION 2: ENGAGEMENT CONTOURS ==========
print("[2/3] Creating Engagement Contours...")

fig, ax = plt.subplots(figsize=(18, 14), dpi=300)

x = df_geo['longitude'].values
y = df_geo['latitude'].values
z = df_geo['total_engagement'].values

xx, yy = np.mgrid[extent_minx:extent_maxx:100j, extent_miny:extent_maxy:100j]
zz = griddata((x, y), z, (xx, yy), method='cubic')

contourf = ax.contourf(xx, yy, zz, levels=15, cmap='viridis', alpha=0.80, zorder=2)
contour = ax.contour(xx, yy, zz, levels=10, colors='white', linewidths=1.5, alpha=0.6, zorder=3)

plot_boundary(ax, gdf)

ax.set_xlim(extent_minx, extent_maxx)
ax.set_ylim(extent_miny, extent_maxy)

cbar = plt.colorbar(contourf, ax=ax, label='Engagement Level', pad=0.02)
ax.set_title('Engagement Contour Map - Tweet Engagement Isolines', fontsize=14, fontweight='bold', pad=20)
ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, zorder=0)
ax.legend(loc='upper left', fontsize=11, framealpha=0.95)

plt.tight_layout()
output_path = os.path.join(config.VISUALIZATION_OUTPUT_DIR, '02_engagement_contours.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"    [✓] Saved: {output_path}")
plt.close()

# ========== VISUALIZATION 3: HEXBIN GRID ==========
print("[3/3] Creating Hexagonal Grid...")

fig, ax = plt.subplots(figsize=(18, 14), dpi=300)

hexbin = ax.hexbin(
    df_geo['longitude'], df_geo['latitude'],
    C=df_geo['total_engagement'],
    gridsize=30,
    cmap='RdYlGn_r',
    edgecolors='black',
    linewidths=0.3,
    reduce_C_function=np.sum,
    mincnt=1,
    zorder=2
)

plot_boundary(ax, gdf)

ax.set_xlim(extent_minx, extent_maxx)
ax.set_ylim(extent_miny, extent_maxy)

cbar = plt.colorbar(hexbin, ax=ax, label='Total Engagement', pad=0.02)
ax.set_title('Hexagonal Grid Aggregation - Engagement by Cell', fontsize=14, fontweight='bold', pad=20)
ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, zorder=0)
ax.legend(loc='upper left', fontsize=11, framealpha=0.95)

plt.tight_layout()
output_path = os.path.join(config.VISUALIZATION_OUTPUT_DIR, '03_hexbin_grid.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"    [✓] Saved: {output_path}")
plt.close()

# =============================================================================
# SUMMARY
# =============================================================================

print("\n" + "="*80)
print("VISUALIZATION COMPLETE")
print("="*80)
print(f"[✓] Generated 3 maps")
print(f"[✓] Output directory: {config.VISUALIZATION_OUTPUT_DIR}")
print(f"[✓] Map files:")
print(f"    - 01_kde_heatmap.png")
print(f"    - 02_engagement_contours.png")
print(f"    - 03_hexbin_grid.png")
print("="*80 + "\n")

print("[6/7] Maps created successfully!")
print("[7/7] You can now view the PNG files in the output directory")
print("\n✓ All done! Check the maps/ folder for your visualizations.\n")
