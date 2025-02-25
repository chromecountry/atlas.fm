import folium
from folium.plugins import MarkerCluster

from pathlib import Path
PROJECT_ROOT = Path(__file__).absolute().parents[2]
import sys; sys.path.append(str(PROJECT_ROOT))  # noqa


class MapView:
    def __init__(self, assets_path):
        self.assets_path = assets_path

    # todo: clean up
    def create_map(self, artist_locations, output_path):
        """Create an interactive map of artist locations."""
        m = self._initialize_map()
        self._load_assets(m)
        cluster_group, individual_group = self._create_marker_groups(m)
        self._add_markers(cluster_group, individual_group, artist_locations)
        individual_group.add_to(m)
        folium.LayerControl(collapsed=False).add_to(m)
        m.save(output_path)
        return output_path

    def _initialize_map(self):
        return folium.Map(
            location=[20, 0],
            zoom_start=2,
            world_copy_jump=False,
            no_wrap=True,
            min_lon=-180,
            max_lon=180,
            min_lat=-90,
            max_lat=90,
            max_bounds=True
        )

    def _load_assets(self, m):
        css_path = Path(self.assets_path) / 'css' / 'tooltip.css'
        js_path = Path(self.assets_path) / 'js' / 'map_bounds.js'

        with open(css_path) as f:
            css = f"<style>{f.read()}</style>"
        m.get_root().html.add_child(folium.Element(css))

        with open(js_path) as f:
            script = f"<script>{f.read()}</script>"
        m.get_root().html.add_child(folium.Element(script))

    def _create_marker_groups(self, m):
        cluster_group = MarkerCluster(
            name='Clustered View',
            options={
                'maxClusterRadius': 30,
                'disableClusteringAtZoom': 8,
                'spiderfyOnMaxZoom': True
            }
        ).add_to(m)

        individual_group = folium.FeatureGroup(
            name='Individual Points',
            show=False
        )
        return cluster_group, individual_group

    def _add_markers(self, cluster_group, individual_group, artist_locations):
        for coords, artists in artist_locations.items():
            base_lat, base_lng = coords
            for i, artist in enumerate(artists):
                offset = i * 0.0001
                adjusted_coords = (base_lat + offset, base_lng + offset)
                tooltip_html = f'<div class="custom-tooltip">{artist}</div>'

                self._create_marker(
                    adjusted_coords,
                    artist,
                    tooltip_html,
                    'red',
                    cluster_group
                )

                self._create_marker(
                    adjusted_coords,
                    artist,
                    tooltip_html,
                    'blue',
                    individual_group
                )

    def _create_marker(self, coords, artist, tooltip_html, color, group):
        folium.CircleMarker(
            location=coords,
            radius=3,
            popup=folium.Popup(artist, max_width=200),
            tooltip=folium.Tooltip(
                tooltip_html,
                permanent=False,
                sticky=True
            ),
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7
        ).add_to(group)
