from flask import (
    Blueprint, redirect, request, session, render_template, send_file
)
from spotipy.oauth2 import SpotifyOAuth
from credentials import Spotipy as SpotipyCredentials
from app.controllers.library_controller import LibraryController
from app.controllers.map_controller import MapController
from flask import current_app as app


from pathlib import Path
PROJECT_ROOT = Path(__file__).absolute().parents[1]
import sys; sys.path.append(str(PROJECT_ROOT))  # noqa

main = Blueprint('main', __name__)


@main.route('/')
def index():
    if not session.get('token_info'):
        return render_template('login.html')
    return redirect('/map')


@main.route('/login')
def login():
    sp_oauth = SpotifyOAuth(
        client_id=SpotipyCredentials.SPOTIPY_CLIENT_ID,
        client_secret=SpotipyCredentials.SPOTIPY_CLIENT_SECRET,
        redirect_uri='http://localhost:5000/callback',
        scope=SpotipyCredentials.SCOPE,
        cache_handler=None
    )
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@main.route('/callback')
def callback():
    if 'error' in request.args:
        return f"Error: {request.args['error']}"
    if 'code' not in request.args:
        return 'No code provided'

    sp_oauth = SpotifyOAuth(
        client_id=SpotipyCredentials.SPOTIPY_CLIENT_ID,
        client_secret=SpotipyCredentials.SPOTIPY_CLIENT_SECRET,
        redirect_uri='http://localhost:5000/callback',
        scope=SpotipyCredentials.SCOPE
    )
    session['token_info'] = sp_oauth.get_access_token(request.args['code'])
    return redirect('/map')


@main.route('/map')
def map_page():
    if not session.get('token_info'):
        return redirect('/login')
    return render_template('loading.html')


# todo: clean up
@main.route('/generate')
def generate_map():
    if not session.get('token_info'):
        return redirect('/login')

    library_controller = LibraryController(
        spotify_token=session['token_info']['access_token'],
        library_cache_path=app.config['LIBRARY_CACHE_PATH'],
        mb_cache_path=app.config['MB_CACHE_PATH']
    )

    map_controller = MapController(
        library_controller=library_controller,
        assets_path=app.config['STATIC_DIR'],
        output_path=app.config['MAP_OUTPUT_PATH'],
        geocode_cache_path=app.config['GEOCODE_CACHE_PATH']
    )

    try:
        map_path = map_controller.generate_map()
        return send_file(map_path)
    except Exception as e:
        print(f"Error generating map: {e}")
        return redirect('/')


@main.route('/logout')
def logout():
    session.clear()
    return redirect('/')
