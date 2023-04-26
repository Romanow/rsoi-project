import pandas as pd
import qrookDB.DB as db
import numpy as np
import pickle
import os

# todo books_count not set here for series - watch for stuff.sql file for update request

BOOK_ID_FILE = 'book_ids.pickle'

DB = db.DB('postgres', 'qrook_db_new', 'kurush', 'pondoxo', format='dict')
DB.create_data(__name__, in_module=True)

def insert_authors():
    df_authors = pd.read_csv('authors.csv')
    df_authors = df_authors.drop(['Unnamed: 0'], axis=1)
    df_authors = df_authors.replace({np.nan: None})
    data = [list(d.values()) for d in df_authors.to_dict(orient='records')]

    DB.insert(DB.authors, DB.authors.name, DB.authors.country,
              DB.authors.birthdate, DB.authors.photo, DB.authors.description, auto_commit=True)\
        .values(data).exec()

def clean_series_title(t):
    if t[0].islower() and t[1] == ' ':
        t = t[1:].strip()
    return t

def insert_series():
    df_authors = pd.read_csv('series.csv')
    df_authors = df_authors.drop(['Unnamed: 0'], axis=1)
    df_authors = df_authors.replace({np.nan: None})
    df_authors['title'] = df_authors['title'].map(clean_series_title)
    data = [list(d.values()) for d in df_authors.to_dict(orient='records')]

    DB.insert(DB.series, DB.series.description, DB.series.title,
              DB.series.skin_image, auto_commit=True)\
        .values(data).exec()


temps, x = [], 'а'
while x <= 'я':
    temps += [x+'.']
    temps += [x+' ']
    x = chr(ord(x)+1)
temps += ['ё.']
temps += ['ё ']
x = 'a'
while x <= 'z':
    temps += [x+'.']
    x = chr(ord(x)+1)

for i in range(10):
    temps.append(str(i) + '.')
    temps.append(str(i) + ' ')
    for j in range(10):
        temps.append(str(i) + str(j) + '.')
        temps.append(str(i) + str(j) + ' ')

ends = ['.zip', '.fb2'] # hardcode
def clean_books_title(t):
    for x in temps:
        if t.startswith(x):
            if t.find('31 июня') != -1: continue  # some hardcode
            t = t[t.find(' '):].strip()
            break
    for e in ends:
        if t.endswith(e):
            t = t[:t.rfind(e)]
    return t

def get_book_format(title):
    return title[title.rfind('.'):][1:]


def insert_books():
    df_entities = pd.read_csv('entity_relations.csv', index_col=0)
    df_books = pd.read_csv('books.csv', index_col=0)

    df_entities['title'] = df_entities['book']
    df = df_books.join(df_entities.set_index('title'), on='title')
    df = df.replace({np.nan: None})
    df['title'] = df['title'].map(clean_books_title)

    # books
    all_data = df.to_dict(orient='records')
    i = 0
    while i < len(all_data):
        if all_data[i]['book'] is None: # not found record in entity_relations
            all_data.pop(i)
            i -= 1
        else:
            all_data[i]['file_type'] = get_book_format(all_data[i]['book'])
        i += 1

    books_data = [[d['title'], d['skin_image'], d['description'], '{%s}' % d['genre']] for d in all_data]
    book_ids = DB.insert(DB.books, DB.books.title, DB.books.skin_image,
              DB.books.description, DB.books.genres)\
        .values(books_data).returning(DB.books.id).all()
    for i in range(len(all_data)):
        all_data[i]['book_id'] = book_ids[i]['id']

    # publications
    publication_ids = []
    for book in all_data:
        id = DB.insert(DB.publications, DB.publications.book_id, DB.publications.language_code)\
            .values([[book['book_id'], 'ru']]).returning(DB.books.id).one()
        publication_ids.append(id['id'])
    for i in range(len(all_data)):
        all_data[i]['publication_id'] = publication_ids[i]

    # book_files
    bf_data = [[d['publication_id'], d['path'], d['file_type']] for d in all_data]
    bf_ids = DB.insert(DB.book_files, DB.book_files.publication_id, DB.book_files.file_path,
              DB.book_files.file_type)\
        .values(bf_data).returning(DB.book_files.publication_id).all()

    # book_authors
    for book in all_data:
        author = book['author']
        author_id = DB.select(DB.authors, DB.authors.id).where(name=author).one()
        ok = DB.insert(DB.books_authors, DB.books_authors.book_id, DB.books_authors.author_id)\
            .values([[book['book_id'], author_id['id']]]).exec()
        if not ok:
            print('ALARM!!!! NOT OK')

    # book series
    for book in all_data:
        series = book['series']
        if series is None:
            continue
        series = clean_series_title(series)
        series_id = DB.select(DB.series, DB.series.id).where(title=series).one()
        ok = DB.insert(DB.books_series, DB.books_series.book_id, DB.books_series.series_id,
                       DB.books_series.book_number)\
            .values([[book['book_id'], series_id['id'], book['book_number']]]).exec()
        if not ok:
            print('ALARM!!!! NOT OK')

    DB.commit()
    return

if __name__ == '__main__':
    #insert_authors()
    # insert_series()
    #insert_books()
    pass