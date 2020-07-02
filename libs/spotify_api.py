import os
import base64
import oauthlib
import requests
from datetime import datetime
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth


'''
The following urls are Spotify API.
For more information please visit documantation page:
https://beta.developer.spotify.com/console
'''
TOKEN_URL = 'https://accounts.spotify.com/api/token'
TRACK_URL = 'https://api.spotify.com/v1/tracks/{id}'
ALBUM_URL = 'https://api.spotify.com/v1/albums/{id}'
ARTIST_URL = 'https://api.spotify.com/v1/artists/{id}'
SEARCH_URL = 'https://api.spotify.com/v1/search'


class SpotifyClient:
    ''' Spotify Client.

    Register your application first on spotify
    and get spotify client_id and client_secret.
    
    Spotify developer site: 
    https://beta.developer.spotify.com/dashboard
    '''
    def __init__(self, client_id, client_secret):
        ''' Spotify Client Constructor.

        Provide your spotify client_id and client_secret
        this is used to able accessing spotify protected api.

        For more information read:
        https://developer.spotify.com/web-api
        '''
        self.client_id = client_id
        self.client_secret = client_secret


    def authenticate(self):
        ''' OAuth2 Authentication.

        Execute this function after class initialization
        the authentication is used to get access_token which
        is required to use Spotify API.

        For more information read:
        https://developer.spotify.com/web-api/authorization-guide
        '''
        auth = HTTPBasicAuth(self.client_id, self.client_secret)
        client = BackendApplicationClient(self.client_id)
        session = OAuth2Session(client=client)
        session.fetch_token(TOKEN_URL, auth=auth)
        self.client = session

   
    def get_track(self, track_id):
        ''' Get track information by id.

        For more information read:
        https://developer.spotify.com/web-api/get-track
        '''
        url = TRACK_URL.format(id=track_id)
        track = self.client.get(url).json()
        return track

    def get_album(self, album_id):    
        ''' Get album information by id.

        For more information read:
        https://developer.spotify.com/web-api/get-album
        '''
        url = ALBUM_URL.format(id=album_id)
        album = self.client.get(url).json()
        return album


    def get_artist(self, artist_id):
        ''' Get album information by id.

        For more information read:
        https://developer.spotify.com/web-api/get-artist
        '''
        url = ARTIST_URL.format(id=artist_id)
        artist = self.client.get(url).json()
        return artist


    def search_track(self, query, limit = 50, offset = 0):
        ''' Search track by query.

        For more information read:
        https://developer.spotify.com/web-api/search-item
        '''
        query = {
            'q': query,
            'type': 'track',
            'limit': limit,
            'offset': offset
        }

        return SearchIterator(self.client, SEARCH_URL, query)


    def download_audio(self, preview_url, name, target_path):
        ''' Download audio preview.

        This function is used to download file from
        preview_url on track. The file is saved in targe path
        with mp3 extension. 
        
        For more information read:
        https://developer.spotify.com/web-api/get-track
        '''
        response = self.client.get(preview_url)
        name = name + '.mp3'
        file_path = os.path.join(target_path, name)

        with open(file_path, 'wb') as f:
            f.write(response.content)

        return file_path


 
class SearchIterator:
    ''' Iterator for search result.

    To manage reponse data with big size
    this method to provide iteration of pages
    by defined offset and limit.
    '''
    def __init__(self, client, url, query):
        self.client = client
        self.url = url
        self.query = query
        self.next_url = url
        self.is_first = True


    def __iter__(self):
        return self


    def __next__(self):
        ''' Move forward iterator.  

        The iterator is moving following 
        the next pages, the iteration is finish 
        if the next page is not available.
        '''
        if self.is_first:
            result = self.client.get(SEARCH_URL, params=self.query)
            result = result.json()
            self.next_url = result['tracks']['next']
            self.is_first = False
            return result

        if self.next_url == None:
            raise StopIteration()

        try:
            result = self.client.get(self.next_url)
            result = result.json()
            self.next_url = result['tracks']['next']
        except:
            return result

        return result