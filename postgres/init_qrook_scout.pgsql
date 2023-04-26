--
-- PostgreSQL database dump
--


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



CREATE SCHEMA qrook;

--
-- Name: plpython3u; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpython3u WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpython3u; Type: COMMENT; Schema: -; Owner:
--

COMMENT ON EXTENSION plpython3u IS 'PL/Python3U untrusted procedural language';





--
-- Name: intelligence; Type: TABLE; Schema: public; Owner: kurush
--

CREATE TABLE public.intelligence (
    id integer NOT NULL,
    "time" timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    event character varying(100) NOT NULL,
    data jsonb
);


ALTER TABLE public.intelligence OWNER TO kurush;

--
-- Name: intelligence_id_seq; Type: SEQUENCE; Schema: public; Owner: kurush
--

ALTER TABLE public.intelligence ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.intelligence_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);





--
-- Name: recent_viewed; Type: TABLE; Schema: public; Owner: kurush
--

CREATE TABLE public.recent_viewed (
    id integer NOT NULL,
    user_login character varying(256),
    entity_id integer,
    entity_type character varying(128),
    "time" timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.recent_viewed OWNER TO kurush;

--
-- Name: recent_viewed_id_seq; Type: SEQUENCE; Schema: public; Owner: kurush
--

ALTER TABLE public.recent_viewed ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.recent_viewed_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);