from concurrent.futures import ThreadPoolExecutor
import time
from tqdm import tqdm
import colorama
from app.util.utils import trim_year
import json

from pathlib import Path
PROJECT_ROOT = Path(__file__).absolute().parents[1]
import sys; sys.path.append(str(PROJECT_ROOT))  # noqa

colorama.init()


class SpotifyModel:
    def __init__(self, spotify_service):
        self.service = spotify_service
        self.library = {}

    def get_user_library(self):
        start_time = time.time()

        initial_response = self.service.get_saved_tracks(limit=1)
        total_tracks = initial_response['total']
        offsets = range(0, total_tracks, 20)

        # Create progress bar
        pbar = tqdm(
            total=total_tracks,
            desc="Retrieving tracks",
            colour='green',
            bar_format='{l_bar}{bar:30}{r_bar}'
        )

        # Iterate through library 20 tracks at a time
        results = []
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [
                executor.submit(self.service.get_saved_tracks, offset)
                for offset in offsets
            ]
            for f in futures:
                result = f.result()
                results.append(result)
                pbar.update(len(result['items']))
        pbar.close()

        # Compile all results
        tracks = []
        for result in results:
            tracks.extend(result['items'])

        execution_time = time.time() - start_time
        print(f'Track Retrieval Execution time: {execution_time:.2f} seconds')
        print(f'Expected tracks: {total_tracks}')
        print(f'Retrieved tracks: {len(tracks)}')
        print(f'Match: {total_tracks == len(tracks)}')

        start_time = time.time()
        self.library = self.build_library(tracks)
        execution_time = time.time() - start_time
        print(f'Library Cleanup Execution time: {execution_time:.2f} seconds')

        return self.library

    def build_library(self, tracks):
        pbar = tqdm(
            total=len(tracks),
            desc='Building library',
            colour='green',
            bar_format='{l_bar}{bar:30}{r_bar}'
        )

        for track_item in tracks:
            track = track_item['track']
            artist = track['artists'][0]['name']

            if artist not in self.library:
                self.library[artist] = self.process_artist(
                    track['artists'][0]
                )

            self.library[artist]['songs'][track['uri']] = (
                self.process_track(track)
            )
            pbar.update(1)

        pbar.close()
        return self.library

    def process_track(self, track):
        return {
            'name': track['name'],
            'popularity': track['popularity'],
            'release_date': trim_year(track['album']['release_date']),
            'id': track['id']
        }

    def process_artist(self, artist_data):
        return {
            'songs': {},
            'artist_uri': artist_data['uri'],
            'artist_id': artist_data['id'],
            # TODO: Either remove or leverage popularity
            # to get niche artists location from other sources such as bandcamp
            # 'artist_popularity' = self.sp.artist(
            #     self.library[artist]['artist_id'])['popularity']
        }

    def save_library(self, filepath):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.library, f, indent=4, ensure_ascii=False)
            print(f'Library saved to {filepath}')
        except Exception as e:
            print(f'Error saving library: {e}')

    def load_library(self, filepath):
        """Load library from JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.library = json.load(f)
            print(f'Library loaded from {filepath}')

            return self.library
        except Exception as e:
            print(f'Error loading library: {e}')

            return None
