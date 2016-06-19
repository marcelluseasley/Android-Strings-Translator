"""
Sample code for obtaining an OAuth token from Azure Data Market.
"""

import json
import urllib

import requests

class AdmOAuthClient(object):
    """
    Provides a client for obtaining an OAuth token from Azure Data Market access control service.
    """

    def __init__(self, client_id, client_secret):
        """
        :param client_id: Client ID.
        :param client_secret: Client secret.
        """

        self.client_id = client_id
        self.client_secret = client_secret

    def get_access_token(self):
        '''
        Generates and returns a new access token.
        '''

        datamarket_url = 'https://datamarket.accesscontrol.windows.net/v2/OAuth2-13'

        request_args = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'http://api.microsofttranslator.com',
            'grant_type': 'client_credentials'
        }

        response = requests.post(datamarket_url, data=urllib.urlencode(request_args))
        response.raise_for_status()
        data = json.loads(response.content)
        return data['access_token']
