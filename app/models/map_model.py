import json

from pathlib import Path
PROJECT_ROOT = Path(__file__).absolute().parents[2]
import sys; sys.path.append(str(PROJECT_ROOT))  # noqa


class MapModel:
    def __init__(self, geocoding_service, cache_path):
        self.service = geocoding_service
        self.cache_file = cache_path
        self.location_cache = self._load_cache()

    def process_artist_locations(self, library):
        """Process and return artist locations."""
        artist_locations = {}

        for artist, data in library.items():
            if 'origin' in data and data['origin'].get('status') == 'success':
                location_str = self._get_location_string(data['origin'])
                if location_str:
                    coords = self._geocode_location(location_str)
                    if coords:
                        if coords not in artist_locations:
                            artist_locations[coords] = []
                        artist_locations[coords].append(artist)
        return artist_locations

    def _get_location_string(self, artist_data):
        location_parts = []
        if artist_data.get('city'):
            location_parts.append(artist_data['city'])
        if artist_data.get('area'):
            location_parts.append(artist_data['area'])
        if artist_data.get('country'):
            location_parts.append(artist_data['country'])
        return ", ".join(location_parts)

    def _geocode_location(self, location_str):
        if location_str in self.location_cache:
            return tuple(self.location_cache[location_str])

        try:
            coords = self.service.get_coordinates(location_str)
            if coords:
                self.location_cache[location_str] = coords
                self._save_cache()
                return coords
        except Exception as e:
            print(f"Error geocoding location: {location_str}: {e}")
        return None

    def _load_cache(self):
        try:
            if Path(self.cache_file).exists():
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading cache: {e}")
        return {}

    def _save_cache(self):
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.location_cache, f)
        except Exception as e:
            print(f"Error saving cache: {e}")
