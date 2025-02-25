from flask import redirect, session, request
from spotipy.oauth2 import SpotifyOAuth
from credentials import Spotipy as SpotipyCredentials


class AuthController:
    def __init__(self):
        self.oauth = SpotifyOAuth(
            client_id=SpotipyCredentials.SPOTIPY_CLIENT_ID,
            client_secret=SpotipyCredentials.SPOTIPY_CLIENT_SECRET,
            redirect_uri=SpotipyCredentials.SPOTIPY_REDIRECT_URI,
            scope=SpotipyCredentials.SCOPE
        )

    def check_auth(self):
        return session.get('token_info') is not None

    def handle_login(self):
        auth_url = self.oauth.get_authorize_url()
        return redirect(auth_url)

    def handle_callback(self, code=None, error=None):
        if error:
            return f"Error: {error}"
        if not code:
            return 'No code provided'

        try:
            token_info = self.oauth.get_access_token(code)
            session['token_info'] = token_info
            return redirect('/map')
        except Exception as e:
            return f"Error getting token: {e}"

    def handle_logout(self):
        session.clear()
        return redirect('/')
