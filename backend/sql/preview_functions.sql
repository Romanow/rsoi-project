-- used in book and series previews
create type author_minimal as
(
    id   int,
    name varchar(256)
);

create type book_preview as
(
    id         int,
    title      varchar(256),
    authors    author_minimal[],
    skin_image varchar
);

create type series_preview as
(
    id          smallint,
    title       varchar(256),
    skin_image  varchar,
    books_count int,
    authors     author_minimal[]
);

create type author_preview as
(
    id   int,
    name varchar(256),
    photo varchar
);


-- for a given book id, return all its authors' ids and names
-- example: select * from get_book_authors(1) as f(id int, name varchar);
create or replace function get_book_authors(book_id_param integer) returns SETOF record
    language plpgsql
as
$$
BEGIN
    RETURN QUERY SELECT a.id AS id, a.name as name
                 FROM books b
                          JOIN books_authors ba ON b.id = ba.book_id
                          JOIN authors a ON a.id = ba.author_id
                 WHERE b.id = book_id_param;
END;
$$;

create or replace function get_books_authors(book_ids_param integer[]) returns SETOF record
as
$$
str_params = ', '.join([str(x) for x in book_ids_param])
query = '''SELECT distinct b.id as book_id, a.id AS author_id, a.name as author_name
         FROM books b
                  JOIN books_authors ba ON b.id = ba.book_id
                  JOIN authors a ON a.id = ba.author_id
         WHERE b.id in (%s)''' % str_params
a_ids = list(plpy.execute(query))
return a_ids
$$ language plpython3u;
select * from get_books_authors('{1, 2}') as s(book_id integer, author_id integer, author_name varchar);


create or replace function get_series_authors(series_ids_param integer[]) returns SETOF record
as
$$
str_params = ', '.join([str(x) for x in series_ids_param])
query = '''select distinct s.id as series_id, a.id as author_id, a.name as author_name, s.books_count as books_count
            from series s
            join books_series on books_series.series_id = s.id
            join books_authors ba on books_series.book_id = ba.book_id
            join authors a on a.id = ba.author_id
            WHERE s.id in (%s) group by s.id, a.id, a.name''' % str_params
a_data = list(plpy.execute(query))
return a_data
$$ language plpython3u;
select * from get_series_authors('{1, 10}') as s(series_id integer, author_id integer, author_name varchar, books_count int);

-- by book id, return its preview
-- usage example: select * from get_book_preview(1);
create or replace function get_book_preview(book_id_param integer) returns book_preview
as
$$
books = plpy.execute(''' select id, title, skin_image from books where id = %d''' % book_id_param)
if len(books) == 0: return None

authors = list(plpy.execute('''select * from get_book_authors(%d) as f(id int, name varchar);''' % book_id_param))
return {
    'id': books[0]['id'],
    'title': books[0]['title'],
    'skin_image': books[0]['skin_image'],
    'authors': authors
}
$$ language plpython3u;

select * from get_series_preview(4);
-- by series id return its preview
-- usage example: select * from get_series_preview(8);
create or replace function get_series_preview(series_id_param integer) returns series_preview
as
$$
series = plpy.execute(''' select s.id, s.title, s.skin_image from series s where id = %d''' % series_id_param)
if len(series) == 0: return None

result = {
    'id': series[0]['id'],
    'title': series[0]['title'],
    'skin_image': series[0]['skin_image'],
}

data = plpy.execute(''' SELECT bs.book_id as id
                            from books_series bs
                            join series s on bs.series_id = s.id
                            where series_id = %d''' % series_id_param)
count = len(data)
result['books_count'] = count
if count == 0: return result

book_id = data[0]['id']
authors = list(plpy.execute('''select * from get_book_authors(%d) as f(id int, name varchar);''' % book_id))
result['authors'] = authors
return result
$$ language plpython3u;


-- by author id, return its preview
-- usage example: select * from get_book_preview(1);
create or replace function get_author_preview(author_id_param integer) returns author_preview
as
$$
authors = plpy.execute(''' select id, name, photo from authors where id = %d''' % author_id_param)
if len(authors) == 0: return None
return authors[0]
$$ language plpython3u;

select * from get_author_preview(1);



grant select on books to guest;
grant select on authors to guest;
grant select on series to guest;
grant select on publications  to guest;
grant select on books_authors to guest;
grant select on books_series to guest;
