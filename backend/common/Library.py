from qr_server.Repository import QRRepository


class LibraryRepository(QRRepository):
    def extend_book_data(self, data):
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

    def extend_series_data(self, data):
        if len(data) == 0: return data
        series_ids = "'{" + ', '.join([str(x['id']) for x in data]) + "}'"
        raw = '''select * from get_series_authors(%s) as 
                    s(series_id integer, author_id integer, author_name varchar, books_count int)''' % series_ids
        authors = self.db.exec(raw).config_fields('series_id', 'author_id', 'author_name', 'books_count').all()

        for i in range(len(data)):
            data[i]['authors'] = [{'id': a['author_id'], 'name': a['author_name']} for a in authors
                                  if a['series_id'] == data[i]['id']]
            data[i]['type'] = 'series'
            data[i]['books_count'] = [a['books_count'] for a in authors if a['series_id'] == data[i]['id']][0]
        return data

    def extend_author_data(self, data):
        for i in range(len(data)):
            data[i]['type'] = 'author'
        return data