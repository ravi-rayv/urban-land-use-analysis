import os
import re
import gc
import time
import errno
import typing as t
from dataclasses import dataclass, field

import requests
import pandas as pd

# Import configuration and constants
import config
import constants

# =============================================================================
# AUTHENTICATION
# =============================================================================

def get_auth_headers(api_token: str) -> t.Tuple[dict, str]:
    """Get authentication headers for Bearer token."""
    return {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }, "Bearer Token"


def get_alt_auth_headers(api_token: str) -> t.List[t.Tuple[dict, str]]:
    """Get alternative authentication headers for fallback."""
    return [
        ({"X-API-Key": api_token, "Content-Type": "application/json"}, "X-API-Key Header"),
        ({"Authorization": f"Token {api_token}", "Content-Type": "application/json"}, "Token Header"),
        ({"Authorization": api_token, "Content-Type": "application/json"}, "Direct Token"),
    ]

# =============================================================================
# UTILITIES
# =============================================================================

def ensure_parent_dir(path: str) -> None:
    """Ensure parent directory exists."""
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        try:
            os.makedirs(parent, exist_ok=True)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


def clean_text_content(text: str) -> str:
    """Clean tweet text: remove URLs and special characters."""
    if not text:
        return ""
    # Remove URLs
    text = re.sub(r'(?:https?|ftp)://\S+', '', text)
    # Remove special characters, keep alphanumeric and spaces
    text = re.sub(r'[^a-z0-9\s]', '', text, flags=re.IGNORECASE)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def iter_queries(
    locations: t.List[t.Dict[str, str]],
    keywords: t.List[str],
    max_locations: t.Optional[int] = None,
    max_keywords: t.Optional[int] = None,
    max_queries: t.Optional[int] = None,
) -> t.Iterator[t.Dict[str, str]]:
    """
    Generate search queries from locations and keywords.
    
    Yields:
        dict with keys: query, location_name, geo, keyword
    """
    locs = locations if max_locations is None else locations[:max_locations]
    keys = keywords if max_keywords is None else keywords[:max_keywords]
    count = 0
    
    for loc in locs:
        geo = loc["geo"]
        loc_name = loc.get("name", "")
        for kw in keys:
            yield {
                "query": f"{kw} geocode:{geo}",
                "location_name": loc_name,
                "geo": geo,
                "keyword": kw,
            }
            count += 1
            if max_queries is not None and count >= max_queries:
                return

# =============================================================================
# NETWORK CLIENT
# =============================================================================

class TwitterClient:
    """Client for Twitter API communication."""
    
    def __init__(self, api_token: str, timeout: int = 30):
        """Initialize Twitter API client."""
        self.api_token = api_token
        self.timeout = timeout
        self.session = requests.Session()

    def fetch(self, query: str, retry_alt: bool = True) -> t.Tuple[dict, str]:
        """
        Fetch tweets from API with fallback authentication.
        
        Args:
            query: Search query string
            retry_alt: Whether to retry with alternative auth methods
            
        Returns:
            Tuple of (response_dict, auth_method_used)
        """
        headers, method = get_auth_headers(self.api_token)
        params = {"query": query}
        
        try:
            resp = self.session.get(
                config.API_BASE_URL,
                headers=headers,
                params=params,
                timeout=self.timeout
            )
            
            if resp.status_code == 200:
                return resp.json(), method
            
            # Retry with alternative auth methods
            if resp.status_code == 401 and retry_alt:
                for alt_headers, alt_method in get_alt_auth_headers(self.api_token):
                    try:
                        alt_resp = self.session.get(
                            config.API_BASE_URL,
                            headers=alt_headers,
                            params=params,
                            timeout=self.timeout
                        )
                        if alt_resp.status_code == 200:
                            return alt_resp.json(), alt_method
                    except Exception:
                        continue
                
                return {
                    "error": {
                        "message": "401 Unauthorized - Token may be invalid or expired"
                    }
                }, method
            
            # Handle HTTP errors
            try:
                resp.raise_for_status()
            except requests.HTTPError as e:
                return {
                    "error": {"message": f"HTTP {resp.status_code}: {str(e)}"}
                }, method
            
            return {"error": {"message": f"HTTP {resp.status_code}"}}, method
            
        except requests.RequestException as e:
            return {"error": {"message": str(e)}}, method

# =============================================================================
# DATA PROCESSING
# =============================================================================

EXPECTED_COLS = [
    "Query", "Date", "Tweet by", "Text Content", 
    "Reply Count", "Like Count", "Tweet URL", 
    "Profile User Name", "Profile Description",
    "No Results", "Error", "Auth Method"
]


def flatten_one(response: dict, method: str, query_obj: dict) -> t.List[dict]:
    """
    Parse API response and flatten to list of rows.
    
    Args:
        response: API response dictionary
        method: Authentication method used
        query_obj: Query object with query text
        
    Returns:
        List of flattened tweet dictionaries
    """
    qtext = query_obj.get("query", "")
    
    # Handle error responses
    if "error" in response:
        return [{
            "Query": qtext,
            "Date": "",
            "Tweet by": "",
            "Text Content": "",
            "Reply Count": 0,
            "Like Count": 0,
            "Tweet URL": "",
            "Profile User Name": "",
            "Profile Description": "",
            "No Results": True,
            "Error": str(response["error"].get("message", response["error"])),
            "Auth Method": method,
        }]

    # Extract tweets from response
    resp_data = response.get("response", response)
    tweets = resp_data.get("tweets", resp_data.get("data", [])) or []

    # Handle no results
    if not tweets:
        return [{
            "Query": qtext,
            "Date": "",
            "Tweet by": "",
            "Text Content": "",
            "Reply Count": 0,
            "Like Count": 0,
            "Tweet URL": "",
            "Profile User Name": "",
            "Profile Description": "",
            "No Results": True,
            "Error": "",
            "Auth Method": method,
        }]

    # Parse tweets
    rows: t.List[dict] = []
    for tw in tweets:
        url = tw.get("url", "")
        if not url and tw.get("id") and tw.get("author", {}).get("userName"):
            url = f"https://twitter.com/{tw['author']['userName']}/status/{tw['id']}"

        row = {
            "Query": qtext,
            "Date": tw.get("createdAt", tw.get("created_at", "")),
            "Tweet by": tw.get("author", {}).get("name", tw.get("user", {}).get("name", "")),
            "Text Content": clean_text_content(tw.get("text", "") or ""),
            "Reply Count": int(tw.get("replyCount", tw.get("public_metrics", {}).get("reply_count", 0)) or 0),
            "Like Count": int(tw.get("likeCount", tw.get("public_metrics", {}).get("like_count", 0)) or 0),
            "Tweet URL": url,
            "Profile User Name": tw.get("author", {}).get("userName", tw.get("user", {}).get("screen_name", "")),
            "Profile Description": tw.get("author", {}).get("description", tw.get("user", {}).get("description", "")),
            "No Results": False,
            "Error": "",
            "Auth Method": method,
        }
        rows.append(row)
    
    return rows


def to_ordered_df(rows: t.List[dict]) -> pd.DataFrame:
    """
    Convert list of dicts to ordered DataFrame.
    
    Args:
        rows: List of tweet dictionaries
        
    Returns:
        Ordered pandas DataFrame
    """
    if not rows:
        return pd.DataFrame(columns=EXPECTED_COLS)
    
    df = pd.DataFrame(rows)

    # Add missing columns
    for col in EXPECTED_COLS:
        if col not in df.columns:
            if col in ("Reply Count", "Like Count"):
                df[col] = 0
            elif col == "No Results":
                df[col] = False
            else:
                df[col] = ""

    # Reorder columns
    df = df[EXPECTED_COLS]

    # Convert numeric columns
    for c in ("Reply Count", "Like Count"):
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    
    for c in df.columns:
        if c not in ("Reply Count", "Like Count", "No Results"):
            df[c] = df[c].astype(str)

    # Remove error rows
    if "No Results" in df.columns:
        df = df[~df["No Results"].astype(bool)].copy()

    # Fill NaN
    df = df.fillna("")
    
    return df

# =============================================================================
# PIPELINE
# =============================================================================

@dataclass
class RunConfig:
    """Configuration for pipeline run."""
    api_token: str = config.TWITTER_API_TOKEN
    csv_filename: str = config.CSV_OUTPUT_FILENAME
    batch_size: int = 200
    sleep_seconds: float = 0.25
    timeout: int = 30
    verbose_every: int = 250
    max_locations: t.Optional[int] = None
    max_keywords: t.Optional[int] = None
    max_queries: t.Optional[int] = None


@dataclass
class RunStats:
    """Statistics from pipeline run."""
    total_queries: int = 0
    total_rows_written: int = 0
    total_likes: int = 0
    total_replies: int = 0
    errors_sample: t.List[str] = field(default_factory=list)


def run_pipeline_streaming(
    locations: t.List[t.Dict[str, str]],
    keywords: t.List[str],
    cfg: RunConfig = None,
) -> RunStats:
    """
    Main streaming pipeline for tweet collection.
    
    Args:
        locations: List of location dicts with geo and name
        keywords: List of keywords to search
        cfg: RunConfig object with settings
        
    Returns:
        RunStats with collection results
    """
    if cfg is None:
        cfg = RunConfig()
    
    ensure_parent_dir(cfg.csv_filename)
    header_written = os.path.exists(cfg.csv_filename) and os.path.getsize(cfg.csv_filename) > 0

    client = TwitterClient(api_token=cfg.api_token, timeout=cfg.timeout)
    batch: t.List[dict] = []
    stats = RunStats()

    print("=" * 80)
    print("STARTING TWEET COLLECTION PIPELINE")
    print("=" * 80)
    print(f"Output CSV: {cfg.csv_filename}")
    print(f"Batch size: {cfg.batch_size}")
    print(f"Sleep between requests: {cfg.sleep_seconds}s")
    print("=" * 80)
    print()

    try:
        for i, qobj in enumerate(
            iter_queries(
                locations=locations,
                keywords=keywords,
                max_locations=cfg.max_locations,
                max_keywords=cfg.max_keywords,
                max_queries=cfg.max_queries,
            ),
            start=1,
        ):
            stats.total_queries += 1
            resp, method = client.fetch(qobj["query"])
            rows = flatten_one(resp, method, qobj)

            # Track errors
            if rows and rows[0].get("Error"):
                if len(stats.errors_sample) < 5:
                    stats.errors_sample.append(f"{rows[0]['Error'][:120]}")

            # Add successful rows to batch
            for r in rows:
                if not r.get("No Results", False) and not r.get("Error"):
                    stats.total_likes += int(r.get("Like Count", 0) or 0)
                    stats.total_replies += int(r.get("Reply Count", 0) or 0)
                    batch.append(r)

            # Write batch to CSV
            if len(batch) >= cfg.batch_size:
                df = to_ordered_df(batch)
                if not df.empty:
                    df.to_csv(
                        cfg.csv_filename,
                        mode="a",
                        header=not header_written,
                        index=False,
                        encoding="utf-8"
                    )
                    header_written = True
                    stats.total_rows_written += len(df)
                batch.clear()
                gc.collect()

            # Progress update
            if cfg.verbose_every and i % cfg.verbose_every == 0:
                print(f"Progress: {i:,} queries processed | Rows written: {stats.total_rows_written:,}")

            # Rate limiting
            if cfg.sleep_seconds:
                time.sleep(cfg.sleep_seconds)

        # Write remaining batch
        if batch:
            df = to_ordered_df(batch)
            if not df.empty:
                df.to_csv(
                    cfg.csv_filename,
                    mode="a",
                    header=not header_written,
                    index=False,
                    encoding="utf-8"
                )
                stats.total_rows_written += len(df)
            batch.clear()

    except MemoryError:
        print("Memory error! Writing remaining batch...")
        if batch:
            try:
                df = to_ordered_df(batch)
                if not df.empty:
                    df.to_csv(
                        cfg.csv_filename,
                        mode="a",
                        header=not header_written,
                        index=False,
                        encoding="utf-8"
                    )
                    stats.total_rows_written += len(df)
            except Exception:
                pass
        raise

    # Summary
    print()
    print("=" * 80)
    print("COLLECTION COMPLETE")
    print("=" * 80)
    print(f"Total queries: {stats.total_queries:,}")
    print(f"Rows written: {stats.total_rows_written:,}")
    print(f"Total likes: {stats.total_likes:,}")
    print(f"Total replies: {stats.total_replies:,}")
    print(f"Output file: {os.path.abspath(cfg.csv_filename)}")
    
    if stats.errors_sample:
        print("\nSample errors:")
        for e in stats.errors_sample:
            print(f"  - {e}")
    
    print("=" * 80)
    print()
    
    return stats

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("\n[INFO] Loading configuration...")
    
    # Get locations and keywords from constants
    try:
        locations = constants.LOCATIONS
        keywords = constants.KEYWORDS
        print(f"[INFO] Loaded {len(locations)} locations and {len(keywords)} keywords")
    except Exception as e:
        print(f"[ERROR] Could not load constants: {e}")
        exit(1)

    # Verify API token
    if "YOUR_API_TOKEN" in config.TWITTER_API_TOKEN or not config.TWITTER_API_TOKEN:
        print("[ERROR] API token not configured in config.py")
        print("Please add your Twitter Bearer token to config.py")
        exit(1)

    # Create configuration
    cfg = RunConfig(
        api_token=config.TWITTER_API_TOKEN,
        csv_filename=config.CSV_OUTPUT_FILENAME,
        batch_size=200,
        sleep_seconds=0.25,
        timeout=30,
        verbose_every=250,
        max_locations=None,  # Set to limit locations
        max_keywords=None,   # Set to limit keywords
        max_queries=None,    # Set to limit total queries
    )

    # Run pipeline
    try:
        stats = run_pipeline_streaming(locations, keywords, cfg)
        print(f"\n[SUCCESS] Collected {stats.total_rows_written} tweets!")
    except KeyboardInterrupt:
        print("\n[INFO] Collection interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        exit(1)
