-- installing plpython3u:
--apt-get update && apt-get install postgresql-plpython3-13
-- psql -U kurush qrook_db_new
--select version();
--CREATE EXTENSION plpython3u;

-- update books_count for series through all tables
update series
set books_count = sub.cnt
from (select series_id, count(*) as cnt from books_series join series s on books_series.series_id = s.id
group by series_id) as sub
where id = sub.series_id;

UPDATE authors a
SET    photo = s.photo
FROM   (select id, concat('http://', photo) as photo from authors)
       AS s(id, photo)
WHERE a.id = s.id
AND a.photo is not null;

UPDATE books b
SET    skin_image = b.skin_image
FROM   (select id, concat('http://', skin_image) as skin_image from books)
       AS s(id, skin_image)
WHERE b.id = b.id
AND b.skin_image is not null;

UPDATE series s
SET    skin_image = tmp.skin_image
FROM   (select id, concat('http://', skin_image) as skin_image from series)
       AS tmp(id, skin_image)
WHERE s.id = tmp.id
AND s.skin_image is not null;