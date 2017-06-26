import requests


class OAuth2AuthExchangeError(Exception):
    def __init__(self, description):
        self.description = description

    def __str__(self):
        return self.description


class InstagramOAuthAPI:

    oauth_base_url = 'https://api.instagram.com/oauth'

    def __init__(self, client_id, client_secret, redirect_uri=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def auth_url(self, scope=None, response_type='code'):
        """Build the authorization url."""
        data = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': response_type,
            'scope': ' '.join(scope or [])
        }
        url = '%s/authorize' % self.oauth_base_url
        req = requests.Request('GET', url, params=data)
        prepared = req.prepare()
        return prepared.url

    def exchange_code_for_access_token(self, code):
        """Send a request to obtain an access token."""
        data = {
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        req = requests.post('%s/access_token' % self.oauth_base_url, data=data)
        status = req.status_code
        result = req.json()
        if status != 200:
            raise OAuth2AuthExchangeError(result.get("error_message", ""))
        return result
