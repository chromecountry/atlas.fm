from flask import (
    Blueprint, redirect, request, session, render_template, send_file
)
from app.controllers.auth_controller import AuthController
from app.controllers.library_controller import LibraryController
from app.controllers.map_controller import MapController
from flask import current_app as app


from pathlib import Path
PROJECT_ROOT = Path(__file__).absolute().parents[1]
import sys; sys.path.append(str(PROJECT_ROOT))  # noqa

main = Blueprint('main', __name__)
auth_controller = AuthController()


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
