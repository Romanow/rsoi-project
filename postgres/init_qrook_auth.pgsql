--
-- PostgreSQL database dump
--

-- Dumped from database version 14.7 (Debian 14.7-1.pgdg110+1)
-- Dumped by pg_dump version 14.7 (Debian 14.7-1.pgdg110+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: oauth2_client; Type: TABLE; Schema: public; Owner: kurush
--

CREATE TABLE public.oauth2_client (
    id integer NOT NULL,
    client_id character varying(48),
    client_secret character varying(120),
    client_id_issued_at integer NOT NULL,
    client_secret_expires_at integer NOT NULL,
    client_metadata text
);


ALTER TABLE public.oauth2_client OWNER TO kurush;

--
-- Name: oauth2_client_id_seq; Type: SEQUENCE; Schema: public; Owner: kurush
--

CREATE SEQUENCE public.oauth2_client_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.oauth2_client_id_seq OWNER TO kurush;

--
-- Name: oauth2_client_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kurush
--

ALTER SEQUENCE public.oauth2_client_id_seq OWNED BY public.oauth2_client.id;


--
-- Name: oauth2_code; Type: TABLE; Schema: public; Owner: kurush
--

CREATE TABLE public.oauth2_code (
    id integer NOT NULL,
    user_id integer,
    code character varying(120) NOT NULL,
    client_id character varying(48),
    redirect_uri text,
    response_type text,
    scope text,
    nonce text,
    auth_time integer NOT NULL,
    code_challenge text,
    code_challenge_method character varying(48)
);


ALTER TABLE public.oauth2_code OWNER TO kurush;

--
-- Name: oauth2_code_id_seq; Type: SEQUENCE; Schema: public; Owner: kurush
--

CREATE SEQUENCE public.oauth2_code_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.oauth2_code_id_seq OWNER TO kurush;

--
-- Name: oauth2_code_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kurush
--

ALTER SEQUENCE public.oauth2_code_id_seq OWNED BY public.oauth2_code.id;


--
-- Name: oauth2_token; Type: TABLE; Schema: public; Owner: kurush
--

CREATE TABLE public.oauth2_token (
    id integer NOT NULL,
    user_id integer,
    client_id character varying(48),
    token_type character varying(40),
    access_token character varying(255) NOT NULL,
    refresh_token character varying(255),
    scope text,
    revoked boolean,
    issued_at integer NOT NULL,
    expires_in integer NOT NULL
);


ALTER TABLE public.oauth2_token OWNER TO kurush;

--
-- Name: oauth2_token_id_seq; Type: SEQUENCE; Schema: public; Owner: kurush
--

CREATE SEQUENCE public.oauth2_token_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.oauth2_token_id_seq OWNER TO kurush;

--
-- Name: oauth2_token_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kurush
--

ALTER SEQUENCE public.oauth2_token_id_seq OWNED BY public.oauth2_token.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: kurush
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    role character varying(32) NOT NULL,
    email character varying(128),
    login character varying(128),
    password character varying(128) NOT NULL,
    name character varying(128),
    surname character varying(128),
    avatar character varying(512)
);


ALTER TABLE public."user" OWNER TO kurush;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: kurush
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_id_seq OWNER TO kurush;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kurush
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: oauth2_client id; Type: DEFAULT; Schema: public; Owner: kurush
--

ALTER TABLE ONLY public.oauth2_client ALTER COLUMN id SET DEFAULT nextval('public.oauth2_client_id_seq'::regclass);


--
-- Name: oauth2_code id; Type: DEFAULT; Schema: public; Owner: kurush
--

ALTER TABLE ONLY public.oauth2_code ALTER COLUMN id SET DEFAULT nextval('public.oauth2_code_id_seq'::regclass);


--
-- Name: oauth2_token id; Type: DEFAULT; Schema: public; Owner: kurush
--

ALTER TABLE ONLY public.oauth2_token ALTER COLUMN id SET DEFAULT nextval('public.oauth2_token_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: kurush
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Data for Name: oauth2_client; Type: TABLE DATA; Schema: public; Owner: kurush
--

COPY public.oauth2_client (id, client_id, client_secret, client_id_issued_at, client_secret_expires_at, client_metadata) FROM stdin;
1	pRiDvVWqbMdVcqUcubD0Y54V	tMWy9xDK6CaCe6LfqpO3BIqkjVgm8eEUnMLAdHaV5IO32Riu	1682255337	0	{"client_name":"qrook","client_uri":"https://authlib.org","grant_types":["authorization_code"],"redirect_uris":["http://localhost:8080/auth_callback"],"response_types":["code"],"scope":"openid profile email","token_endpoint_auth_method":"client_secret_basic"}
2	2anATLPeTFWid8WXq5rKm964	WD2QLXYSn5xHT9PoeYNLfQGUWlYSGEfB4LKNppg5eUcAN5XT	1682255392	0	{"client_name":"dummy_client","client_uri":"https://example.com","grant_types":["authorization_code"],"redirect_uris":["https://example.com"],"response_types":["code"],"scope":"openid","token_endpoint_auth_method":"client_secret_basic"}
\.


--
-- Data for Name: oauth2_code; Type: TABLE DATA; Schema: public; Owner: kurush
--

COPY public.oauth2_code (id, user_id, code, client_id, redirect_uri, response_type, scope, nonce, auth_time, code_challenge, code_challenge_method) FROM stdin;
\.


--
-- Data for Name: oauth2_token; Type: TABLE DATA; Schema: public; Owner: kurush
--

COPY public.oauth2_token (id, user_id, client_id, token_type, access_token, refresh_token, scope, revoked, issued_at, expires_in) FROM stdin;
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: kurush
--

COPY public."user" (id, role, email, login, password, name, surname, avatar) FROM stdin;
1	admin	ze17@ya.ru	kurush	pondoxo	kurush	pondoxo	\N
2	user	dummy@ya.ru	dummy	dummy	dummy	dummy	\N
\.


--
-- Name: oauth2_client_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kurush
--

SELECT pg_catalog.setval('public.oauth2_client_id_seq', 2, true);


--
-- Name: oauth2_code_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kurush
--

SELECT pg_catalog.setval('public.oauth2_code_id_seq', 1, false);


--
-- Name: oauth2_token_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kurush
--

SELECT pg_catalog.setval('public.oauth2_token_id_seq', 1, false);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kurush
--

SELECT pg_catalog.setval('public.user_id_seq', 2, true);


--
-- Name: oauth2_client oauth2_client_pkey; Type: CONSTRAINT; Schema: public; Owner: kurush
--

ALTER TABLE ONLY public.oauth2_client
    ADD CONSTRAINT oauth2_client_pkey PRIMARY KEY (id);


--
-- Name: oauth2_code oauth2_code_code_key; Type: CONSTRAINT; Schema: public; Owner: kurush
--

ALTER TABLE ONLY public.oauth2_code
    ADD CONSTRAINT oauth2_code_code_key UNIQUE (code);


--
-- Name: oauth2_code oauth2_code_pkey; Type: CONSTRAINT; Schema: public; Owner: kurush
--

ALTER TABLE ONLY public.oauth2_code
    ADD CONSTRAINT oauth2_code_pkey PRIMARY KEY (id);


--
-- Name: oauth2_token oauth2_token_access_token_key; Type: CONSTRAINT; Schema: public; Owner: kurush
--

ALTER TABLE ONLY public.oauth2_token
    ADD CONSTRAINT oauth2_token_access_token_key UNIQUE (access_token);


--
-- Name: oauth2_token oauth2_token_pkey; Type: CONSTRAINT; Schema: public; Owner: kurush
--

ALTER TABLE ONLY public.oauth2_token
    ADD CONSTRAINT oauth2_token_pkey PRIMARY KEY (id);


--
-- Name: user user_email_key; Type: CONSTRAINT; Schema: public; Owner: kurush
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- Name: user user_login_key; Type: CONSTRAINT; Schema: public; Owner: kurush
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_login_key UNIQUE (login);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: kurush
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: ix_oauth2_client_client_id; Type: INDEX; Schema: public; Owner: kurush
--

CREATE INDEX ix_oauth2_client_client_id ON public.oauth2_client USING btree (client_id);


--
-- Name: ix_oauth2_token_refresh_token; Type: INDEX; Schema: public; Owner: kurush
--

CREATE INDEX ix_oauth2_token_refresh_token ON public.oauth2_token USING btree (refresh_token);


--
-- Name: oauth2_code oauth2_code_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: kurush
--

ALTER TABLE ONLY public.oauth2_code
    ADD CONSTRAINT oauth2_code_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: oauth2_token oauth2_token_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: kurush
--

ALTER TABLE ONLY public.oauth2_token
    ADD CONSTRAINT oauth2_token_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

