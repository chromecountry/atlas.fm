from flask import (
    Blueprint, redirect, request, session, render_template
)
from app.controllers.auth_controller import AuthController
from app.controllers.library_controller import LibraryController
from app.controllers.map_controller import MapController
from flask import g, current_app as app


from pathlib import Path
PROJECT_ROOT = Path(__file__).absolute().parents[1]
import sys; sys.path.append(str(PROJECT_ROOT))  # noqa

main = Blueprint('main', __name__)

auth_controller = AuthController()


def get_map_controller():
    if 'map_controller' not in g:
        library_controller = LibraryController(
            spotify_token=session['token_info']['access_token'],
            library_cache_path=app.config['LIBRARY_CACHE_PATH'],
            mb_cache_path=app.config['MB_CACHE_PATH']
        )

        g.map_controller = MapController(
            library_controller=library_controller,
            assets_path=app.config['STATIC_DIR'],
            output_path=app.config['MAP_OUTPUT_PATH'],
            geocode_cache_path=app.config['GEOCODE_CACHE_PATH']
        )

    return g.map_controller


@main.teardown_app_request
def teardown_controllers(exception):
    g.pop('map_controller', None)


@main.route('/')
def index():
    if not auth_controller.check_auth():
        return render_template('login.html')
    return redirect('/map')


@main.route('/login')
def login():
    return auth_controller.handle_login()


@main.route('/callback')
def callback():
    return auth_controller.handle_callback(
        code=request.args.get('code'),
        error=request.args.get('error')
    )


@main.route('/logout')
def logout():
    return auth_controller.handle_logout()


@main.route('/map')
def map_page():
    return get_map_controller().show_map_page()


@main.route('/generate')
def generate_map():
    return get_map_controller().generate_map()
