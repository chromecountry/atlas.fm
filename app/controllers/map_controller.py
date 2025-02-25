from flask import (
    redirect, session, render_template, send_file
)
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

    def show_map_page(self):
        if not session.get('token_info'):
            return redirect('/login')
        return render_template('loading.html')

    def generate_map(self, use_cache=True):
        if not session.get('token_info'):
            return redirect('/login')

        library = self.library_controller.build_complete_library(use_cache)
        artist_locations = self.map_model.process_artist_locations(library)
        try:
            map_path = self.map_view.create_map(
                artist_locations, self.output_path
            )
            return send_file(map_path)
        except Exception as e:
            print(f"Error generating map: {e}")
            return redirect('/')
