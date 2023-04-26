DROP ROLE IF EXISTS guest;
DROP ROLE IF EXISTS reader;
DROP ROLE IF EXISTS moderator;

CREATE ROLE guest;
CREATE ROLE moderator;
CREATE ROLE reader;

ALTER USER moderator WITH PASSWORD 'moderator';
alter role moderator with LOGIN;

GRANT pg_read_all_data TO guest;
GRANT pg_write_all_data TO guest;

GRANT pg_read_all_data TO moderator;
GRANT pg_write_all_data TO moderator;

GRANT pg_read_all_data TO reader;
GRANT pg_write_all_data TO reader;


create table if not exists authors
(
    id          integer generated always as identity
        constraint authors_pkey primary key,
    created_at  timestamp with time zone default current_timestamp not null,
    updated_at  timestamp with time zone default current_timestamp not null,
    name        varchar(256)                                       not null,
    birthdate   date,
    country     varchar(64),
    photo       varchar,
    description varchar
);

create table if not exists series
(
    id          integer generated always as identity
        constraint series_pkey primary key,
    created_at  timestamp with time zone default current_timestamp not null,
    updated_at  timestamp with time zone default current_timestamp not null,
    title       varchar(256)                                       not null,
    is_finished boolean,
    books_count smallint                 default 0,
    skin_image  varchar,
    description varchar
);

create table if not exists books
(
    id          integer generated always as identity
        constraint books_pkey primary key,
    created_at  timestamp with time zone default current_timestamp not null,
    updated_at  timestamp with time zone default current_timestamp not null,
    title       varchar(256)                                       not null,
    skin_image  varchar,
    description varchar,
    genres      varchar[]
);

create table if not exists publications
(
    id               integer generated always as identity
        constraint publications_pkey primary key,
    book_id          integer
        constraint translation_book_fkey references books               not null,
    created_at       timestamp with time zone default current_timestamp not null,
    updated_at       timestamp with time zone default current_timestamp not null,
    publication_year smallint,
    language_code    varchar(2),
    isbn             bigint unique,
    isbn13           bigint unique,
    info             jsonb                    default '{}'
);

create table if not exists book_files
(
    publication_id integer
        constraint publication_fkey references publications           not null,
    created_at     timestamp with time zone default current_timestamp not null,
    updated_at     timestamp with time zone default current_timestamp not null,
    file_path      varchar(256)                                       not null,
    file_type      varchar(16),
    UNIQUE (publication_id, file_path)
);


create table if not exists users
(
    id         serial not null
        constraint users_pkey primary key,
    created_at timestamp with time zone default current_timestamp,
    updated_at timestamp with time zone default current_timestamp,
    name       varchar(256),
    surname    varchar(256),
    email      varchar(64),
    login      varchar(64),
    password   varchar(64),
    avatar     varchar
);

create table if not exists books_authors
(
    author_id integer
        constraint books_authors_author_id_fkey references authors,
    book_id   integer
        constraint books_authors_book_id_fkey references books
);

create table if not exists books_series
(
    series_id   integer
        constraint books_series_series_id_fkey references series,
    book_id     integer unique
        constraint books_series_book_id_fkey references books,
    book_number smallint
);

create table if not exists intelligence
(
    id    integer generated always as identity,
    time  timestamp with time zone default current_timestamp,
    event varchar(100) not null,
    data  jsonb
);

create table if not exists recent_viewed
(
    id          integer generated always as identity,
    user_id     integer
        constraint recent_viewed_user_id_fkey references users,
    entity_id   integer,
    entity_type varchar(128),
    time        timestamp with time zone default current_timestamp
);
