from kinde_sdk.kinde_api_client import GrantType

LOCALHOST = "127.0.0.1"

SITE_HOST = f"{LOCALHOST}"
SITE_PORT = "5000"
SITE_URL = f"http://{SITE_HOST}:{SITE_PORT}"
GRANT_TYPE = GrantType.AUTHORIZATION_CODE_WITH_PKCE
CODE_VERIFIER = "joasd923nsad09823noaguesr9u3qtewrnaio90eutgersgdsfg"  # A suitably long string > 43 chars
TEMPLATES_AUTO_RELOAD = True
SESSION_TYPE = "filesystem"
SESSION_PERMANENT = False
SECRET_KEY = "joasd923nsad09823noaguesr9u3qtewrnaio90eutgersgdsfgs"  # Secret used for session management

KINDE_ISSUER_URL = "https://selectionguide.kinde.com"
KINDE_CALLBACK_URL = f"http://{LOCALHOST}:5000/callback"
LOGOUT_REDIRECT_URL = f"http://{LOCALHOST}:5000"
CLIENT_ID = "7cda8ea4b82a40998f24e33395548613"
CLIENT_SECRET = "1bIIXU1X4TelLA12oBBPWOmX0Lo6dcwt7iu802e7hgC50JEFE4TW"
