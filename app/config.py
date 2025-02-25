import secrets
from pathlib import Path


class Config:
    # Base Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / 'data'
    STATIC_DIR = PROJECT_ROOT / 'app' / 'static'

    # Cache paths
    CACHE_DIR = DATA_DIR / 'cache'
    LIBRARY_CACHE_PATH = CACHE_DIR / 'library_cache.json'
    MB_CACHE_PATH = CACHE_DIR / 'mb_cache.json'
    GEOCODE_CACHE_PATH = CACHE_DIR / 'geocode_cache.json'

    # Output paths
    OUTPUT_DIR = DATA_DIR / 'output'
    MAP_OUTPUT_PATH = OUTPUT_DIR / 'artist_map.html'

    # Asset paths
    ASSETS_PATH = STATIC_DIR

    # Create directories if they don't exist
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    SECRET_KEY = secrets.token_hex(16)
    SESSION_TYPE = 'filesystem'
