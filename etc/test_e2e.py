import argparse
import itertools
import json
import sys
import os

from memory_profiler import profile


# cur = os.path.dirname(os.path.abspath(__file__))
import threading
import time
from datetime import datetime
from multiprocessing import Process

import requests

sys.path.append('auth_service_old')
sys.path.append('.')
sys.path.append('auth_service_old')
sys.path.append('./search_service')
sys.path.append('./scout_service')
sys.path.append('./common')


import pytest
import unittest
from qr_server.TokenManager import MockTokenManager, JwtTokenManager
from common.test_tools import ContextCreator, setUpDBTester


from AuthRepository import AuthRepository
from SearchRepository import SearchRepository
from auth_service_old import login, AuthServer, init_auth_server
from search_service import SearchServer, init_search_server
from scout_service import ScoutServer, init_scout_server
from manage_urls import *

TEST_CONFIG_PATH = 'common/'
USER_TEST_DATA_PATH = 'auth_service_old/test_data/'
LIBRARY_TEST_DATA_PATH = 'search_service/test_data/'
SCOUT_TEST_DATA_PATH = 'scout_service/test_data/'


def create_context(repository, token_man, json_data=None, params=None, headers=None, form=None, files=None, auth_id=None):
    ctx = ContextCreator()\
        .context(json_data, params, headers, form, files)\
        .with_token_manager(token_man, auth_id)\
        .with_repository(repository)\
        .build()
    return ctx


def run_server(server, host, port):
    server.run(host, port)


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



@pytest.mark.e2e
class TestDownloadBookE2E(unittest.TestCase):
    N_REPEAT = 1

    @classmethod
    def setUpClass(cls):
        config = setUpDBTester(cls, TEST_CONFIG_PATH, with_proc=True)

        cls.token_man = JwtTokenManager()
        cls.token_man.load_config(config['jwt'])

        cls.auth_server = AuthServer()
        init_auth_server(cls.auth_server, cls.token_man, config)
        cls.dbtest_man.fill_data_from_dir(cls.auth_server.db, USER_TEST_DATA_PATH)

        cls.search_server = SearchServer()
        init_search_server(cls.search_server, cls.token_man, config)
        cls.dbtest_man.fill_data_from_dir(cls.search_server.db, LIBRARY_TEST_DATA_PATH)

        cls.scout_server = ScoutServer()
        init_scout_server(cls.scout_server, cls.token_man, config)
        #cls.dbtest_man.fill_data(cls.scout_server.db.recent_viewed, SCOUT_TEST_DATA_PATH + 'recent_viewed.json')

        cls.auth_process = Process(target=run_server, args=(cls.auth_server, 'localhost', 9000))
        cls.search_process = Process(target=run_server, args=(cls.search_server, 'localhost', 9001))
        cls.scout_process = Process(target=run_server, args=(cls.scout_server, 'localhost', 9002))

        cls.auth_process.start()
        cls.search_process.start()
        cls.scout_process.start()

        auth_url = 'http://localhost:9000/'
        search_url = 'http://localhost:9001/'
        scout_url = 'http://localhost:9002/'
        cls.event_init = EventInitiator(auth_url, search_url, scout_url)

    @classmethod
    def tearDownClass(cls):
        cls.auth_process.terminate()
        cls.search_process.terminate()
        cls.scout_process.terminate()

        cls.auth_process.join()
        cls.search_process.join()
        cls.scout_process.join()

        del cls.auth_server.db
        del cls.search_server.db
        del cls.scout_server.db
        #time.sleep(5)
        cls.dbtest_man.exit_test_db()


    def _assert_main_results(self, res, origin):
        origin_cut = []
        for x in origin:
            origin_cut.append({'type': x['type'], 'id': x['id']})

        cmp = lambda x: str(x['id']) + x['type']
        res = sorted(res, key=cmp)
        origin_cut = sorted(origin_cut, key=cmp)
        self.assertEqual(res, origin_cut)

    def _form_result(self, book_ids=None, author_ids=None, series_ids=None):
        res = []
        for id in book_ids if book_ids else []:
            res.append({'type': 'book', 'id': id})
        for id in series_ids if series_ids else []:
            res.append({'type': 'series', 'id': id})
        for id in author_ids if author_ids else []:
            res.append({'type': 'author', 'id': id})
        return res

    def test_download_book(self):
        # todo connect to real DB with unknown entities set... change entity-sets to more common
        """used urls:
        login: POST http://localhost:9000/users/login
        account: GET http://localhost:9000/users (token)

        main: GET http://localhost:9001/library?offset=0&limit=100&find_book=true&find_series=true&find_author=true
        author: GET http://localhost:9001/authors/1
        series: GET http://localhost:9001/series/1
        book: GET http://localhost:9001/books/1

        events: POST http://localhost:9002/events (token)
        recent_viewed: GET http://localhost:9002/users/recent_viewed (token)
        """
        print(f'repeating test {self.N_REPEAT} times')
        for i in range(self.N_REPEAT):
            self.__download_book()

    def __download_book(self):
        # login
        token = self.event_init.login('user1', 'pass1')
        self.assertNotEqual(token, None)

        # request main page
        home_data = self.event_init.home_page()
        self.assertNotEqual(home_data, None)
        self.assertEqual(7, len(home_data))
        self._assert_main_results(self._form_result([1,2,3], [1,2], [1,2]), home_data)

        author = None
        for x in home_data:
            if (x['type'], x['id']) == ('author', 1):
                author = x
                break
        self.assertIsNotNone(author)
        author_id = 1

        # request author page
        author, author_linked = self.event_init.author_page(author_id)
        self.assertNotEqual(author, None)
        self.assertEqual((author['type'], author['id']), ('author', author_id))
        self.assertNotEqual(author_linked, None)
        self._assert_main_results(self._form_result([1, 2], [], [1]), author_linked)

        series = None
        for x in author_linked:
            if (x['type'], x['id']) == ('series', 1):
                series = x
                break
        self.assertIsNotNone(series)
        series_id = 1

        # request series page
        series, series_linked = self.event_init.series_page(series_id)
        self.assertNotEqual(series, None)
        self.assertEqual((series['type'], series['id']), ('series', series_id))
        self.assertNotEqual(series_linked, None)
        self._assert_main_results(self._form_result([1, 2], [], []), series_linked)

        book = None
        for x in series_linked:
            if (x['type'], x['id']) == ('book', 1):
                book = x
                break
        self.assertIsNotNone(book)
        book_id = 1

        # request book page
        book = self.event_init.book_page(book_id)
        self.assertNotEqual(book, None)
        self.assertEqual((book['type'], book['id']), ('book', book_id))

        # request account page
        user, recent_viewed = self.event_init.user_page()
        self.assertNotEqual(user, None)
        self.assertEqual((user['name'], user['email']), ('user1', 'user1@ya.ru'))
        self.assertNotEqual(recent_viewed, None)
        self._assert_main_results(self._form_result([1], [1], [1]), recent_viewed)


@profile
def main():
    if len(sys.argv) > 1:
        n_test = sys.argv[1]
        if n_test[:3] == '-n=':
            TestDownloadBookE2E.N_REPEAT = int(n_test[3:])
            del (sys.argv[1])

    unittest.main(module='test_e2e')


if __name__ == '__main__':
    main()


