-- book files update
CREATE OR REPLACE FUNCTION public.update_files_tf()
RETURNS TRIGGER AS $$ BEGIN
    NEW."updated_at" := now();
    update publications set updated_at = now() where id = NEW.publication_id;
RETURN NEW; END; $$ LANGUAGE plpgsql;


CREATE TRIGGER update_files_trigger
    BEFORE UPDATE or INSERT ON book_files
    FOR EACH ROW
    EXECUTE PROCEDURE update_files_tf();

-- publications update
CREATE OR REPLACE FUNCTION public.update_publications_tf()
RETURNS TRIGGER AS $$ BEGIN
    NEW."updated_at" := now();
    update books set updated_at = now() where id = NEW.book_id;
RETURN NEW; END; $$ LANGUAGE plpgsql;

CREATE TRIGGER update_publications_trigger
    BEFORE UPDATE or INSERT ON publications
    FOR EACH ROW
    EXECUTE PROCEDURE update_publications_tf();

-- book update
CREATE OR REPLACE FUNCTION public.update_book_tf()
RETURNS TRIGGER AS $$ BEGIN
    NEW."updated_at" := now();
    update authors set updated_at = now() where id in (select author_id from books_authors
                                                       where book_id = NEW.id);
    update series set updated_at = now() where id in (select series_id from books_series
                                                   where book_id = NEW.id);
RETURN NEW; END; $$ LANGUAGE plpgsql;

CREATE TRIGGER update_book_trigger
    BEFORE UPDATE or INSERT ON books
    FOR EACH ROW
    EXECUTE PROCEDURE update_book_tf();

-- series update
CREATE OR REPLACE FUNCTION public.update_series_tf()
RETURNS TRIGGER AS $$ BEGIN
    NEW."updated_at" := now();
    update authors set updated_at = now() where id in (select author_id from books_authors
                join books_series bs on books_authors.book_id = bs.book_id
                where series_id = NEW.id);
RETURN NEW; END; $$ LANGUAGE plpgsql;

CREATE TRIGGER update_series_trigger
    BEFORE UPDATE or INSERT ON series
    FOR EACH ROW
    EXECUTE PROCEDURE update_series_tf();


-- authors update
CREATE OR REPLACE FUNCTION public.update_author_tf()
RETURNS TRIGGER AS $$ BEGIN
    NEW."updated_at" := now();
RETURN NEW; END; $$ LANGUAGE plpgsql;

CREATE TRIGGER update_author_trigger
    BEFORE UPDATE or INSERT ON authors
    FOR EACH ROW
    EXECUTE PROCEDURE update_author_tf();