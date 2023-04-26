import sys
sys.path.append("..")
sys.path.append("../common")

import itertools
import os

from common.jwt_validator import with_jwt_token_raw

sys.path.append("..")
sys.path.append("../common")
import random

from search.SearchRepository import *
from search.Filters import *
from search.dtos import *

from qr_server.Server import MethodResult, QRContext
from qr_server.Config import QRYamlConfig
from qr_server.TokenManager import require_token, JwtTokenManager
from qr_server.FlaskServer import FlaskServer

from common.common_api import health
from common.jwt_validator import JWTTokenValidator, require_role, with_jwt_token, TokenUser
from common.kafka_manager import KafkaProducer


def shuffle_sorted(arr, get):
    n = len(arr)
    i = 0
    while i < n - 1:
        s = i
        j = i + 1
        while get(arr[j]) == get(arr[j - 1]):
            j += 1
            if j == n: break
        e = j
        copy = arr[s:e]
        random.shuffle(copy)
        i = j
        arr[s:e] = copy

@with_jwt_token(extract_user=True, full_user=True)
def main(ctx: QRContext, user: TokenUser):
    offset = ctx.params.get('offset')
    limit = ctx.params.get('limit')
    filters = dict(ctx.params)

    offset = int(offset) if offset else 0
    limit = int(limit) if limit else 'all'

    bf = book_filter(filters)
    bf_skip0, magic_flag = bf['skip'], False

    for k in 'language format genres'.split(' '):
        if k in bf:
            bf['skip'] = False
            magic_flag = True
            if bf.get('search') and bf_skip0:
                bf.pop('search')

    cnt = int(not bf_skip0)
    if filters.get('find_author'): cnt += 1
    if filters.get('find_series'): cnt += 1
    if cnt == 0:
        return MethodResult([])

    local_limit = 1000

    books = ctx.repository.get_filtered_books(bf, 0, local_limit)
    book_ids = [b['id'] for b in books]

    af = author_filter(filters, book_ids if magic_flag else None)
    authors = ctx.repository.get_filtered_authors(af, 0, local_limit)

    sf = series_filter(filters, book_ids if magic_flag else None)
    series = ctx.repository.get_filtered_series(sf, 0, local_limit)

    if bf_skip0 == True:
        books = []
    data = list(itertools.chain.from_iterable([authors, series, books]))

    sort_filter = filters.get('sort')
    if not sort_filter:
        if limit == 'all':
            data = data[offset:]
        else:
            data = data[offset:offset+limit]

        return MethodResult(SearchMainDTO(data))

    # todo more beautiful sort
    reverse = sort_filter in ['name_desc', 'date_desc']
    if sort_filter.find('date') != -1:
        func = lambda x: x.get('updated_at')
    elif sort_filter.find('name') != -1:
        func = lambda x: x.get('title') if x.get('title') else x.get('name')
    elif sort_filter == 'series_order':
        func = lambda x: x.get('book_number')
    else:
        func = None
    data.sort(key=func, reverse=reverse)

    # todo probably useless
    shuffle_sorted(data, func)

    data = data[offset:offset + limit]

    # note: слишком много однотипных записей в scout_db - аж фу
    #ctx.managers['kafka_producer'].produce_dict('using_filters', {'filters': filters, 'user_login': user.login})
    if filters.get('search'):
        ctx.managers['kafka_producer'].produce_dict('searching', {'search': filters['search'], 'user_login': user.login})
    return MethodResult(SearchMainDTO(data))


@with_jwt_token(extract_user=True, full_user=True)
def author(ctx: QRContext, id, user: TokenUser):
    id = int(id)
    data = ctx.repository.get_full_author(id)
    if data is None:
        return MethodResult('author not found', 500)

    ctx.managers['kafka_producer'].produce_dict('view_author', {'author_id': id, 'user_login': user.login})
    return MethodResult(AuthorFullDTO(**data))


@with_jwt_token(extract_user=True, full_user=True)
def series(ctx: QRContext, id, user: TokenUser):
    id = int(id)
    data = ctx.repository.get_full_series(id)
    if data is None:
        return MethodResult('series not found', 500)

    ctx.managers['kafka_producer'].produce_dict('view_series', {'series_id': id, 'user_login': user.login})
    return MethodResult(SeriesFullDTO(**data))


@with_jwt_token(extract_user=True, full_user=True)
def book(ctx: QRContext, id, user: TokenUser):
    id = int(id)
    data = ctx.repository.get_full_book(id)
    if data is None:
        return MethodResult('book not found', 500)

    ctx.managers['kafka_producer'].produce_dict('view_book', {'book_id': id, 'user_login': user.login})
    return MethodResult(BookFullDTO(**data))

@with_jwt_token(extract_user=True)
def get_entities(ctx: QRContext, user: TokenUser):
    book_ids = ctx.json_data.get('book_ids')
    series_ids = ctx.json_data.get('series_ids')
    author_ids = ctx.json_data.get('author_ids')

    data = ctx.repository.get_entities(author_ids, book_ids, series_ids)
    if data is None:
        return MethodResult('data not found', 500)
    return MethodResult(EntitiesListDTO(data))

class SearchServer(FlaskServer, SearchRepository):
    """DI class🐕"""



def init_search_server(server, token_man, kafka_producer, config):
    server.init_server(config['app'])
    if config['app']['logging']:
        server.configure_logger(config['app']['logging'])
        kafka_producer.logger = server.logger
    server.register_manager(token_man)
    server.register_manager(kafka_producer)
    server.connect_repository(config['database'])

    server.register_method('/library', main, 'GET')
    server.register_method('/authors/<id>', author, 'GET')
    server.register_method('/series/<id>', series, 'GET')
    server.register_method('/books/<id>', book, 'GET')
    server.register_method('/entities', get_entities, 'GET')

    server.register_method('/manage/health', health, 'GET')


if __name__ == "__main__":
    config = QRYamlConfig()
    config.read_config('config.yaml', )

    host = config['app']['host']    # load default value
    port = config['app']['port']

    host_env = os.environ.get('HOST_NAME')
    if host_env is not None:
        host = host_env

    jwt = config['jwt']
    token_man = JWTTokenValidator(jwks_uri=jwt.jwks_uri, issuer=jwt.iss, audience=jwt.aud)
    kafka_producer = KafkaProducer(config=config.kafka_producer.data)

    server = SearchServer()
    init_search_server(server, token_man, kafka_producer, config)
    server.run(host, port)
