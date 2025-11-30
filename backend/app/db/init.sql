--
-- PostgreSQL database dump
--

-- Dumped from database version 15.14 (Debian 15.14-1.pgdg13+1)
-- Dumped by pg_dump version 15.14 (Debian 15.14-1.pgdg13+1)

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
-- Clean existing objects so the script can be re-run idempotently
--
DROP TABLE IF EXISTS public.expense_split CASCADE;
DROP TABLE IF EXISTS public.expense CASCADE;
DROP TABLE IF EXISTS public.group_invite CASCADE;
DROP TABLE IF EXISTS public.group_members CASCADE;
DROP TABLE IF EXISTS public."group" CASCADE;
DROP TABLE IF EXISTS public."user" CASCADE;

--
-- Name: expense; Type: TABLE; Schema: public; Owner: mycountadmin
--

CREATE TABLE public.expense (
    id integer NOT NULL,
    amount double precision NOT NULL,
    description character varying,
    group_id integer NOT NULL,
    paid_by_id integer NOT NULL,
    created_by_id integer NOT NULL
);


ALTER TABLE public.expense OWNER TO mycountadmin;

--
-- Name: expense_id_seq; Type: SEQUENCE; Schema: public; Owner: mycountadmin
--

CREATE SEQUENCE public.expense_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.expense_id_seq OWNER TO mycountadmin;

--
-- Name: expense_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mycountadmin
--

ALTER SEQUENCE public.expense_id_seq OWNED BY public.expense.id;


--
-- Name: expense_split; Type: TABLE; Schema: public; Owner: mycountadmin
--

CREATE TABLE public.expense_split (
    id integer NOT NULL,
    expense_id integer NOT NULL,
    user_id integer NOT NULL,
    amount double precision NOT NULL
);


ALTER TABLE public.expense_split OWNER TO mycountadmin;

--
-- Name: expense_split_id_seq; Type: SEQUENCE; Schema: public; Owner: mycountadmin
--

CREATE SEQUENCE public.expense_split_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.expense_split_id_seq OWNER TO mycountadmin;

--
-- Name: expense_split_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mycountadmin
--

ALTER SEQUENCE public.expense_split_id_seq OWNED BY public.expense_split.id;


--
-- Name: group; Type: TABLE; Schema: public; Owner: mycountadmin
--

CREATE TABLE public."group" (
    id integer NOT NULL,
    name character varying NOT NULL,
    pw character varying NOT NULL,
    emoji text
);


ALTER TABLE public."group" OWNER TO mycountadmin;

--
-- Name: group_id_seq; Type: SEQUENCE; Schema: public; Owner: mycountadmin
--

CREATE SEQUENCE public.group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.group_id_seq OWNER TO mycountadmin;

--
-- Name: group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mycountadmin
--

ALTER SEQUENCE public.group_id_seq OWNED BY public."group".id;


--
-- Name: group_invite; Type: TABLE; Schema: public; Owner: mycountadmin
--

CREATE TABLE public.group_invite (
    id integer NOT NULL,
    token character varying NOT NULL,
    group_id integer NOT NULL,
    created_by_id integer NOT NULL,
    expires_at timestamp with time zone,
    used boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.group_invite OWNER TO mycountadmin;

--
-- Name: group_invite_id_seq; Type: SEQUENCE; Schema: public; Owner: mycountadmin
--

CREATE SEQUENCE public.group_invite_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.group_invite_id_seq OWNER TO mycountadmin;

--
-- Name: group_invite_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mycountadmin
--

ALTER SEQUENCE public.group_invite_id_seq OWNED BY public.group_invite.id;


--
-- Name: group_members; Type: TABLE; Schema: public; Owner: mycountadmin
--

CREATE TABLE public.group_members (
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.group_members OWNER TO mycountadmin;

--
-- Name: user; Type: TABLE; Schema: public; Owner: mycountadmin
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    name character varying NOT NULL,
    pw character varying NOT NULL,
    email character varying NOT NULL
);


ALTER TABLE public."user" OWNER TO mycountadmin;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: mycountadmin
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_id_seq OWNER TO mycountadmin;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mycountadmin
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: expense id; Type: DEFAULT; Schema: public; Owner: mycountadmin
--

ALTER TABLE ONLY public.expense ALTER COLUMN id SET DEFAULT nextval('public.expense_id_seq'::regclass);


--
-- Name: expense_split id; Type: DEFAULT; Schema: public; Owner: mycountadmin
--

ALTER TABLE ONLY public.expense_split ALTER COLUMN id SET DEFAULT nextval('public.expense_split_id_seq'::regclass);


--
-- Name: group id; Type: DEFAULT; Schema: public; Owner: mycountadmin
--

ALTER TABLE ONLY public."group" ALTER COLUMN id SET DEFAULT nextval('public.group_id_seq'::regclass);


--
-- Name: group_invite id; Type: DEFAULT; Schema: public; Owner: mycountadmin
--

ALTER TABLE ONLY public.group_invite ALTER COLUMN id SET DEFAULT nextval('public.group_invite_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: mycountadmin
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Data for Name: expense; Type: TABLE DATA; Schema: public; Owner: mycountadmin
--

COPY public.expense (id, amount, description, group_id, paid_by_id, created_by_id) FROM stdin;
3	100	balance	1	4	4
5	13.13	Tricount	5	5	5
6	832.01	IB Prepared	5	6	5
7	92	Groceries	3	6	6
8	23	Wifi	3	5	6
9	82.12	Utilities	3	5	6
10	123	Bar	4	6	6
11	34	Club	4	6	6
12	132	Lunch	4	7	7
13	928	VM	5	5	7
\.


--
-- Data for Name: expense_split; Type: TABLE DATA; Schema: public; Owner: mycountadmin
--

COPY public.expense_split (id, expense_id, user_id, amount) FROM stdin;
3	3	4	50
4	3	3	50
7	5	5	6.57
8	5	6	6.56
9	6	5	416.01
10	6	6	416
11	7	6	46
12	7	5	46
13	8	6	11.5
14	8	5	11.5
15	9	6	41.06
16	9	5	41.06
17	10	6	61.5
18	10	5	61.5
19	11	6	33
20	11	5	1
21	12	7	44
22	12	6	44
23	12	5	44
27	13	7	309.33
28	13	5	309.33
29	13	6	309.34
\.


--
-- Data for Name: group; Type: TABLE DATA; Schema: public; Owner: mycountadmin
--

COPY public."group" (id, name, pw, emoji) FROM stdin;
1	apartment	1	🏠
2	trip	1	✈️
3	Apartment	1	🏠
4	Spring Break	1	✈️
5	AWS	1	🚀
\.


--
-- Data for Name: group_invite; Type: TABLE DATA; Schema: public; Owner: mycountadmin
--

COPY public.group_invite (id, token, group_id, created_by_id, expires_at, used, created_at) FROM stdin;
1	GDY4bLkkWFGHbhYVs2GdvQ	1	3	2025-10-05 11:02:14.7506+00	t	2025-10-05 10:52:14.749296+00
2	2GCTlXSsH1BcJz9LZ9tyTQ	1	4	2025-10-05 11:03:28.959144+00	f	2025-10-05 10:53:28.954747+00
3	3nSBvX4UCB0h3xHWrpkSRg	5	6	2025-10-05 11:30:58.606547+00	t	2025-10-05 11:20:58.603403+00
5	BxA1a8D8LRc-TA7_OmgjXg	3	5	2025-10-05 11:32:51.622062+00	t	2025-10-05 11:22:51.617836+00
4	lAsDT8bOqY3RTiuC0B5Upg	4	5	2025-10-05 11:32:38.802432+00	t	2025-10-05 11:22:38.799238+00
\.


--
-- Data for Name: group_members; Type: TABLE DATA; Schema: public; Owner: mycountadmin
--

COPY public.group_members (user_id, group_id) FROM stdin;
3	1
4	1
3	2
5	3
5	4
6	5
5	5
6	3
6	4
7	4
7	5
8	3
8	5
8	4
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: mycountadmin
--

COPY public."user" (id, name, pw, email) FROM stdin;
1	Boris Gans	$argon2id$v=19$m=65536,t=3,p=4$5BxD6H1PKeXcu9caIyRkTA$vN3fV3n0qAb1S235dybHGgn5CooREU3Aw/LuNEmslN8	borisgans418@gmail.com
2	matt	$argon2id$v=19$m=65536,t=3,p=4$cC7FeC9l7L13DgFgDEHoHQ$Fe8YJ37Y9bYo+nDsGlEuOtSPNUhWXemJiKzBGu6KuDs	s@s
3	testing	$argon2id$v=19$m=65536,t=3,p=4$EILwvjfG+N+7F6JUSomRcg$pw/H3jBeVEObxJRxwL+W95JOAd8tTOr+yocL1oZ3VBM	1@1
4	ryan	$argon2id$v=19$m=65536,t=3,p=4$ndMag7BWitHaO0eI0boXwg$7zLN6ZxiiSsE9WwwyWVkILJpdTefroQaUKnDD45QksE	2@2
5	Boris Gans	$argon2id$v=19$m=65536,t=3,p=4$K6W09p6TMkZo7R0jxPjfuw$b9mMfpNZX8ZxDNPglowk+tW9478KCU1XMIPPNX5HoAo	borisgans@gmail.com
6	Matt Porteous	$argon2id$v=19$m=65536,t=3,p=4$9z6nVArBmNNaC8F47x3jXA$iZ6UAMgiLfuAMINV+2YH6ijqfJDNc1xAPPT6jy4qgws	mp@gmail.com
7	Ryan M	$argon2id$v=19$m=65536,t=3,p=4$j3Fu7Z0zRmjtfW8thTAmRA$nBcMY5GNnXPPo/5pMsNojUbp3x3doZUPQChDEw10xZo	rm@gmail.com
8	Borja Serra Planelles	$argon2id$v=19$m=65536,t=3,p=4$LcVYy/lfi5ESAsCYU8pZ6w$WonG2YA8pFb3Um/RcXceZIG/PbkjKobqBb2yEt5trg4	borja@gmail.com
\.


--
-- Name: expense_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mycountadmin
--

SELECT pg_catalog.setval('public.expense_id_seq', 13, true);


--
-- Name: expense_split_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mycountadmin
--

SELECT pg_catalog.setval('public.expense_split_id_seq', 29, true);


--
-- Name: group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mycountadmin
--

SELECT pg_catalog.setval('public.group_id_seq', 5, true);


--
-- Name: group_invite_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mycountadmin
--

SELECT pg_catalog.setval('public.group_invite_id_seq', 5, true);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mycountadmin
--

SELECT pg_catalog.setval('public.user_id_seq', 8, true);


--
-- Name: expense expense_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense
    ADD CONSTRAINT expense_pkey PRIMARY KEY (id);


--
-- Name: expense_split expense_split_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_split
    ADD CONSTRAINT expense_split_pkey PRIMARY KEY (id);


--
-- Name: group_invite group_invite_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.group_invite
    ADD CONSTRAINT group_invite_pkey PRIMARY KEY (id);


--
-- Name: group_members group_members_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.group_members
    ADD CONSTRAINT group_members_pkey PRIMARY KEY (user_id, group_id);


--
-- Name: group group_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."group"
    ADD CONSTRAINT group_pkey PRIMARY KEY (id);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: ix_group_invite_token; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_group_invite_token ON public.group_invite USING btree (token);


--
-- Name: expense expense_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense
    ADD CONSTRAINT expense_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public."user"(id);


--
-- Name: expense expense_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense
    ADD CONSTRAINT expense_group_id_fkey FOREIGN KEY (group_id) REFERENCES public."group"(id);


--
-- Name: expense expense_paid_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense
    ADD CONSTRAINT expense_paid_by_id_fkey FOREIGN KEY (paid_by_id) REFERENCES public."user"(id);


--
-- Name: expense_split expense_split_expense_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_split
    ADD CONSTRAINT expense_split_expense_id_fkey FOREIGN KEY (expense_id) REFERENCES public.expense(id);


--
-- Name: expense_split expense_split_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_split
    ADD CONSTRAINT expense_split_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: group_invite group_invite_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.group_invite
    ADD CONSTRAINT group_invite_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public."user"(id);


--
-- Name: group_invite group_invite_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.group_invite
    ADD CONSTRAINT group_invite_group_id_fkey FOREIGN KEY (group_id) REFERENCES public."group"(id);


--
-- Name: group_members group_members_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.group_members
    ADD CONSTRAINT group_members_group_id_fkey FOREIGN KEY (group_id) REFERENCES public."group"(id);


--
-- Name: group_members group_members_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.group_members
    ADD CONSTRAINT group_members_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- PostgreSQL database dump complete
--
