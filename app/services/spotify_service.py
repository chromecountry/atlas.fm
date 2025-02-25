import backoff
from spotipy.exceptions import SpotifyException


class SpotifyService:
    def __init__(self, spotify_client):
        self.sp = spotify_client

    @backoff.on_exception(
        backoff.expo,
        SpotifyException,
        max_tries=5
    )
    def get_saved_tracks(self, offset=0, limit=20):
        return self.sp.current_user_saved_tracks(limit=limit, offset=offset)
