from app.models.map_model import MapModel
from app.views.map_view import MapView
from app.services.geocoding_service import GeocodingService


class MapController:
    def __init__(self, library_controller, assets_path,
                 output_path, geocode_cache_path):
        self.library_controller = library_controller
        geocoding_service = GeocodingService()
        self.map_model = MapModel(
            geocoding_service=geocoding_service,
            cache_path=geocode_cache_path
        )
        self.map_view = MapView(assets_path=assets_path)
        self.output_path = output_path

    def generate_map(self, use_cache=True):
        library = self.library_controller.build_complete_library(use_cache)
        artist_locations = self.map_model.process_artist_locations(library)
        return self.map_view.create_map(artist_locations, self.output_path)
