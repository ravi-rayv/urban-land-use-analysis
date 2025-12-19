

import os
import re
import numpy as np
from typing import Tuple, Optional


def ensure_directory_exists(path: str) -> None:
    """
    Ensure a directory exists, create if needed.
    
    Args:
        path: Directory path to create
    """
    os.makedirs(path, exist_ok=True)


def clean_text(text: str, remove_urls: bool = True, remove_special_chars: bool = True) -> str:
    """
    Clean text by removing URLs and special characters.
    
    Args:
        text: Text to clean
        remove_urls: Whether to remove URLs
        remove_special_chars: Whether to remove special characters
        
    Returns:
        Cleaned text
    """
    if not text or not isinstance(text, str):
        return ""
    
    if remove_urls:
        text = re.sub(r'(?:https?|ftp)://\S+', '', text)
    
    if remove_special_chars:
        text = re.sub(r'[^a-z0-9\s]', '', text, flags=re.IGNORECASE)
    
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_geocode_string(query: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Extract latitude and longitude from geocode string.
    
    Expected format: "geocode:lat,lon"
    
    Args:
        query: Query string containing geocode
        
    Returns:
        Tuple of (latitude, longitude) or (None, None)
    """
    if not isinstance(query, str):
        return None, None
    
    try:
        pattern = r'geocode:([-+]?\d+\.\d+),([-+]?\d+\.\d+)'
        match = re.search(pattern, query)
        if match:
            lat = float(match.group(1))
            lon = float(match.group(2))
            return lat, lon
    except (ValueError, AttributeError):
        pass
    
    return None, None


def format_number(num: float, decimals: int = 2) -> str:
    """
    Format number with thousand separators.
    
    Args:
        num: Number to format
        decimals: Number of decimal places
        
    Returns:
        Formatted string
    """
    if isinstance(num, int):
        return f"{num:,}"
    return f"{num:,.{decimals}f}"


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate approximate distance between two coordinates in kilometers.
    Uses Haversine formula for rough estimation.
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
        
    Returns:
        Distance in kilometers
    """
    from math import radians, cos, sin, asin, sqrt
    
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    
    return km


def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Validate latitude and longitude values.
    
    Args:
        lat: Latitude value
        lon: Longitude value
        
    Returns:
        True if valid, False otherwise
    """
    try:
        lat_float = float(lat)
        lon_float = float(lon)
        return -90 <= lat_float <= 90 and -180 <= lon_float <= 180
    except (ValueError, TypeError):
        return False


def get_file_size(filepath: str) -> str:
    """
    Get human-readable file size.
    
    Args:
        filepath: Path to file
        
    Returns:
        Size as formatted string (e.g., "1.5 MB")
    """
    if not os.path.exists(filepath):
        return "N/A"
    
    size = os.path.getsize(filepath)
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    
    return f"{size:.2f} TB"


def count_lines(filepath: str) -> int:
    """
    Count lines in a file.
    
    Args:
        filepath: Path to file
        
    Returns:
        Number of lines
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


class ProgressTracker:
    """Simple progress tracker for iterations."""
    
    def __init__(self, total: int, name: str = "Progress"):
        self.total = total
        self.name = name
        self.current = 0
    
    def update(self, increment: int = 1):
        """Update progress."""
        self.current += increment
        percent = (self.current / self.total) * 100
        print(f"{self.name}: {self.current}/{self.total} ({percent:.1f}%)", end='\r')
    
    def finish(self):
        """Mark as finished."""
        print(f"{self.name}: {self.total}/{self.total} (100.0%)")


# Example usage functions
def example_clean_text():
    """Example of text cleaning."""
    text = "Check out this amazing location! https://example.com #Urban"
    cleaned = clean_text(text)
    print(f"Original: {text}")
    print(f"Cleaned: {cleaned}")


def example_parse_geocode():
    """Example of parsing geocode."""
    query = "Houses geocode:19.0760,72.8777"
    lat, lon = parse_geocode_string(query)
    print(f"Query: {query}")
    print(f"Latitude: {lat}, Longitude: {lon}")


if __name__ == "__main__":
    # Run examples
    print("Utility Functions Examples\n")
    example_clean_text()
    print()
    example_parse_geocode()
