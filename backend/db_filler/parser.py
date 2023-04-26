import os
import pandas as pd
import time
import numpy as np
import requests

pd.set_option('display.max_rows', 40)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

import wiki_author_loader as author_wiki
import wiki_series_loader as series_wiki
import wiki_books_loader as books_wiki


books_path = '/home/kurush/Documents/qrook/backend/file_service/books'

level_mapping = {
    0: 'genre',
    1: 'author',
    2: 'series',
    3: 'book'
}


def merge(x, y):
    if x is None:
        return y.copy()
    z = x.copy()
    z.update(y)
    return z


def walk_books(path):
    storage = []
    def recursive(path, level=0, data=None):
        x = os.listdir(path)
        x.sort()
        for i, d in enumerate(x):
            cur = os.path.join(path, d)
            if os.path.isdir(cur):
                cur_data = merge(data, {level_mapping[level]: d})
                recursive(cur, level+1, cur_data)
            else:
                short_path = cur[cur.find('books') + 6:]
                cur_data = merge(data, {'book': d, 'path': short_path, 'book_number': i+1})
                storage.append(cur_data)

    recursive(path)
    return storage


def read_files():
    data = walk_books(books_path)
    df = pd.DataFrame(data)
    df.to_csv('entity_relations.csv')
    print(df)

def make_authors():
    print('loading authors info...')
    df = pd.read_csv('entity_relations.csv')
    author_names = df['author'].unique()

    authors = []
    n = len(author_names)
    for i, name in enumerate(author_names):
        try:
            if str(name) == 'nan': continue
            a_data = author_wiki.parse_author(name)
            authors.append(a_data)
            if i % 10 == 0:
                print('%d of %d' % (i, n))
        except Exception as e:
            print('ERROR: ', e)
            continue

    df_authors = pd.DataFrame(authors)
    df_authors.to_csv('authors.csv', mode='a')
    print(df_authors)

def make_series():
    print('loading series info...')
    df = pd.read_csv('entity_relations.csv')
    series_titles = df['series'].unique()

    series = []
    n = len(series_titles)
    for i, name in enumerate(series_titles):
        try:
            if str(name) == 'nan': continue
            a_data = series_wiki.parse_series(name)
            series.append(a_data)
            if i % 10 == 0:
                print('%d of %d' % (i, n))
        except Exception as e:
            print('ERROR: ', e)
            continue

    df_authors = pd.DataFrame(series)
    df_authors.to_csv('series.csv', mode='a')
    print(df_authors)

def make_books():
    print('loading books info...')
    df = pd.read_csv('entity_relations.csv')
    book_titles = df['book'].unique()
    for i, b in enumerate(book_titles):
        print(i, b)

    books = []
    n = len(book_titles)
    offset = 919
    for i, name in enumerate(book_titles[offset:]):
        try:
            if str(name) == 'nan': continue
            a_data = books_wiki.parse_book(name)
            books.append(a_data)
            if i % 10 == 0:
                print('%d (%d) of %d' % (offset+i, i, n))
            if i and i % 10 == 0:
                df_books = pd.DataFrame(books)
                df_books.to_csv('books_tmp.csv')
                print(df_books.info())
        except Exception as e:
            print('ERROR: ', e)
            books.append({'name': name})
            continue

    df_authors = pd.DataFrame(books)
    df_authors.to_csv('books.csv', mode='a')
    print(df_authors)



def reorder_books():
    df_books = pd.read_csv('books_tmp_tmp.csv', index_col=0)

    df_books = df_books.replace({np.nan: None})
    data = df_books.to_dict(orient='records')
    new_data = []
    for d in data:
        new_d = {'title': None, 'skin_image': None, 'description': None}
        for x in [d['title'], d['skin_image'], d['description']]:
            if x in ['', '\n']: x = None
            if x is not None and x.startswith('upload'):
                new_d['skin_image'] = x
            elif x is not None:
                if new_d['title'] is None:
                    new_d['title'] = x
                elif len(new_d['title']) > len(x):
                    new_d['description'] = new_d['title']
                    new_d['title'] = x
                else:
                    new_d['description'] = x
        if new_d['title'] is None or new_d['title'] in ['', '\n']:
            print('ALARM!!!')
        new_data.append(new_d)
    df = pd.DataFrame(new_data)
    df.to_csv('new_books.csv')
    print(df.info())
    return

# todo not used, not tested
def load_author_photos():
    df = pd.read_csv('entity_relations.csv')
    photos = df[df['photo'].notnull()]['photo']

    i = 0
    from os.path import basename
    for photo in photos:
        with open('a', "wb") as f:
            f.write(requests.get(photo).content)

if __name__ == '__main__':
    read_files()
    # make_authors()
    # make_series()
    # make_books()
    # reorder_books()