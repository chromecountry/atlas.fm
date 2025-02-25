from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
import backoff


class GeocodingService:
    def __init__(self):
        self.geolocator = Nominatim(
            user_agent="Atlas.fm shulalex1998@gmail.com",
            timeout=5
        )

    @backoff.on_exception(
        backoff.expo,
        (GeocoderTimedOut, GeocoderServiceError),
        max_tries=3
    )
    def get_coordinates(self, location_str):
        time.sleep(1)  # Rate limiting
        location = self.geolocator.geocode(location_str)

        if not location and ',' in location_str:
            shorter_location = ','.join(
                location_str.rsplit(',', 1)[0].split(',')
            )
            time.sleep(1)
            location = self.geolocator.geocode(shorter_location)

        if location:
            return (location.latitude, location.longitude)
        return None
