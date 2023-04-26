from itertools import chain
from typing import List

import qr_server.Repository as rep
from qr_server.Config import IQRConfig
from ast import literal_eval
from qrookDB.data import QRTable
from qr_server.dict_parsing import *
from abc import abstractmethod

books, authors, books_authors, series, books_series, publications, book_files = [QRTable()] * 7
op = None


class ISearchRepository:
    @abstractmethod
    def get_full_author(self, id):
        """get author info by id"""
    @abstractmethod
    def get_full_series(self, id):
        """get series info by id"""
    @abstractmethod
    def get_full_book(self, id):
        """get book info by id"""
    @abstractmethod
    def get_filtered_books(self, filters: dict, offset=0, limit=100):
        """get books previews using filters"""
    @abstractmethod
    def get_filtered_authors(self, filters: dict, offset=0, limit=100):
        """get authors previews using filters"""
    @abstractmethod
    def get_filtered_series(self, filters: dict, offset=0, limit=100):
        """get series previews using filters"""


class SearchRepository(ISearchRepository, rep.QRRepository):
    def __init__(self):
        super().__init__()

    def connect_repository(self, config: IQRConfig):
        super().connect_repository(config)
        global op, books, authors, books_authors, series, books_series, publications, book_files
        op = self.db.operators
        books = self.db.books
        authors = self.db.authors
        books_authors = self.db.books_authors
        series = self.db.series
        books_series = self.db.books_series
        publications = self.db.publications
        book_files = self.db.book_files

    def __extend_book_data(self, data):
        if len(data) == 0: return data
        book_ids = "'{" + ', '.join([str(x['id']) for x in data]) + "}'"
        raw = '''select * from get_books_authors(%s) as 
            s(book_id integer, author_id integer, author_name varchar)''' % book_ids
        authors = self.db.exec(raw).config_fields('book_id', 'author_id', 'author_name').all()

        book_ids = book_ids[2: -2]
        raw = '''select s.title as title, series_id, book_id, book_number from books_series 
        join series s on books_series.series_id = s.id
        where book_id in (%s)''' % book_ids
        series = self.db.exec(raw).config_fields('title', 'series_id', 'book_id', 'book_number').all()
        # todo orm-usage series = self.db.select(books_series).where(book_id=op.In(book_ids))

        for i in range(len(data)):
            data[i]['authors'] = [{'id': a['author_id'], 'name': a['author_name']} for a in authors
                                  if a['book_id'] == data[i]['id']]
            series = [x for x in series if x['book_id'] == data[i]['id']]
            if series:
                s = series[0]
                data[i]['series'] = {'id': s['series_id'], 'title': s['title']}
                data[i]['book_number'] = s['book_number']
            data[i]['type'] = 'book'

        return data

    def __extend_series_data(self, data):
        if len(data) == 0: return data
        series_ids = "'{" + ', '.join([str(x['id']) for x in data]) + "}'"
        raw = '''select * from get_series_authors(%s) as 
                    s(series_id integer, author_id integer, author_name varchar, books_count int)''' % series_ids
        authors = self.db.exec(raw).config_fields('series_id', 'author_id', 'author_name', 'books_count').all()

        for i in range(len(data)):
            data[i]['authors'] = [{'id': a['author_id'], 'name': a['author_name']} for a in authors
                                  if a['series_id'] == data[i]['id']]
            data[i]['type'] = 'series'
            sb = [a['books_count'] for a in authors if a['series_id'] == data[i]['id']]
            data[i]['books_count'] = 0 if len(sb) == 0 else sb[0]
        return data

    def __extend_author_data(self, data):
        for i in range(len(data)):
            data[i]['type'] = 'author'
        return data

    def get_filtered_books(self, filters:dict, offset=0, limit=100):
        if filters.get('skip'):
            return []

        query = self.db.select(books, books.id, books.title, books.skin_image, books.updated_at, distinct=True)

        if filters.get('sort') == 'series_order':
            query.add_attribute(books_series.book_number)

        if filters.get('genres'):
            query.add_attribute(books.genres)

        self.__add_book_joins(query, filters)
        self.__add_book_wheres(query, filters)

        self.__add_sort(query, filters, books.title, books.updated_at)
        data = query.limit(limit).offset(offset).all()
        return self.__extend_book_data(data)

    def get_filtered_authors(self, filters: dict, offset=0, limit=100):
        if filters.get('skip'):
            return []

        query = authors.select(authors.id, authors.name, authors.photo, authors.updated_at, distinct=True)

        self.__add_author_joins(query, filters)
        self.__add_author_wheres(query, filters)
        self.__add_sort(query, filters, authors.name, authors.updated_at)
        data = query.limit(limit).offset(offset).all()
        return self.__extend_author_data(data)

    def get_filtered_series(self, filters: dict, offset=0, limit=100):
        if filters.get('skip'):
            return []

        query = series.select(series, series.id, series.title, series.skin_image, series.updated_at, distinct=True)

        self.__add_series_joins(query, filters)
        self.__add_series_wheres(query, filters)
        self.__add_sort(query, filters, series.title, series.updated_at)
        data = query.limit(limit).offset(offset).all()
        return self.__extend_series_data(data)

    def __add_book_wheres(self, query, filters):
        if filters.get('search'):
            # todo add search with other fields
            query.where(op.Eq('lower(books.title)', op.Like('%' + filters['search'].lower() + '%')))

        if filters.get('book_id'):
            query.where(op.Eq(books.id, int(filters['book_id'])))
        if filters.get('author_id'):
            query.where(op.Eq(books_authors.author_id, int(filters['author_id'])))
        if filters.get('series_id'):
            query.where(op.Eq(books_series.series_id, int(filters['series_id'])))

        if filters.get('language'):
            query.where(op.Eq(publications.language_code, filters['language']))
        if filters.get('format'):
            query.where(op.Eq(book_files.file_type, filters['format']))
        if filters.get('genres'):
            g = filters['genres']
            genres = ', '.join('"' + x + '"' for x in g)
            '{"Фэнтези", "Юмор"}'
            s = "'{" + genres + "}' && books.genres"
            query.where(s)

    def __add_book_joins(self, query, filters):
        joins = set()
        if filters.get('author_id'):
            if 'books_authors' not in joins:
                joins.update('books_authors')
                query.join(books_authors, 'books_authors.book_id = books.id')

        if filters.get('series_id') or filters.get('series_order'):
            if 'books_series' not in joins:
                joins.update('books_series')
                query.join(books_series, 'books_series.book_id = books.id')

        if filters.get('language') or filters.get('format'):
            if 'publications' not in joins:
                joins.update('publications')
                query.join(publications, 'publications.book_id = books.id')

        if filters.get('format'):
            if 'book_files' not in joins:
                joins.update('book_files')
                query.join(book_files, 'book_files.publication_id = publications.id')


    def __add_author_wheres(self, query, filters):
        if filters.get('search'):
            query.where(op.Eq('lower(authors.name)', op.Like('%' + filters['search'].lower() + '%')))

        if filters.get('author_id'):
            query.where(op.Eq(authors.id, int(filters['author_id'])))

        if filters.get('filtered_books') is not None:
            if len(filters['filtered_books']) == 0:
                filters['filtered_books'] = [-1]
            query.where(op.Eq(books_authors.book_id, op.In(*filters['filtered_books'])))

    def __add_author_joins(self, query, filters):
        if filters.get('filtered_books') is not None:
                query.join(books_authors, 'books_authors.author_id = authors.id')


    def __add_series_wheres(self, query, filters):
        if filters.get('search'):
            query.where(op.Eq('lower(series.title)', op.Like('%' + filters['search'].lower() + '%')))

        if filters.get('series_id'):
            query.where(op.Eq(series.id, int(filters['series_id'])))

        if filters.get('author_id'):
            query.where(op.Eq(books_authors.author_id, int(filters['author_id'])))

        if filters.get('filtered_books') is not None:
            if len(filters['filtered_books']) == 0:
                filters['filtered_books'] = [-1]
            query.where(op.Eq(books_series.book_id, op.In(*filters['filtered_books'])))

    def __add_series_joins(self, query, filters):
        joins = set()
        if filters.get('filtered_books') is not None:
            if 'books_series' not in joins:
                query.join(books_series, 'books_series.series_id = series.id')

        if filters.get('author_id'):
            if 'books_series' not in joins:
                joins.update('books_series')
                query.join(books_series, 'books_series.series_id = series.id')
            if 'books' not in joins:
                joins.update('books')
                query.join(books, 'books_series.book_id = books.id')
            if 'books_authors' not in joins:
                joins.update('books_authors')
                query.join(books_authors, 'books_authors.book_id = books.id')

    def __add_sort(self, query, filters, name_field, date_field):
        sort = filters.get('sort')
        if sort is None: return

        if sort == 'name_acc': query.order_by(name_field, desc=False)
        elif sort == 'name_desc': query.order_by(name_field, desc=True)
        if sort == 'date_acc': query.order_by(date_field, desc=False)
        elif sort == 'date_desc': query.order_by(date_field, desc=True)


    def get_full_author(self, id):
        if self.db is None:
            raise Exception('DBAdapter not connected to database')

        data = self.db.select(authors) \
            .where(id=id).one()

        return data

    def get_full_series(self, id):
        if self.db is None:
            raise Exception('DBAdapter not connected to database')

        data = self.db.select(series).where(id=id).one()
        if not data:
            return data

        return self.__extend_series_data([data])[0]

    def get_full_book(self, id):
        if self.db is None:
            raise Exception('DBAdapter not connected to database')

        data = self.db.select(books).where(id=id).one()
        if not data:
            return data

        publics = self.db.select(publications).where(book_id=id).all()
        files = self.db.select(book_files)\
            .join(publications, self.db.operators.Eq(publications.id, book_files.publication_id))\
            .where(book_id=id).all()

        for p in publics:
            p['files'] = [f for f in files if f['publication_id'] == p['id']]

        data['publications'] = publics
        return self.__extend_book_data([data])[0]

    def get_entities(self, author_ids: List[int] = None, book_ids: List[int] = None, series_ids: List[int] = None):
        if self.db is None:
            raise Exception('DBAdapter not connected to database')

        author_ids = author_ids if author_ids is not None else []
        book_ids = book_ids if book_ids is not None else []
        series_ids = series_ids if series_ids is not None else []

        books = self.db.books
        authors = self.db.authors
        series = self.db.series
        op = self.db.operators

        if len(book_ids) == 0:
            books_data = []
        else:
            books_data = books.select(books.id, books.title, books.skin_image, books.updated_at)\
                .where(id=op.In(*book_ids)).all()
            books_data = self.__extend_book_data(books_data)

        if len(author_ids) == 0:
            authors_data = []
        else:
            authors_data = authors.select(authors.id, authors.name, authors.photo, authors.updated_at)\
                .where(id=op.In(*author_ids)).all()
            authors_data = self.__extend_author_data(authors_data)

        if len(series_ids) == 0:
            series_data = []
        else:
            series_data = series.select(series.id, series.title, series.skin_image, series.updated_at)\
                .where(id=op.In(*series_ids)).all()
            series_data = self.__extend_series_data(series_data)

        return list(chain(authors_data, books_data, series_data))