from qr_server.dict_parsing import *

def if_skip(s):
    return s in [False, 'false', 'f', None]

def book_filter(filters: dict):
    g = filters.get('genres')
    if g:
        g = g.split(';')
        g = [x.strip().title() for x in g]
    res = {
        'search': filters.get('search'),
        'skip': if_skip(filters.get('find_book')),
        'book_id': filters.get('book_id'),
        'author_id': filters.get('author_id'),
        'series_id': filters.get('series_id'),
        'language': filters.get('language'),
        'format': filters.get('format'),
        'genres': g,
        'sort': filters.get('sort'),
    }
    res = drop_none(res)
    if len(res) == 0:
        res['skip'] = True
    return res


def author_filter(filters: dict, filtered_books):
    res = {
        'search': filters.get('search'),
        'skip': if_skip(filters.get('find_author')),
        'author_id': filters.get('author_id'),
        'filtered_books': filtered_books,
        'sort': filters.get('sort'),
    }
    res = drop_none(res)
    if len(res) == 0:
        res['skip'] = True
    return res


def series_filter(filters: dict, filtered_books, book_match='any'):
    res = {
        'search': filters.get('search'),
        'skip': if_skip(filters.get('find_series')),
        'series_id': filters.get('series_id'),
        'author_id': filters.get('author_id'),
        'filtered_books': filtered_books,
        'book_match': book_match,
        'sort': filters.get('sort'),
    }
    res = drop_none(res)
    if len(res) == 0:
        res['skip'] = True
    return res
