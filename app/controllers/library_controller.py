from pathlib import Path
from app.models.spotify_model import SpotifyModel
from app.models.artist_model import ArtistModel
from app.services.spotify_service import SpotifyService
from app.services.musicbrainz_service import MusicBrainzService
import spotipy


class LibraryController:
    def __init__(
            self,
            spotify_token,
            library_cache_path,
            mb_cache_path
    ):
        spotify_client = spotipy.Spotify(auth=spotify_token)
        spotify_service = SpotifyService(spotify_client)
        musicbrainz_service = MusicBrainzService()
        self.spotify_model = SpotifyModel(spotify_service)
        self.artist_model = ArtistModel(
            musicbrainz_service=musicbrainz_service,
            cache_path=mb_cache_path
        )
        # todo: move this logic back into spotify model
        self.cache_path = library_cache_path

    def build_complete_library(self, use_cache=True):
        """Build complete library with artist locations."""
        try:
            # Get base library
            library = self._get_base_library(use_cache)

            # Enrich with locations
            enriched_library = self.artist_model.enrich_artists(library)

            return enriched_library

        except Exception as e:
            raise e

    def _get_base_library(self, use_cache):
        """Get library from cache or Spotify."""
        if use_cache and self._cache_exists():
            return self.spotify_model.load_library(self.cache_path)

        # todo: does it make sense to move
        # some of the library building logic up from the model?
        library = self.spotify_model.get_user_library()
        self.spotify_model.save_library(self.cache_path)
        return library

    def _cache_exists(self):
        return Path(self.cache_path).exists()
