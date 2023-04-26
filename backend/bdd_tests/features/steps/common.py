import json
from datetime import datetime
import requests


class EventInitiator:
    def __init__(self, auth_url, search_url, scout_url):
        self.auth_url = auth_url
        self.search_url = search_url
        self.scout_url = scout_url
        self.token = None

    def login(self, login, password):
        resp = requests.post(self.auth_url + 'users/login', json={'login': login, 'password': password})
        if resp.status_code != 200:
            return None
        resp = json.loads(resp.text)
        token = resp['access_token']
        if not isinstance(token, str):
            return None
        self.token = token
        return token

    def home_page(self):
        return self.__library_request('library', params={'find_book': True, 'find_series': True, 'find_author': True})

    def author_page(self, id):
        author = self.__library_request(f'authors/{id}')
        linked = self.__library_request(f'library', params={'offset':0, 'limit':100, 'author_id':id,
                                                           'find_book': True, 'find_series': True})
        self.register_event('view_author', {'author_id': id})
        return author, linked

    def series_page(self, id):
        series = self.__library_request(f'series/{id}')

        linked = self.__library_request(f'library', params={'offset': 0, 'limit': 100, 'series_id': id,
                                                        'find_book': True})
        self.register_event('view_series', {'series_id': id})
        return series, linked

    def book_page(self, id):
        self.register_event('view_book', {'book_id': id})
        return self.__library_request(f'books/{id}')

    def user_page(self):
        if not self.token:
            return None, None
        user = requests.get(self.auth_url + 'users', headers={'Authorization': 'Bearer ' + self.token})
        if user.status_code != 200:
            return None, None
        user = json.loads(user.text)

        recent = requests.get(self.scout_url + 'users/recent_viewed', headers={'Authorization': 'Bearer ' + self.token})
        if recent.status_code != 200:
            return user, None
        recent = json.loads(recent.text)
        return user, recent

    def __library_request(self, path, *args, **kwargs):
        resp = requests.get(self.search_url + path, *args, **kwargs)
        if resp.status_code != 200:
            return None
        resp = json.loads(resp.text)
        return resp

    def register_event(self, event, data):
        if not self.token:
            return None
        time = int(datetime.now().timestamp())
        print({'time': time, 'event': event, 'data': data})
        resp = requests.post(self.scout_url + 'events', json={'time': time, 'event': event, 'data': data},
                             headers={'Authorization': 'Bearer ' + self.token})
        if resp.status_code != 200:
            return False
        return True