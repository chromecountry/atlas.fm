import musicbrainzngs as mb
from credentials import MusicBrainz as MusicBrainzCredentials
import backoff


class MusicBrainzService:
    def __init__(self):
        mb.set_useragent("Atlas.fm", "1.0")
        try:
            mb.auth(
                MusicBrainzCredentials.USERNAME,
                MusicBrainzCredentials.PASSWORD
            )
        except Exception as e:
            print(f"Error authenticating with MusicBrainz: {e}")

    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=3
    )
    def search_artist(self, name):
        return mb.search_artists(artist=name, limit=1)
