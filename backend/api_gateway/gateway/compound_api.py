from datetime import datetime

from qr_server.Server import MethodResult, QRContext

from .circuit_breaker import circuitBreaker, ServiceUnavailableException
from .dtos import *
from .utils import *


# /api/v1/reservations
from common.job_queue import TASK_QUEUE
from common.jwt_validator import with_jwt_token, TokenUser, require_role

def home(ctx: QRContext):
    txt = '''<!DOCTYPE html>
    <html>
    <body>
    This is QROOK API v3.0
    </body>
    </html>'''
    return MethodResult(txt, raw_data=True)


@with_jwt_token(extract_user=True, full_user=True)
@require_role(['user', 'admin'])
def user_info(ctx: QRContext, user: TokenUser):
    return MethodResult(UserInfoDTO(user.name, user.surname, user.email, user.login, user.avatar))


@circuitBreaker.circuit([Service.SCOUT, Service.SEARCH], MethodResult(f'{SERVICE_NAMES[Service.SCOUT]} service unavailable', 503))
@with_jwt_token(extract_user=True, full_user=True)
@require_role(['user', 'admin'])
def get_recent_viewed(ctx: QRContext, user: TokenUser):
    scout_address = ctx.meta['services'][Service.SCOUT]
    search_address = ctx.meta['services'][Service.SEARCH]

    # get ids
    resp = send_request(scout_address, f'users/recent_viewed',
                        request=QRRequest(params=ctx.params, json_data=[], headers=ctx.headers))
    if resp.status_code != 200:
        raise ServiceUnavailableException(Service.SCOUT)
    entities = resp.get_json()

    entity_ids = {
        'author_ids': [x['id'] for x in entities if x['entity_type'] == 'author'],
        'book_ids': [x['id'] for x in entities if x['entity_type'] == 'book'],
        'series_ids': [x['id'] for x in entities if x['entity_type'] == 'series'],
    }

    # get data
    resp = send_request(search_address, f'entities',
                        request=QRRequest(params=[], json_data=entity_ids, headers=ctx.headers))
    if resp.status_code != 200:
        raise ServiceUnavailableException(Service.SEARCH)

    data = resp.get_json()  # todo почему сюда пришла структура DTO...

    result = []  # ради того, чтобы упорядочить в том порядке, что был в entities
    for entity in entities:
        for d in data:
            if d['id'] == entity['id'] and d['type'] == entity['entity_type']:
                result.append(d)
                break

    return MethodResult(RecentViewedDTO(result))




@circuitBreaker.circuit([Service.SCOUT, Service.SEARCH], MethodResult(f'{SERVICE_NAMES[Service.SCOUT]} service unavailable', 503))
@with_jwt_token(extract_user=True)
@require_role(['admin'])
def get_report_data(ctx: QRContext, user: TokenUser):
    # {'time_start': time_start, 'time_end': time_end}
    scout_address = ctx.meta['services'][Service.SCOUT]
    search_address = ctx.meta['services'][Service.SEARCH]

    # get events in interval
    resp = send_request(scout_address, f'events',
                        request=QRRequest(params=ctx.params, json_data=[], headers=ctx.headers))
    if resp.status_code != 200:
        raise ServiceUnavailableException(Service.SCOUT)
    events = resp.get_json()

    # prepare stats
    def inc_or_default(d, key, default=0):
        if d.get(key) is None:
            d[key] = default
        d[key] += 1
    def most_freq(d, default=None):
        best_key, best_cnt = None, 0
        for k, v in d.items():
            if v > best_cnt:
                best_key, best_cnt = k, v
        return best_key

    views = {'books': dict(), 'authors': dict(), 'series': dict()}
    downloads = 0
    search = dict()

    for e in events:
        t, d = e['event'], e['data']
        if t.startswith('view_'):
            if t == 'view_book':
                inc_or_default(views['books'], d['book_id'])
            elif t == 'view_author':
                inc_or_default(views['authors'], d['author_id'])
            elif t == 'view_series':
                inc_or_default(views['series'], d['series_id'])
        elif t == 'download_book':
            downloads += 1
        elif t == 'searching':
            inc_or_default(search, d['search'])

    view_books = sum(views['books'].values())
    view_authors = sum(views['authors'].values())
    view_series = sum(views['series'].values())

    freq_book = most_freq(views['books'])
    freq_author = most_freq(views['authors'])
    freq_series = most_freq(views['series'])
    entity_ids = {
        'author_ids': [freq_author] if freq_author is not None else [],
        'book_ids':  [freq_book] if freq_book is not None else [],
        'series_ids': [freq_series] if freq_series is not None else [],
    }
    resp = send_request(search_address, f'entities',
                        request=QRRequest(params=[], json_data=entity_ids, headers=ctx.headers))
    if resp.status_code != 200:
        raise ServiceUnavailableException(Service.SEARCH)

    freq_entities = resp.get_json()  # todo почему сюда пришла структура DTO...

    report = dict(
        views_cnt={
            'total': view_books+view_authors+view_series,
            'books': view_books,
            'authors': view_authors,
            'series': view_series,
        },
        downloads_cnt=downloads,
        search_cnt=sum(search.values()),
        most_frequent_search=most_freq(search, default=''),
        most_frequent_entities=freq_entities,
    )

    return MethodResult(ReportDTO(**report))