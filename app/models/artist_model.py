import time
from concurrent.futures import ThreadPoolExecutor
import backoff
from tqdm import tqdm
import json

from pathlib import Path
PROJECT_ROOT = Path(__file__).absolute().parents[2]
import sys; sys.path.append(str(PROJECT_ROOT))  # noqa


class ArtistModel:
    RATE_LIMIT = 1  # seconds between API calls
    MAX_WORKERS = 8
    MAX_RETRIES = 3

    def __init__(self, cache_path, musicbrainz_service):
        self.service = musicbrainz_service
        self.cache_path = cache_path
        self.cache = self._load_cache()

    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=MAX_RETRIES
    )
    def get_artist_location(self, artist_name):
        # From ArtistEnricher._get_artist_location()
        # MusicBrainz API call logic
        """Get artist location from cache or MusicBrainz API."""
        # Check cache first
        if artist_name in self.cache:
            cached_data = self.cache[artist_name]
            return cached_data

        # Get from API
        time.sleep(self.RATE_LIMIT)
        result = self.service.search_artist(artist=artist_name, limit=1)

        if not result['artist-list']:
            origin_data = {'status': 'not_found'}
            self.cache[artist_name] = origin_data
            self._save_cache()
            return origin_data

        artist_info = result['artist-list'][0]
        origin_data = self._extract_location_data(artist_info)
        self.cache[artist_name] = origin_data
        self._save_cache()

        return origin_data

    def extract_location_data(self, artist_info):
        # From ArtistEnricher._extract_location_data()
        # Parse location fields
        """Extract location data from artist info."""
        origin_data = {
            'city': artist_info.get('begin-area', {}).get('name'),
            'country': artist_info.get('country'),
            'area': artist_info.get('area', {}).get('name'),
            'status': 'success'
        }

        return origin_data

    def _process_artist(self, artist_tuple):
        """Process a single artist."""
        artist_name, artist_data = artist_tuple
        try:
            return artist_name, self.get_artist_location(artist_name)
        except Exception as e:
            return artist_name, {
                'status': 'error',
                'error': str(e)
            }

    def enrich_artists(self, library):
        """Enrich library with artist location data."""
        print("Enriching artist locations from MusicBrainz...")
        enriched_library = library.copy()

        with tqdm(
            total=len(library),
            desc="Getting artist locations",
            colour='green',
            bar_format='{l_bar}{bar:30}{r_bar}'
        ) as pbar:
            with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
                futures = [
                    executor.submit(self._process_artist, artist_tuple)
                    for artist_tuple in library.items()
                ]
                for future in futures:
                    artist_name, origin_data = future.result()
                    enriched_library[artist_name]['origin'] = origin_data
                    pbar.update(1)

        return enriched_library

    def _load_cache(self):
        """Load existing cache or create new one."""
        try:
            if Path(self.cache_path).exists():
                with open(self.cache_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading cache: {e}")
        return {}

    def _save_cache(self):
        """Save cache to file."""
        try:
            with open(self.cache_path, 'w') as f:
                json.dump(self.cache, f)
        except Exception as e:
            print(f"Error saving cache: {e}")

    # TODO: def validate_location_data(self, location_data):
    #     # Validation logic
