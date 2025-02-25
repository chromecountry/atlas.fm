# Atlas.fm

***
***

## Preamble ##

This document makes the following assumptions:

- developers have a working knowledge of:
  - Flask web applications
  - MVC architecture patterns
  - API service layers

- developers have a thorough knowledge of:
  - Python, Flask, Spotipy
  - MusicBrainz API
  - Web mapping with Folium

## Introduction ##

Atlas.fm is a Flask web application that:

1. implements MVC architecture with:
    1. Models for data handling
    1. Views for presentation
    1. Controllers for business logic
    1. Services for API interactions

2. provides the following features:
    1. Spotify library visualization
    1. Artist origin mapping
    1. Clustered/individual markers
    1. Caching system

These functionalities are served through a Flask application. Component logic
lives within the `app/` directory.

## Configuration ##

### Environment Variables ###

### credentials.py ###

Create a credentials.py file with the following classes:

```python
class Spotipy:
    SPOTIPY_CLIENT_ID = "your_spotify_client_id"
    SPOTIPY_CLIENT_SECRET = "your_spotify_client_secret"
    SCOPE = "user-library-read"

class MusicBrainz:
    USERNAME = "your_musicbrainz_username"
    PASSWORD = "your_musicbrainz_password"
```

### Installation ###

Ensure Python 3.8 or greater is available in the environment. If using virtual
environments, ensure the correct one is active.

To install required packages:

```bash
pip install -r requirements.txt
```

## Project Structure ##

### Directory Layout ###

```
app/
├── controllers/      # Application logic
│   ├── library_controller.py
│   └── map_controller.py
├── models/          # Data models
│   ├── spotify_model.py
│   ├── artist_model.py
│   └── map_model.py
├── services/        # API interactions
│   ├── spotify_service.py
│   ├── musicbrainz_service.py
│   └── geocoding_service.py
├── views/          # Presentation layer
│   ├── templates/
│   └── map_view.py
└── utils/          # Helper functions
```

### Cache System ###

The application maintains caches for:
- Spotify library data
- MusicBrainz artist origins
- Geocoding results

Cache files are stored in `data/cache/`.

## Execution ##

### Running the Application ###

To run Atlas.fm:

```bash
python run.py
```

Navigate to `http://localhost:5000`

### Authentication Flow ###

1. Login with Spotify credentials
2. Authorize application access
3. Redirect to map generation

### Output ###

The application generates:
- `artist_map.html`: Interactive map visualization
- Cache files for API responses
- Session data for authentication

### Sample Output Structure ###
```json
{
    "Artist Name": {
        "songs": {
            "spotify:track:id": {
                "name": "Song Name",
                "popularity": 65,
                "release_date": "2020",
                "id": "track_id"
            }
        },
        "artist_uri": "spotify:artist:id",
        "artist_id": "artist_id",
        "origin": {
            "city": "City Name",
            "country": "Country Name",
            "area": "Area Name",
            "status": "success"
        }
    }
}
```