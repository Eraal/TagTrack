PGDMP  9            
        }            tagtrack    17.2    17.2 .    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                           false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                           false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                           false            �           1262    16558    tagtrack    DATABASE     �   CREATE DATABASE tagtrack WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'English_United States.1252';
    DROP DATABASE tagtrack;
                     postgres    false            �            1259    16560 
   categories    TABLE     �   CREATE TABLE public.categories (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text DEFAULT 'No description'::text,
    status character varying(20) DEFAULT 'Active'::character varying
);
    DROP TABLE public.categories;
       public         heap r       postgres    false            �            1259    16559    categories_id_seq    SEQUENCE     �   CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 (   DROP SEQUENCE public.categories_id_seq;
       public               postgres    false    218            �           0    0    categories_id_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;
          public               postgres    false    217            �            1259    16604    claims    TABLE     �   CREATE TABLE public.claims (
    id integer NOT NULL,
    item_id integer NOT NULL,
    user_id integer,
    claim_date date NOT NULL,
    status character varying(50) NOT NULL
);
    DROP TABLE public.claims;
       public         heap r       postgres    false            �            1259    16603    claims_id_seq    SEQUENCE     �   CREATE SEQUENCE public.claims_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 $   DROP SEQUENCE public.claims_id_seq;
       public               postgres    false    226            �           0    0    claims_id_seq    SEQUENCE OWNED BY     ?   ALTER SEQUENCE public.claims_id_seq OWNED BY public.claims.id;
          public               postgres    false    225            �            1259    16585    items    TABLE     H  CREATE TABLE public.items (
    id integer NOT NULL,
    category_id integer NOT NULL,
    description text NOT NULL,
    location_id integer NOT NULL,
    date_reported date NOT NULL,
    image_file character varying(255),
    rfid_tag character varying(255),
    status character varying(50) NOT NULL,
    owner_id integer
);
    DROP TABLE public.items;
       public         heap r       postgres    false            �            1259    16584    items_id_seq    SEQUENCE     �   CREATE SEQUENCE public.items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 #   DROP SEQUENCE public.items_id_seq;
       public               postgres    false    224            �           0    0    items_id_seq    SEQUENCE OWNED BY     =   ALTER SEQUENCE public.items_id_seq OWNED BY public.items.id;
          public               postgres    false    223            �            1259    16567 	   locations    TABLE     d   CREATE TABLE public.locations (
    id integer NOT NULL,
    name character varying(50) NOT NULL
);
    DROP TABLE public.locations;
       public         heap r       postgres    false            �            1259    16566    locations_id_seq    SEQUENCE     �   CREATE SEQUENCE public.locations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 '   DROP SEQUENCE public.locations_id_seq;
       public               postgres    false    220            �           0    0    locations_id_seq    SEQUENCE OWNED BY     E   ALTER SEQUENCE public.locations_id_seq OWNED BY public.locations.id;
          public               postgres    false    219            �            1259    16574    users    TABLE     �   CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    student_id character varying(50) NOT NULL,
    contact_number character varying(15)
);
    DROP TABLE public.users;
       public         heap r       postgres    false            �            1259    16573    users_id_seq    SEQUENCE     �   CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 #   DROP SEQUENCE public.users_id_seq;
       public               postgres    false    222            �           0    0    users_id_seq    SEQUENCE OWNED BY     =   ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;
          public               postgres    false    221            5           2604    16563    categories id    DEFAULT     n   ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);
 <   ALTER TABLE public.categories ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    218    217    218            ;           2604    16607 	   claims id    DEFAULT     f   ALTER TABLE ONLY public.claims ALTER COLUMN id SET DEFAULT nextval('public.claims_id_seq'::regclass);
 8   ALTER TABLE public.claims ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    226    225    226            :           2604    16588    items id    DEFAULT     d   ALTER TABLE ONLY public.items ALTER COLUMN id SET DEFAULT nextval('public.items_id_seq'::regclass);
 7   ALTER TABLE public.items ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    224    223    224            8           2604    16570    locations id    DEFAULT     l   ALTER TABLE ONLY public.locations ALTER COLUMN id SET DEFAULT nextval('public.locations_id_seq'::regclass);
 ;   ALTER TABLE public.locations ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    219    220    220            9           2604    16577    users id    DEFAULT     d   ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);
 7   ALTER TABLE public.users ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    222    221    222            �          0    16560 
   categories 
   TABLE DATA           C   COPY public.categories (id, name, description, status) FROM stdin;
    public               postgres    false    218   '4       �          0    16604    claims 
   TABLE DATA           J   COPY public.claims (id, item_id, user_id, claim_date, status) FROM stdin;
    public               postgres    false    226   �4       �          0    16585    items 
   TABLE DATA           �   COPY public.items (id, category_id, description, location_id, date_reported, image_file, rfid_tag, status, owner_id) FROM stdin;
    public               postgres    false    224   �4       �          0    16567 	   locations 
   TABLE DATA           -   COPY public.locations (id, name) FROM stdin;
    public               postgres    false    220   �5       �          0    16574    users 
   TABLE DATA           L   COPY public.users (id, name, email, student_id, contact_number) FROM stdin;
    public               postgres    false    222   /6       �           0    0    categories_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.categories_id_seq', 6, true);
          public               postgres    false    217            �           0    0    claims_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('public.claims_id_seq', 6, true);
          public               postgres    false    225            �           0    0    items_id_seq    SEQUENCE SET     :   SELECT pg_catalog.setval('public.items_id_seq', 9, true);
          public               postgres    false    223            �           0    0    locations_id_seq    SEQUENCE SET     >   SELECT pg_catalog.setval('public.locations_id_seq', 6, true);
          public               postgres    false    219            �           0    0    users_id_seq    SEQUENCE SET     :   SELECT pg_catalog.setval('public.users_id_seq', 8, true);
          public               postgres    false    221            =           2606    16565    categories categories_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);
 D   ALTER TABLE ONLY public.categories DROP CONSTRAINT categories_pkey;
       public                 postgres    false    218            I           2606    16609    claims claims_pkey 
   CONSTRAINT     P   ALTER TABLE ONLY public.claims
    ADD CONSTRAINT claims_pkey PRIMARY KEY (id);
 <   ALTER TABLE ONLY public.claims DROP CONSTRAINT claims_pkey;
       public                 postgres    false    226            G           2606    16592    items items_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.items DROP CONSTRAINT items_pkey;
       public                 postgres    false    224            ?           2606    16572    locations locations_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_pkey PRIMARY KEY (id);
 B   ALTER TABLE ONLY public.locations DROP CONSTRAINT locations_pkey;
       public                 postgres    false    220            A           2606    16581    users users_email_key 
   CONSTRAINT     Q   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);
 ?   ALTER TABLE ONLY public.users DROP CONSTRAINT users_email_key;
       public                 postgres    false    222            C           2606    16579    users users_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public                 postgres    false    222            E           2606    16583    users users_student_id_key 
   CONSTRAINT     [   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_student_id_key UNIQUE (student_id);
 D   ALTER TABLE ONLY public.users DROP CONSTRAINT users_student_id_key;
       public                 postgres    false    222            M           2606    16610    claims claims_item_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.claims
    ADD CONSTRAINT claims_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id) ON DELETE CASCADE;
 D   ALTER TABLE ONLY public.claims DROP CONSTRAINT claims_item_id_fkey;
       public               postgres    false    224    226    4679            N           2606    16615    claims claims_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.claims
    ADD CONSTRAINT claims_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
 D   ALTER TABLE ONLY public.claims DROP CONSTRAINT claims_user_id_fkey;
       public               postgres    false    222    226    4675            J           2606    16593    items items_category_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id) ON DELETE CASCADE;
 F   ALTER TABLE ONLY public.items DROP CONSTRAINT items_category_id_fkey;
       public               postgres    false    224    218    4669            K           2606    16598    items items_location_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id) ON DELETE CASCADE;
 F   ALTER TABLE ONLY public.items DROP CONSTRAINT items_location_id_fkey;
       public               postgres    false    4671    224    220            L           2606    49434    items items_owner_id_fkey    FK CONSTRAINT     y   ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);
 C   ALTER TABLE ONLY public.items DROP CONSTRAINT items_owner_id_fkey;
       public               postgres    false    222    4675    224            �   ~   x�M�M
�@FיS��^�E��p� �q�T��*T���=>���pX-�u�r����p�s�S��,��T��%K�T����#�&G*��j��b^���_�p���M ^��K)��*<J      �   ,   x�3�4���4202�50�5��t�I��MM�2�4�!���� ^(a      �   �   x�u����0���)x�xՓY5��/\��[lSJԷ�%d������2�a0���	>���!QFq��\4�����^�j~��@��	���7�.�@10P�4Jj�է0��ֺ��ݑ�]4A���XK��h-@�2Ru�eiۛ^12��m�v�,<ɠ�G&$����g�_�u��_�]ֹ��K�����Wˇ���)Y���2�`s��L6#���/�      �   6   x�3��wL�2�tN�+IM��2�tv�2�t���2r�\��8�C\�b���� �
q      �      x�}�;�0�z�\ k���-=͢��%�"!�=2H�s33�58J�< �6�;�),:N�f�o���[W�M�yjqݝ4F�S��GQ�M���*K��oa�����,)	��EVo����&�B     