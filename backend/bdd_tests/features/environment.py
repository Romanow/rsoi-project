import argparse
import itertools
import json
import sys
import os

# cur = os.path.dirname(os.path.abspath(__file__))
import threading
import time
from datetime import datetime
from multiprocessing import Process

import requests
from behave import fixture
from behave import *

sys.path.append('../../auth_service_old')
sys.path.append('../../search_service')
sys.path.append('../../scout_service')
sys.path.append('../../common')


import pytest
import unittest
from qr_server.TokenManager import MockTokenManager, JwtTokenManager
from test_tools import ContextCreator, setUpDBTester

from AuthRepository import AuthRepository
from SearchRepository import SearchRepository
from auth_service import login, AuthServer, init_auth_server
from search_service import SearchServer, init_search_server
from scout_service import ScoutServer, init_scout_server
from manage_urls import *

use_step_matcher("re")


TEST_CONFIG_PATH = '../../common/'
USER_TEST_DATA_PATH = '../../auth_service_old/test_data/'
LIBRARY_TEST_DATA_PATH = '../../search_service/test_data/'
SCOUT_TEST_DATA_PATH = '../../scout_service/test_data/'

def run_server(server, host, port):
    server.run(host, port)

@fixture
def fix_run_server(context):
    # -- SETUP-FIXTURE PART:
    config = setUpDBTester(context, TEST_CONFIG_PATH, with_proc=True)

    context.token_man = JwtTokenManager()
    context.token_man.load_config(config['jwt'])

    context.auth_server = AuthServer()
    init_auth_server(context.auth_server, context.token_man, config)
    context.dbtest_man.fill_data_from_dir(context.auth_server.db, USER_TEST_DATA_PATH)

    context.search_server = SearchServer()
    init_search_server(context.search_server, context.token_man, config)
    context.dbtest_man.fill_data_from_dir(context.search_server.db, LIBRARY_TEST_DATA_PATH)

    context.scout_server = ScoutServer()
    init_scout_server(context.scout_server, context.token_man, config)
    # cls.dbtest_man.fill_data(cls.scout_server.db.recent_viewed, SCOUT_TEST_DATA_PATH + 'recent_viewed.json')

    context.auth_process = Process(target=run_server, args=(context.auth_server, 'localhost', 9000))
    context.search_process = Process(target=run_server, args=(context.search_server, 'localhost', 9001))
    context.scout_process = Process(target=run_server, args=(context.scout_server, 'localhost', 9002))

    context.auth_process.start()
    context.search_process.start()
    context.scout_process.start()

    yield context

    # -- CLEANUP-FIXTURE PART:
    context.auth_process.terminate()
    context.search_process.terminate()
    context.scout_process.terminate()

    context.auth_process.join()
    context.search_process.join()
    context.scout_process.join()

    del context.auth_server.db
    del context.search_server.db
    del context.scout_server.db
    #todo time.sleep(5)
    context.dbtest_man.exit_test_db()

def before_tag(context, tag):
    if tag == "fixture.running.server":
        use_fixture(fix_run_server, context)