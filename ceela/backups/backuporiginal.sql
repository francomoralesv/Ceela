--
-- PostgreSQL database dump
--

\restrict B7rdqltE89wpjRPcqGzpeshwVOSM91jFNKEAmND4UT495HKfWbADopkB8hXrx4f

-- Dumped from database version 15.14
-- Dumped by pg_dump version 15.14

-- Started on 2025-09-20 10:34:42 UTC

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

ALTER TABLE ONLY public.windows DROP CONSTRAINT windows_enclosure_id_fkey;
ALTER TABLE ONLY public.windowpo DROP CONSTRAINT windowpo_enclosure_id_fkey;
ALTER TABLE ONLY public.walls DROP CONSTRAINT walls_enclosure_id_fkey;
ALTER TABLE ONLY public.wallpo DROP CONSTRAINT wallpo_enclosure_id_fkey;
ALTER TABLE ONLY public.thermals_bridges_walls DROP CONSTRAINT thermals_bridges_walls_enclosure_id_fkey;
ALTER TABLE ONLY public.roofs DROP CONSTRAINT roofs_enclosure_id_fkey;
ALTER TABLE ONLY public.projects DROP CONSTRAINT projects_user_id_fkey;
ALTER TABLE ONLY public.personal_access_token DROP CONSTRAINT personal_access_token_user_id_fkey;
ALTER TABLE ONLY public.orientations DROP CONSTRAINT orientations_enclosure_id_fkey;
ALTER TABLE ONLY public.heating_config DROP CONSTRAINT heating_config_project_id_fkey;
ALTER TABLE ONLY public.formulas DROP CONSTRAINT formulas_project_id_fkey;
ALTER TABLE ONLY public.floors DROP CONSTRAINT floors_enclosure_id_fkey;
ALTER TABLE ONLY public.floorpo DROP CONSTRAINT floorpo_enclosure_id_fkey;
ALTER TABLE ONLY public.enclosures_generals DROP CONSTRAINT enclosures_generals_project_id_fkey;
ALTER TABLE ONLY public.enclosures_generals DROP CONSTRAINT enclosures_generals_occupation_profile_id_fkey;
ALTER TABLE ONLY public.elements DROP CONSTRAINT elements_user_id_fkey;
ALTER TABLE ONLY public.doors DROP CONSTRAINT doors_enclosure_id_fkey;
ALTER TABLE ONLY public.divisions DROP CONSTRAINT divisions_orientation_id_fkey;
ALTER TABLE ONLY public.details DROP CONSTRAINT details_project_id_fkey;
ALTER TABLE ONLY public.constants DROP CONSTRAINT constants_user_id_fkey;
ALTER TABLE ONLY public.comunas DROP CONSTRAINT comunas_region_id_fkey;
ALTER TABLE ONLY public.calculation_results DROP CONSTRAINT calculation_results_project_id_fkey;
ALTER TABLE ONLY public.building_conditions DROP CONSTRAINT building_conditions_enclosure_id_fkey;
DROP INDEX public.ix_wallpo_tipo_muro;
DROP INDEX public.ix_enclosures_code;
DROP INDEX public.ix_constants_name;
ALTER TABLE ONLY public.windows DROP CONSTRAINT windows_pkey;
ALTER TABLE ONLY public.windowpo DROP CONSTRAINT windowpo_pkey;
ALTER TABLE ONLY public.weather_metadata DROP CONSTRAINT weather_metadata_pkey;
ALTER TABLE ONLY public.walls DROP CONSTRAINT walls_pkey;
ALTER TABLE ONLY public.wallpo DROP CONSTRAINT wallpo_pkey;
ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
ALTER TABLE ONLY public.thermals_bridges_walls DROP CONSTRAINT thermals_bridges_walls_pkey;
ALTER TABLE ONLY public.thermal_bridges DROP CONSTRAINT thermal_bridges_pkey;
ALTER TABLE ONLY public.tabla_py DROP CONSTRAINT tabla_py_pkey;
ALTER TABLE ONLY public.roofs DROP CONSTRAINT roofs_pkey;
ALTER TABLE ONLY public.resultados_por_recinto DROP CONSTRAINT resultados_por_recinto_pkey;
ALTER TABLE ONLY public.regiones DROP CONSTRAINT regiones_pkey;
ALTER TABLE ONLY public.pt_table DROP CONSTRAINT pt_table_pkey;
ALTER TABLE ONLY public.projects DROP CONSTRAINT projects_pkey;
ALTER TABLE ONLY public.personal_access_token DROP CONSTRAINT personal_access_token_pkey;
ALTER TABLE ONLY public.orientations DROP CONSTRAINT orientations_pkey;
ALTER TABLE ONLY public.levels DROP CONSTRAINT levels_pkey;
ALTER TABLE ONLY public.indicadores_finales DROP CONSTRAINT indicadores_finales_pkey;
ALTER TABLE ONLY public.heating_config DROP CONSTRAINT heating_config_project_id_key;
ALTER TABLE ONLY public.heating_config DROP CONSTRAINT heating_config_pkey;
ALTER TABLE ONLY public.formulas DROP CONSTRAINT formulas_pkey;
ALTER TABLE ONLY public.floors DROP CONSTRAINT floors_pkey;
ALTER TABLE ONLY public.floorpo DROP CONSTRAINT floorpo_pkey;
ALTER TABLE ONLY public.favs DROP CONSTRAINT favs_pkey;
ALTER TABLE ONLY public.energy_data DROP CONSTRAINT energy_data_pkey;
ALTER TABLE ONLY public.enclosures DROP CONSTRAINT enclosures_pkey;
ALTER TABLE ONLY public.enclosures_generals DROP CONSTRAINT enclosures_generals_pkey;
ALTER TABLE ONLY public.elements DROP CONSTRAINT elements_pkey;
ALTER TABLE ONLY public.doors DROP CONSTRAINT doors_pkey;
ALTER TABLE ONLY public.divisions DROP CONSTRAINT divisions_pkey;
ALTER TABLE ONLY public.details DROP CONSTRAINT details_pkey;
ALTER TABLE ONLY public.details_part DROP CONSTRAINT details_part_pkey;
ALTER TABLE ONLY public.dailyschedule DROP CONSTRAINT dailyschedule_pkey;
ALTER TABLE ONLY public.customizations DROP CONSTRAINT customizations_pkey;
ALTER TABLE ONLY public.constants DROP CONSTRAINT constants_pkey;
ALTER TABLE ONLY public.comunas DROP CONSTRAINT comunas_pkey;
ALTER TABLE ONLY public.casobase DROP CONSTRAINT casobase_pkey;
ALTER TABLE ONLY public.calculations DROP CONSTRAINT calculations_pkey;
ALTER TABLE ONLY public.calculation_results DROP CONSTRAINT calculation_results_pkey;
ALTER TABLE ONLY public.calculate_piso DROP CONSTRAINT calculate_piso_pkey;
ALTER TABLE ONLY public.building_conditions DROP CONSTRAINT building_conditions_pkey;
ALTER TABLE ONLY public.alembic_version DROP CONSTRAINT alembic_version_pkc;
ALTER TABLE ONLY public.agua_caliente DROP CONSTRAINT agua_caliente_pkey;
ALTER TABLE public.windows ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.windowpo ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.weather_metadata ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.walls ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.wallpo ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.users ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.thermals_bridges_walls ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.thermal_bridges ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.tabla_py ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.roofs ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.resultados_por_recinto ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.regiones ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.pt_table ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.projects ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.personal_access_token ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.orientations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.levels ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.indicadores_finales ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.heating_config ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.formulas ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.floors ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.floorpo ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.favs ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.energy_data ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.enclosures_generals ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.enclosures ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.elements ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.doors ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.divisions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.details_part ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.details ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.dailyschedule ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.customizations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.constants ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.comunas ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.casobase ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.calculations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.calculation_results ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.calculate_piso ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.building_conditions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.agua_caliente ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE public.windows_id_seq;
DROP TABLE public.windows;
DROP SEQUENCE public.windowpo_id_seq;
DROP TABLE public.windowpo;
DROP SEQUENCE public.weather_metadata_id_seq;
DROP TABLE public.weather_metadata;
DROP SEQUENCE public.walls_id_seq;
DROP TABLE public.walls;
DROP SEQUENCE public.wallpo_id_seq;
DROP TABLE public.wallpo;
DROP SEQUENCE public.users_id_seq;
DROP TABLE public.users;
DROP SEQUENCE public.thermals_bridges_walls_id_seq;
DROP TABLE public.thermals_bridges_walls;
DROP SEQUENCE public.thermal_bridges_id_seq;
DROP TABLE public.thermal_bridges;
DROP SEQUENCE public.tabla_py_id_seq;
DROP TABLE public.tabla_py;
DROP SEQUENCE public.roofs_id_seq;
DROP TABLE public.roofs;
DROP SEQUENCE public.resultados_por_recinto_id_seq;
DROP TABLE public.resultados_por_recinto;
DROP SEQUENCE public.regiones_id_seq;
DROP TABLE public.regiones;
DROP SEQUENCE public.pt_table_id_seq;
DROP TABLE public.pt_table;
DROP SEQUENCE public.projects_id_seq;
DROP TABLE public.projects;
DROP SEQUENCE public.personal_access_token_id_seq;
DROP TABLE public.personal_access_token;
DROP SEQUENCE public.orientations_id_seq;
DROP TABLE public.orientations;
DROP SEQUENCE public.levels_id_seq;
DROP TABLE public.levels;
DROP SEQUENCE public.indicadores_finales_id_seq;
DROP TABLE public.indicadores_finales;
DROP SEQUENCE public.heating_config_id_seq;
DROP TABLE public.heating_config;
DROP SEQUENCE public.formulas_id_seq;
DROP TABLE public.formulas;
DROP SEQUENCE public.floors_id_seq;
DROP TABLE public.floors;
DROP SEQUENCE public.floorpo_id_seq;
DROP TABLE public.floorpo;
DROP SEQUENCE public.favs_id_seq;
DROP TABLE public.favs;
DROP SEQUENCE public.energy_data_id_seq;
DROP TABLE public.energy_data;
DROP SEQUENCE public.enclosures_id_seq;
DROP SEQUENCE public.enclosures_generals_id_seq;
DROP TABLE public.enclosures_generals;
DROP TABLE public.enclosures;
DROP SEQUENCE public.elements_id_seq;
DROP TABLE public.elements;
DROP SEQUENCE public.doors_id_seq;
DROP TABLE public.doors;
DROP SEQUENCE public.divisions_id_seq;
DROP TABLE public.divisions;
DROP SEQUENCE public.details_part_id_seq;
DROP TABLE public.details_part;
DROP SEQUENCE public.details_id_seq;
DROP TABLE public.details;
DROP SEQUENCE public.dailyschedule_id_seq;
DROP TABLE public.dailyschedule;
DROP SEQUENCE public.customizations_id_seq;
DROP TABLE public.customizations;
DROP SEQUENCE public.constants_id_seq;
DROP TABLE public.constants;
DROP SEQUENCE public.comunas_id_seq;
DROP TABLE public.comunas;
DROP SEQUENCE public.casobase_id_seq;
DROP TABLE public.casobase;
DROP SEQUENCE public.calculations_id_seq;
DROP TABLE public.calculations;
DROP SEQUENCE public.calculation_results_id_seq;
DROP TABLE public.calculation_results;
DROP SEQUENCE public.calculate_piso_id_seq;
DROP TABLE public.calculate_piso;
DROP SEQUENCE public.building_conditions_id_seq;
DROP TABLE public.building_conditions;
DROP TABLE public.alembic_version;
DROP SEQUENCE public.agua_caliente_id_seq;
DROP TABLE public.agua_caliente;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 216 (class 1259 OID 16391)
-- Name: agua_caliente; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agua_caliente (
    t_acs double precision NOT NULL,
    demanda_acs double precision NOT NULL,
    combustible character varying NOT NULL,
    rendimiento character varying NOT NULL,
    sist_distribucion character varying NOT NULL,
    sis_control character varying NOT NULL,
    consumo_acs double precision NOT NULL,
    consumo_energia_primaria double precision NOT NULL,
    energia_primaria double precision NOT NULL,
    data jsonb,
    id integer NOT NULL,
    project_id integer
);


--
-- TOC entry 215 (class 1259 OID 16390)
-- Name: agua_caliente_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.agua_caliente_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3848 (class 0 OID 0)
-- Dependencies: 215
-- Name: agua_caliente_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.agua_caliente_id_seq OWNED BY public.agua_caliente.id;


--
-- TOC entry 214 (class 1259 OID 16385)
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- TOC entry 262 (class 1259 OID 16628)
-- Name: building_conditions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.building_conditions (
    type character varying NOT NULL,
    attributes jsonb,
    id integer NOT NULL,
    enclosure_id integer,
    created_status character varying NOT NULL
);


--
-- TOC entry 261 (class 1259 OID 16627)
-- Name: building_conditions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.building_conditions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3849 (class 0 OID 0)
-- Dependencies: 261
-- Name: building_conditions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.building_conditions_id_seq OWNED BY public.building_conditions.id;


--
-- TOC entry 236 (class 1259 OID 16492)
-- Name: calculate_piso; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.calculate_piso (
    id integer NOT NULL,
    enclosure_id integer NOT NULL,
    floor_id integer NOT NULL,
    b double precision NOT NULL,
    rf double precision NOT NULL,
    df double precision NOT NULL,
    ufg_sog double precision NOT NULL,
    psi double precision NOT NULL,
    u_vert double precision NOT NULL,
    rn_vert double precision NOT NULL,
    dn_vert double precision NOT NULL,
    r_vertical double precision NOT NULL,
    d_vertical double precision NOT NULL,
    psi_vertical double precision NOT NULL,
    u_horiz double precision NOT NULL,
    rn_horiz double precision NOT NULL,
    dn_horiz double precision NOT NULL,
    r_horiz double precision NOT NULL,
    d_horiz double precision NOT NULL,
    psi_horiz double precision NOT NULL,
    psi_min double precision NOT NULL,
    ls double precision NOT NULL
);


--
-- TOC entry 235 (class 1259 OID 16491)
-- Name: calculate_piso_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.calculate_piso_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3850 (class 0 OID 0)
-- Dependencies: 235
-- Name: calculate_piso_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.calculate_piso_id_seq OWNED BY public.calculate_piso.id;


--
-- TOC entry 268 (class 1259 OID 16672)
-- Name: calculation_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.calculation_results (
    id integer NOT NULL,
    final_indicators jsonb NOT NULL,
    result_by_enclosure jsonb NOT NULL,
    co2_eq jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    project_id integer NOT NULL
);


--
-- TOC entry 267 (class 1259 OID 16671)
-- Name: calculation_results_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.calculation_results_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3851 (class 0 OID 0)
-- Dependencies: 267
-- Name: calculation_results_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.calculation_results_id_seq OWNED BY public.calculation_results.id;


--
-- TOC entry 222 (class 1259 OID 16418)
-- Name: calculations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.calculations (
    id integer NOT NULL,
    project_id integer,
    reference_id integer,
    type character varying NOT NULL,
    name character varying NOT NULL,
    formula character varying,
    "values" jsonb
);


--
-- TOC entry 221 (class 1259 OID 16417)
-- Name: calculations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.calculations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3852 (class 0 OID 0)
-- Dependencies: 221
-- Name: calculations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.calculations_id_seq OWNED BY public.calculations.id;


--
-- TOC entry 238 (class 1259 OID 16499)
-- Name: casobase; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.casobase (
    id integer NOT NULL,
    enclosure_id integer,
    type character varying,
    characteristic character varying,
    item_id integer,
    data jsonb
);


--
-- TOC entry 237 (class 1259 OID 16498)
-- Name: casobase_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.casobase_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3853 (class 0 OID 0)
-- Dependencies: 237
-- Name: casobase_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.casobase_id_seq OWNED BY public.casobase.id;


--
-- TOC entry 264 (class 1259 OID 16642)
-- Name: comunas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.comunas (
    id integer NOT NULL,
    nombre_comuna character varying NOT NULL,
    latitud double precision,
    longitud double precision,
    zonas_termicas character varying[],
    region_id integer NOT NULL
);


--
-- TOC entry 263 (class 1259 OID 16641)
-- Name: comunas_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.comunas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3854 (class 0 OID 0)
-- Dependencies: 263
-- Name: comunas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.comunas_id_seq OWNED BY public.comunas.id;


--
-- TOC entry 258 (class 1259 OID 16599)
-- Name: constants; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.constants (
    atributs jsonb,
    name character varying NOT NULL,
    type character varying NOT NULL,
    id integer NOT NULL,
    user_id integer,
    create_status character varying NOT NULL,
    is_deleted boolean NOT NULL,
    code_ifc character varying
);


--
-- TOC entry 257 (class 1259 OID 16598)
-- Name: constants_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.constants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3855 (class 0 OID 0)
-- Dependencies: 257
-- Name: constants_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.constants_id_seq OWNED BY public.constants.id;


--
-- TOC entry 242 (class 1259 OID 16517)
-- Name: customizations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.customizations (
    id integer NOT NULL,
    primary_color character varying NOT NULL,
    secondary_color character varying NOT NULL,
    background_color character varying NOT NULL,
    logo_url character varying NOT NULL
);


--
-- TOC entry 241 (class 1259 OID 16516)
-- Name: customizations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.customizations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3856 (class 0 OID 0)
-- Dependencies: 241
-- Name: customizations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.customizations_id_seq OWNED BY public.customizations.id;


--
-- TOC entry 240 (class 1259 OID 16508)
-- Name: dailyschedule; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dailyschedule (
    hour_1 integer NOT NULL,
    hour_2 integer NOT NULL,
    hour_3 integer NOT NULL,
    hour_4 integer NOT NULL,
    hour_5 integer NOT NULL,
    hour_6 integer NOT NULL,
    hour_7 integer NOT NULL,
    hour_8 integer NOT NULL,
    hour_9 integer NOT NULL,
    hour_10 integer NOT NULL,
    hour_11 integer NOT NULL,
    hour_12 integer NOT NULL,
    hour_13 integer NOT NULL,
    hour_14 integer NOT NULL,
    hour_15 integer NOT NULL,
    hour_16 integer NOT NULL,
    hour_17 integer NOT NULL,
    hour_18 integer NOT NULL,
    hour_19 integer NOT NULL,
    hour_20 integer NOT NULL,
    hour_21 integer NOT NULL,
    hour_22 integer NOT NULL,
    hour_23 integer NOT NULL,
    hour_24 integer NOT NULL,
    id integer NOT NULL,
    type character varying NOT NULL,
    perfil_id integer NOT NULL,
    user_id integer
);


--
-- TOC entry 239 (class 1259 OID 16507)
-- Name: dailyschedule_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.dailyschedule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3857 (class 0 OID 0)
-- Dependencies: 239
-- Name: dailyschedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.dailyschedule_id_seq OWNED BY public.dailyschedule.id;


--
-- TOC entry 274 (class 1259 OID 16720)
-- Name: details; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.details (
    scantilon_location character varying NOT NULL,
    name_detail character varying NOT NULL,
    material_id integer NOT NULL,
    layer_thickness double precision NOT NULL,
    id integer NOT NULL,
    project_id integer,
    detail_part_id integer,
    is_deleted boolean NOT NULL,
    created_status character varying NOT NULL
);


--
-- TOC entry 273 (class 1259 OID 16719)
-- Name: details_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.details_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3858 (class 0 OID 0)
-- Dependencies: 273
-- Name: details_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.details_id_seq OWNED BY public.details.id;


--
-- TOC entry 224 (class 1259 OID 16431)
-- Name: details_part; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.details_part (
    name_detail character varying,
    info jsonb,
    id integer NOT NULL,
    project_id integer,
    type character varying NOT NULL,
    value_u double precision,
    calculations jsonb,
    created_status character varying NOT NULL,
    code_ifc character varying
);


--
-- TOC entry 223 (class 1259 OID 16430)
-- Name: details_part_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.details_part_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3859 (class 0 OID 0)
-- Dependencies: 223
-- Name: details_part_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.details_part_id_seq OWNED BY public.details_part.id;


--
-- TOC entry 296 (class 1259 OID 16873)
-- Name: divisions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.divisions (
    division character varying NOT NULL,
    a double precision NOT NULL,
    b double precision NOT NULL,
    d double precision NOT NULL,
    id integer NOT NULL,
    orientation_id integer,
    is_deleted boolean NOT NULL,
    num_orientation integer
);


--
-- TOC entry 295 (class 1259 OID 16872)
-- Name: divisions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.divisions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3860 (class 0 OID 0)
-- Dependencies: 295
-- Name: divisions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.divisions_id_seq OWNED BY public.divisions.id;


--
-- TOC entry 278 (class 1259 OID 16748)
-- Name: doors; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.doors (
    door_id integer NOT NULL,
    characteristics character varying NOT NULL,
    angulo_azimut character varying NOT NULL,
    high double precision NOT NULL,
    broad double precision NOT NULL,
    id integer NOT NULL,
    enclosure_id integer,
    orientation character varying NOT NULL,
    is_base boolean DEFAULT false,
    original_id integer
);


--
-- TOC entry 277 (class 1259 OID 16747)
-- Name: doors_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.doors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3861 (class 0 OID 0)
-- Dependencies: 277
-- Name: doors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.doors_id_seq OWNED BY public.doors.id;


--
-- TOC entry 260 (class 1259 OID 16614)
-- Name: elements; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.elements (
    name_element character varying NOT NULL,
    type character varying NOT NULL,
    atributs jsonb,
    u_marco double precision NOT NULL,
    fm double precision NOT NULL,
    id integer NOT NULL,
    user_id integer,
    created_status character varying NOT NULL,
    is_deleted boolean NOT NULL,
    calculations jsonb,
    code_ifc character varying
);


--
-- TOC entry 259 (class 1259 OID 16613)
-- Name: elements_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.elements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3862 (class 0 OID 0)
-- Dependencies: 259
-- Name: elements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.elements_id_seq OWNED BY public.elements.id;


--
-- TOC entry 228 (class 1259 OID 16449)
-- Name: enclosures; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.enclosures (
    name character varying NOT NULL,
    id integer NOT NULL,
    user_id integer,
    original_id integer,
    code character varying NOT NULL,
    created_status character varying NOT NULL,
    is_deleted boolean NOT NULL,
    code_ifc character varying
);


--
-- TOC entry 272 (class 1259 OID 16701)
-- Name: enclosures_generals; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.enclosures_generals (
    name_enclosure character varying NOT NULL,
    occupation_profile_id integer,
    height double precision NOT NULL,
    co2_sensor character varying NOT NULL,
    level_id integer,
    id integer NOT NULL,
    project_id integer,
    is_deleted boolean,
    is_base boolean DEFAULT false,
    original_enclosure_id integer
);


--
-- TOC entry 271 (class 1259 OID 16700)
-- Name: enclosures_generals_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.enclosures_generals_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3863 (class 0 OID 0)
-- Dependencies: 271
-- Name: enclosures_generals_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.enclosures_generals_id_seq OWNED BY public.enclosures_generals.id;


--
-- TOC entry 227 (class 1259 OID 16448)
-- Name: enclosures_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.enclosures_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3864 (class 0 OID 0)
-- Dependencies: 227
-- Name: enclosures_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.enclosures_id_seq OWNED BY public.enclosures.id;


--
-- TOC entry 248 (class 1259 OID 16544)
-- Name: energy_data; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.energy_data (
    id integer NOT NULL,
    type character varying NOT NULL,
    name character varying NOT NULL,
    value double precision NOT NULL
);


--
-- TOC entry 247 (class 1259 OID 16543)
-- Name: energy_data_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.energy_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3865 (class 0 OID 0)
-- Dependencies: 247
-- Name: energy_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.energy_data_id_seq OWNED BY public.energy_data.id;


--
-- TOC entry 230 (class 1259 OID 16463)
-- Name: favs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.favs (
    fav1 jsonb,
    fav2_izq jsonb,
    fav2_der jsonb,
    fav3 jsonb,
    id integer NOT NULL,
    item_id integer NOT NULL,
    type character varying NOT NULL
);


--
-- TOC entry 229 (class 1259 OID 16462)
-- Name: favs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.favs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3866 (class 0 OID 0)
-- Dependencies: 229
-- Name: favs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.favs_id_seq OWNED BY public.favs.id;


--
-- TOC entry 294 (class 1259 OID 16859)
-- Name: floorpo; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.floorpo (
    id integer NOT NULL,
    enclosure_id integer,
    floor_id integer,
    nombre character varying NOT NULL,
    longitud_pt double precision,
    categoria character varying NOT NULL,
    categoria_1 character varying NOT NULL,
    categoria_2 character varying,
    posicion_aislamiento character varying,
    e_aislamiento_1 double precision,
    e_aislamiento_2 double precision,
    codigo_pt character varying,
    pt double precision,
    pt_lineal double precision,
    espacio_contiguo character varying
);


--
-- TOC entry 293 (class 1259 OID 16858)
-- Name: floorpo_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.floorpo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3867 (class 0 OID 0)
-- Dependencies: 293
-- Name: floorpo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.floorpo_id_seq OWNED BY public.floorpo.id;


--
-- TOC entry 280 (class 1259 OID 16762)
-- Name: floors; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.floors (
    floor_id integer NOT NULL,
    characteristic character varying NOT NULL,
    area double precision NOT NULL,
    parameter double precision,
    is_ventilated character varying,
    id integer NOT NULL,
    enclosure_id integer,
    u double precision NOT NULL,
    po6_l double precision NOT NULL,
    is_base boolean DEFAULT false,
    original_id integer
);


--
-- TOC entry 279 (class 1259 OID 16761)
-- Name: floors_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.floors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3868 (class 0 OID 0)
-- Dependencies: 279
-- Name: floors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.floors_id_seq OWNED BY public.floors.id;


--
-- TOC entry 270 (class 1259 OID 16687)
-- Name: formulas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.formulas (
    id integer NOT NULL,
    project_id integer,
    item_id integer NOT NULL,
    type character varying NOT NULL,
    name character varying NOT NULL,
    atributs jsonb,
    is_deleted boolean NOT NULL
);


--
-- TOC entry 269 (class 1259 OID 16686)
-- Name: formulas_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.formulas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3869 (class 0 OID 0)
-- Dependencies: 269
-- Name: formulas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.formulas_id_seq OWNED BY public.formulas.id;


--
-- TOC entry 266 (class 1259 OID 16656)
-- Name: heating_config; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.heating_config (
    id integer NOT NULL,
    project_id integer NOT NULL,
    combustible_codigo character varying NOT NULL,
    combustible_valor double precision NOT NULL,
    rendimiento_codigo character varying,
    rendimiento_valor double precision,
    caldera_codigo character varying,
    caldera_valor double precision,
    distribucion_codigo character varying,
    distribucion_valor double precision,
    control_codigo character varying,
    control_valor double precision
);


--
-- TOC entry 265 (class 1259 OID 16655)
-- Name: heating_config_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.heating_config_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3870 (class 0 OID 0)
-- Dependencies: 265
-- Name: heating_config_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.heating_config_id_seq OWNED BY public.heating_config.id;


--
-- TOC entry 250 (class 1259 OID 16553)
-- Name: indicadores_finales; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.indicadores_finales (
    data jsonb,
    id integer NOT NULL,
    project_id integer,
    type character varying NOT NULL
);


--
-- TOC entry 249 (class 1259 OID 16552)
-- Name: indicadores_finales_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.indicadores_finales_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3871 (class 0 OID 0)
-- Dependencies: 249
-- Name: indicadores_finales_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.indicadores_finales_id_seq OWNED BY public.indicadores_finales.id;


--
-- TOC entry 246 (class 1259 OID 16535)
-- Name: levels; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.levels (
    id integer NOT NULL,
    name character varying,
    description character varying
);


--
-- TOC entry 245 (class 1259 OID 16534)
-- Name: levels_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.levels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3872 (class 0 OID 0)
-- Dependencies: 245
-- Name: levels_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.levels_id_seq OWNED BY public.levels.id;


--
-- TOC entry 286 (class 1259 OID 16804)
-- Name: orientations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.orientations (
    azimut character varying NOT NULL,
    id integer NOT NULL,
    enclosure_id integer,
    orientation character varying NOT NULL,
    is_deleted boolean NOT NULL
);


--
-- TOC entry 285 (class 1259 OID 16803)
-- Name: orientations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.orientations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3873 (class 0 OID 0)
-- Dependencies: 285
-- Name: orientations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.orientations_id_seq OWNED BY public.orientations.id;


--
-- TOC entry 254 (class 1259 OID 16571)
-- Name: personal_access_token; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.personal_access_token (
    id integer NOT NULL,
    user_id integer NOT NULL,
    token character varying NOT NULL,
    token_type character varying NOT NULL,
    in_used boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    expires_at timestamp without time zone NOT NULL
);


--
-- TOC entry 253 (class 1259 OID 16570)
-- Name: personal_access_token_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.personal_access_token_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3874 (class 0 OID 0)
-- Dependencies: 253
-- Name: personal_access_token_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.personal_access_token_id_seq OWNED BY public.personal_access_token.id;


--
-- TOC entry 256 (class 1259 OID 16585)
-- Name: projects; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.projects (
    country character varying,
    divisions jsonb,
    name_project character varying NOT NULL,
    owner_name character varying NOT NULL,
    owner_lastname character varying NOT NULL,
    project_metadata jsonb,
    residential_type character varying,
    building_type character varying NOT NULL,
    main_use_type character varying NOT NULL,
    number_levels integer NOT NULL,
    number_homes_per_level integer NOT NULL,
    built_surface double precision NOT NULL,
    latitude double precision NOT NULL,
    longitude double precision NOT NULL,
    status character varying NOT NULL,
    id integer NOT NULL,
    user_id integer NOT NULL,
    is_deleted boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    are_files_processed boolean,
    building_name character varying
);


--
-- TOC entry 255 (class 1259 OID 16584)
-- Name: projects_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.projects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3875 (class 0 OID 0)
-- Dependencies: 255
-- Name: projects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.projects_id_seq OWNED BY public.projects.id;


--
-- TOC entry 234 (class 1259 OID 16485)
-- Name: pt_table; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pt_table (
    id integer NOT NULL,
    enclosure_id integer,
    "P01" double precision NOT NULL,
    "P02" double precision NOT NULL,
    "P03" double precision NOT NULL,
    "P04" double precision NOT NULL,
    "P05" double precision NOT NULL,
    "P06" double precision NOT NULL,
    total_pt double precision NOT NULL,
    pt_piso_prop double precision NOT NULL,
    pt_piso_base double precision NOT NULL,
    "case" character varying(50) NOT NULL
);


--
-- TOC entry 233 (class 1259 OID 16484)
-- Name: pt_table_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.pt_table_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3876 (class 0 OID 0)
-- Dependencies: 233
-- Name: pt_table_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.pt_table_id_seq OWNED BY public.pt_table.id;


--
-- TOC entry 244 (class 1259 OID 16526)
-- Name: regiones; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.regiones (
    id integer NOT NULL,
    nombre_region character varying NOT NULL
);


--
-- TOC entry 243 (class 1259 OID 16525)
-- Name: regiones_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.regiones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3877 (class 0 OID 0)
-- Dependencies: 243
-- Name: regiones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.regiones_id_seq OWNED BY public.regiones.id;


--
-- TOC entry 252 (class 1259 OID 16562)
-- Name: resultados_por_recinto; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.resultados_por_recinto (
    recinto character varying NOT NULL,
    perfil_uso character varying NOT NULL,
    superficie double precision NOT NULL,
    categorias jsonb,
    id integer NOT NULL,
    enclosure_id integer,
    perfil_id integer,
    project_id integer,
    type character varying NOT NULL
);


--
-- TOC entry 251 (class 1259 OID 16561)
-- Name: resultados_por_recinto_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.resultados_por_recinto_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3878 (class 0 OID 0)
-- Dependencies: 251
-- Name: resultados_por_recinto_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.resultados_por_recinto_id_seq OWNED BY public.resultados_por_recinto.id;


--
-- TOC entry 282 (class 1259 OID 16776)
-- Name: roofs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.roofs (
    roof_id integer NOT NULL,
    characteristic character varying NOT NULL,
    area double precision NOT NULL,
    id integer NOT NULL,
    enclosure_id integer,
    u double precision NOT NULL,
    is_base boolean DEFAULT false,
    original_id integer
);


--
-- TOC entry 281 (class 1259 OID 16775)
-- Name: roofs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.roofs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3879 (class 0 OID 0)
-- Dependencies: 281
-- Name: roofs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.roofs_id_seq OWNED BY public.roofs.id;


--
-- TOC entry 226 (class 1259 OID 16440)
-- Name: tabla_py; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tabla_py (
    id integer NOT NULL,
    enclosure_id integer NOT NULL,
    item_id integer,
    name character varying NOT NULL,
    type character varying NOT NULL,
    orientation character varying NOT NULL,
    nodos_emisividad double precision NOT NULL,
    nodos_area double precision NOT NULL,
    r_puro double precision NOT NULL,
    emisividad_x_sup double precision NOT NULL,
    r_a_atot double precision NOT NULL
);


--
-- TOC entry 225 (class 1259 OID 16439)
-- Name: tabla_py_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tabla_py_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3880 (class 0 OID 0)
-- Dependencies: 225
-- Name: tabla_py_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tabla_py_id_seq OWNED BY public.tabla_py.id;


--
-- TOC entry 232 (class 1259 OID 16473)
-- Name: thermal_bridges; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.thermal_bridges (
    id integer NOT NULL,
    code_pt character varying NOT NULL,
    type_pt character varying NOT NULL,
    element_1 character varying NOT NULL,
    element_2 character varying NOT NULL,
    position_insulation character varying NOT NULL,
    insulation_thickness double precision NOT NULL,
    return_insulation jsonb,
    position_window jsonb,
    value_pt double precision NOT NULL
);


--
-- TOC entry 231 (class 1259 OID 16472)
-- Name: thermal_bridges_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.thermal_bridges_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3881 (class 0 OID 0)
-- Dependencies: 231
-- Name: thermal_bridges_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.thermal_bridges_id_seq OWNED BY public.thermal_bridges.id;


--
-- TOC entry 288 (class 1259 OID 16818)
-- Name: thermals_bridges_walls; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.thermals_bridges_walls (
    po1_length double precision,
    po1_id_element integer,
    po2_length double precision,
    po2_id_element integer,
    po3_length double precision,
    po3_id_element integer,
    po4_length double precision,
    po4_e_aislacion double precision,
    po4_id_element integer,
    id integer NOT NULL,
    wall_id integer,
    enclosure_id integer
);


--
-- TOC entry 287 (class 1259 OID 16817)
-- Name: thermals_bridges_walls_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.thermals_bridges_walls_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3882 (class 0 OID 0)
-- Dependencies: 287
-- Name: thermals_bridges_walls_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.thermals_bridges_walls_id_seq OWNED BY public.thermals_bridges_walls.id;


--
-- TOC entry 218 (class 1259 OID 16400)
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    name character varying NOT NULL,
    lastname character varying NOT NULL,
    email character varying NOT NULL,
    number_phone character varying NOT NULL,
    birthdate date,
    country character varying NOT NULL,
    ubigeo character varying,
    proffesion character varying,
    direccion character varying,
    id integer NOT NULL,
    password character varying NOT NULL,
    active boolean NOT NULL,
    is_deleted boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    role_id integer NOT NULL,
    last_activity timestamp without time zone
);


--
-- TOC entry 217 (class 1259 OID 16399)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3883 (class 0 OID 0)
-- Dependencies: 217
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 290 (class 1259 OID 16830)
-- Name: wallpo; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.wallpo (
    id integer NOT NULL,
    enclosure_id integer,
    wall_id integer,
    tipo_muro character varying NOT NULL,
    nombre character varying NOT NULL,
    orientacion character varying NOT NULL,
    longitud_pt double precision,
    categoria_1 character varying NOT NULL,
    categoria_2 character varying,
    posicion_aislamiento_1 character varying,
    posicion_aislamiento_2 character varying,
    e_aislamient0_1 double precision,
    e_aislamiento_2 double precision,
    codigo_pt character varying,
    pt double precision,
    pt_lineal double precision,
    espacio_contiguo character varying
);


--
-- TOC entry 289 (class 1259 OID 16829)
-- Name: wallpo_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.wallpo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3884 (class 0 OID 0)
-- Dependencies: 289
-- Name: wallpo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.wallpo_id_seq OWNED BY public.wallpo.id;


--
-- TOC entry 276 (class 1259 OID 16734)
-- Name: walls; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.walls (
    wall_id integer NOT NULL,
    characteristics character varying NOT NULL,
    angulo_azimut character varying NOT NULL,
    area double precision NOT NULL,
    id integer NOT NULL,
    enclosure_id integer,
    orientation character varying NOT NULL,
    u double precision,
    is_base boolean DEFAULT false,
    original_id integer NOT NULL
);


--
-- TOC entry 275 (class 1259 OID 16733)
-- Name: walls_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.walls_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3885 (class 0 OID 0)
-- Dependencies: 275
-- Name: walls_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.walls_id_seq OWNED BY public.walls.id;


--
-- TOC entry 220 (class 1259 OID 16409)
-- Name: weather_metadata; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.weather_metadata (
    id integer NOT NULL,
    name character varying NOT NULL,
    location character varying NOT NULL,
    version integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    content_hash character varying NOT NULL,
    country character varying NOT NULL,
    city character varying NOT NULL,
    district character varying NOT NULL,
    extension character varying NOT NULL,
    file_size integer NOT NULL,
    zone character varying,
    complementary character varying
);


--
-- TOC entry 219 (class 1259 OID 16408)
-- Name: weather_metadata_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.weather_metadata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3886 (class 0 OID 0)
-- Dependencies: 219
-- Name: weather_metadata_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.weather_metadata_id_seq OWNED BY public.weather_metadata.id;


--
-- TOC entry 292 (class 1259 OID 16845)
-- Name: windowpo; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.windowpo (
    id integer NOT NULL,
    enclosure_id integer,
    window_id integer,
    tipo character varying NOT NULL,
    hosted_in character varying NOT NULL,
    orientacion character varying NOT NULL,
    altura double precision NOT NULL,
    ancho double precision NOT NULL,
    categoria_muro character varying NOT NULL,
    categoria_ventana character varying NOT NULL,
    posicion_aislamiento character varying,
    e_aislamient0_1 double precision,
    e_aislamiento_2 double precision,
    retorno character varying,
    posicion_vidrio character varying,
    codigo_pt character varying,
    pt double precision,
    pt_lineal double precision,
    espacio_contiguo character varying
);


--
-- TOC entry 291 (class 1259 OID 16844)
-- Name: windowpo_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.windowpo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3887 (class 0 OID 0)
-- Dependencies: 291
-- Name: windowpo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.windowpo_id_seq OWNED BY public.windowpo.id;


--
-- TOC entry 284 (class 1259 OID 16790)
-- Name: windows; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.windows (
    window_id integer NOT NULL,
    characteristics character varying NOT NULL,
    angulo_azimut character varying NOT NULL,
    housed_in integer NOT NULL,
    "position" character varying NOT NULL,
    with_no_return character varying NOT NULL,
    high double precision NOT NULL,
    broad double precision NOT NULL,
    id integer NOT NULL,
    enclosure_id integer,
    orientation character varying NOT NULL,
    is_base boolean DEFAULT false,
    original_id integer,
    clousure_type character varying NOT NULL,
    frame character varying NOT NULL
);


--
-- TOC entry 283 (class 1259 OID 16789)
-- Name: windows_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.windows_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3888 (class 0 OID 0)
-- Dependencies: 283
-- Name: windows_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.windows_id_seq OWNED BY public.windows.id;


--
-- TOC entry 3464 (class 2604 OID 16394)
-- Name: agua_caliente id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agua_caliente ALTER COLUMN id SET DEFAULT nextval('public.agua_caliente_id_seq'::regclass);


--
-- TOC entry 3487 (class 2604 OID 16631)
-- Name: building_conditions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.building_conditions ALTER COLUMN id SET DEFAULT nextval('public.building_conditions_id_seq'::regclass);


--
-- TOC entry 3474 (class 2604 OID 16495)
-- Name: calculate_piso id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.calculate_piso ALTER COLUMN id SET DEFAULT nextval('public.calculate_piso_id_seq'::regclass);


--
-- TOC entry 3490 (class 2604 OID 16675)
-- Name: calculation_results id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.calculation_results ALTER COLUMN id SET DEFAULT nextval('public.calculation_results_id_seq'::regclass);


--
-- TOC entry 3467 (class 2604 OID 16421)
-- Name: calculations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.calculations ALTER COLUMN id SET DEFAULT nextval('public.calculations_id_seq'::regclass);


--
-- TOC entry 3475 (class 2604 OID 16502)
-- Name: casobase id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.casobase ALTER COLUMN id SET DEFAULT nextval('public.casobase_id_seq'::regclass);


--
-- TOC entry 3488 (class 2604 OID 16645)
-- Name: comunas id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comunas ALTER COLUMN id SET DEFAULT nextval('public.comunas_id_seq'::regclass);


--
-- TOC entry 3485 (class 2604 OID 16602)
-- Name: constants id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.constants ALTER COLUMN id SET DEFAULT nextval('public.constants_id_seq'::regclass);


--
-- TOC entry 3477 (class 2604 OID 16520)
-- Name: customizations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customizations ALTER COLUMN id SET DEFAULT nextval('public.customizations_id_seq'::regclass);


--
-- TOC entry 3476 (class 2604 OID 16511)
-- Name: dailyschedule id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dailyschedule ALTER COLUMN id SET DEFAULT nextval('public.dailyschedule_id_seq'::regclass);


--
-- TOC entry 3494 (class 2604 OID 16723)
-- Name: details id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.details ALTER COLUMN id SET DEFAULT nextval('public.details_id_seq'::regclass);


--
-- TOC entry 3468 (class 2604 OID 16434)
-- Name: details_part id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.details_part ALTER COLUMN id SET DEFAULT nextval('public.details_part_id_seq'::regclass);


--
-- TOC entry 3505 (class 2604 OID 16876)
-- Name: divisions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.divisions ALTER COLUMN id SET DEFAULT nextval('public.divisions_id_seq'::regclass);


--
-- TOC entry 3496 (class 2604 OID 16751)
-- Name: doors id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.doors ALTER COLUMN id SET DEFAULT nextval('public.doors_id_seq'::regclass);


--
-- TOC entry 3486 (class 2604 OID 16617)
-- Name: elements id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.elements ALTER COLUMN id SET DEFAULT nextval('public.elements_id_seq'::regclass);


--
-- TOC entry 3470 (class 2604 OID 16452)
-- Name: enclosures id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.enclosures ALTER COLUMN id SET DEFAULT nextval('public.enclosures_id_seq'::regclass);


--
-- TOC entry 3493 (class 2604 OID 16704)
-- Name: enclosures_generals id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.enclosures_generals ALTER COLUMN id SET DEFAULT nextval('public.enclosures_generals_id_seq'::regclass);


--
-- TOC entry 3480 (class 2604 OID 16547)
-- Name: energy_data id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.energy_data ALTER COLUMN id SET DEFAULT nextval('public.energy_data_id_seq'::regclass);


--
-- TOC entry 3471 (class 2604 OID 16466)
-- Name: favs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.favs ALTER COLUMN id SET DEFAULT nextval('public.favs_id_seq'::regclass);


--
-- TOC entry 3504 (class 2604 OID 16862)
-- Name: floorpo id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.floorpo ALTER COLUMN id SET DEFAULT nextval('public.floorpo_id_seq'::regclass);


--
-- TOC entry 3497 (class 2604 OID 16765)
-- Name: floors id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.floors ALTER COLUMN id SET DEFAULT nextval('public.floors_id_seq'::regclass);


--
-- TOC entry 3492 (class 2604 OID 16690)
-- Name: formulas id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.formulas ALTER COLUMN id SET DEFAULT nextval('public.formulas_id_seq'::regclass);


--
-- TOC entry 3489 (class 2604 OID 16659)
-- Name: heating_config id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.heating_config ALTER COLUMN id SET DEFAULT nextval('public.heating_config_id_seq'::regclass);


--
-- TOC entry 3481 (class 2604 OID 16556)
-- Name: indicadores_finales id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.indicadores_finales ALTER COLUMN id SET DEFAULT nextval('public.indicadores_finales_id_seq'::regclass);


--
-- TOC entry 3479 (class 2604 OID 16538)
-- Name: levels id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.levels ALTER COLUMN id SET DEFAULT nextval('public.levels_id_seq'::regclass);


--
-- TOC entry 3500 (class 2604 OID 16807)
-- Name: orientations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orientations ALTER COLUMN id SET DEFAULT nextval('public.orientations_id_seq'::regclass);


--
-- TOC entry 3483 (class 2604 OID 16574)
-- Name: personal_access_token id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personal_access_token ALTER COLUMN id SET DEFAULT nextval('public.personal_access_token_id_seq'::regclass);


--
-- TOC entry 3484 (class 2604 OID 16588)
-- Name: projects id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects ALTER COLUMN id SET DEFAULT nextval('public.projects_id_seq'::regclass);


--
-- TOC entry 3473 (class 2604 OID 16488)
-- Name: pt_table id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pt_table ALTER COLUMN id SET DEFAULT nextval('public.pt_table_id_seq'::regclass);


--
-- TOC entry 3478 (class 2604 OID 16529)
-- Name: regiones id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.regiones ALTER COLUMN id SET DEFAULT nextval('public.regiones_id_seq'::regclass);


--
-- TOC entry 3482 (class 2604 OID 16565)
-- Name: resultados_por_recinto id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.resultados_por_recinto ALTER COLUMN id SET DEFAULT nextval('public.resultados_por_recinto_id_seq'::regclass);


--
-- TOC entry 3498 (class 2604 OID 16779)
-- Name: roofs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roofs ALTER COLUMN id SET DEFAULT nextval('public.roofs_id_seq'::regclass);


--
-- TOC entry 3469 (class 2604 OID 16443)
-- Name: tabla_py id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tabla_py ALTER COLUMN id SET DEFAULT nextval('public.tabla_py_id_seq'::regclass);


--
-- TOC entry 3472 (class 2604 OID 16479)
-- Name: thermal_bridges id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.thermal_bridges ALTER COLUMN id SET DEFAULT nextval('public.thermal_bridges_id_seq'::regclass);


--
-- TOC entry 3501 (class 2604 OID 16821)
-- Name: thermals_bridges_walls id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.thermals_bridges_walls ALTER COLUMN id SET DEFAULT nextval('public.thermals_bridges_walls_id_seq'::regclass);


--
-- TOC entry 3465 (class 2604 OID 16403)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 3502 (class 2604 OID 16833)
-- Name: wallpo id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wallpo ALTER COLUMN id SET DEFAULT nextval('public.wallpo_id_seq'::regclass);


--
-- TOC entry 3495 (class 2604 OID 16737)
-- Name: walls id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.walls ALTER COLUMN id SET DEFAULT nextval('public.walls_id_seq'::regclass);


--
-- TOC entry 3466 (class 2604 OID 16412)
-- Name: weather_metadata id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.weather_metadata ALTER COLUMN id SET DEFAULT nextval('public.weather_metadata_id_seq'::regclass);


--
-- TOC entry 3503 (class 2604 OID 16848)
-- Name: windowpo id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.windowpo ALTER COLUMN id SET DEFAULT nextval('public.windowpo_id_seq'::regclass);


--
-- TOC entry 3499 (class 2604 OID 16793)
-- Name: windows id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.windows ALTER COLUMN id SET DEFAULT nextval('public.windows_id_seq'::regclass);


--
-- TOC entry 3762 (class 0 OID 16391)
-- Dependencies: 216
-- Data for Name: agua_caliente; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.agua_caliente (t_acs, demanda_acs, combustible, rendimiento, sist_distribucion, sis_control, consumo_acs, consumo_energia_primaria, energia_primaria, data, id, project_id) FROM stdin;
\.


--
-- TOC entry 3760 (class 0 OID 16385)
-- Dependencies: 214
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
\.


--
-- TOC entry 3808 (class 0 OID 16628)
-- Dependencies: 262
-- Data for Name: building_conditions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.building_conditions (type, attributes, id, enclosure_id, created_status) FROM stdin;
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	1	1	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 12, "potencia_propuesta": 12.0}	2	1	default
internal_loads	{"equipos": 0.0, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 4.0, "calor_latente": 164.0, "calor_sensible": 164.0}	3	1	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	4	1	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA3", "r_pers": 5.277777777777778, "ocupacion": "Sedentario"}}	5	2	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 15, "potencia_propuesta": 15.0}	6	2	default
internal_loads	{"equipos": 0.0, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 0.5, "calor_latente": 82.0, "calor_sensible": 82.0}	7	2	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	8	2	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	9	3	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 10, "potencia_propuesta": 10.0}	10	3	default
internal_loads	{"equipos": 0.0, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 0.0, "calor_latente": 0.0, "calor_sensible": 0.0}	11	3	default
schedule_weather	{"recinto": {"climatizado": "No", "desfase_clima": 0.0}}	12	3	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	13	4	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 10, "potencia_propuesta": 10.0}	14	4	default
internal_loads	{"equipos": 1.453, "horario": {"laboral": {"fin": 24, "inicio": 1}, "funcionamiento_semanal": "7x0"}, "usuarios": 0.0, "calor_latente": 0.0, "calor_sensible": 0.0}	15	4	default
schedule_weather	{"recinto": {"climatizado": "No", "desfase_clima": 0.0}}	16	4	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	17	5	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 15, "potencia_propuesta": 15.0}	18	5	default
internal_loads	{"equipos": 50.0, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 10.0, "calor_latente": 147.6, "calor_sensible": 147.6}	19	5	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	20	5	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	21	6	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 10, "potencia_propuesta": 10.0}	22	6	default
internal_loads	{"equipos": 0.0, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 0.91, "calor_latente": 131.2, "calor_sensible": 131.2}	23	6	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	24	6	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	25	7	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 11, "potencia_propuesta": 11.0}	26	7	default
internal_loads	{"equipos": 0.0, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 4.0, "calor_latente": 0.0, "calor_sensible": 0.0}	27	7	default
schedule_weather	{"recinto": {"climatizado": "No", "desfase_clima": 0.0}}	28	7	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	29	8	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 12, "potencia_propuesta": 12.0}	30	8	default
internal_loads	{"equipos": 15.3, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 10.0, "calor_latente": 82.0, "calor_sensible": 82.0}	31	8	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	32	8	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	33	9	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 14, "potencia_propuesta": 14.0}	34	9	default
internal_loads	{"equipos": 0.0, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 4.0, "calor_latente": 131.2, "calor_sensible": 131.2}	35	9	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	36	9	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	37	10	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 14, "potencia_propuesta": 14.0}	38	10	default
internal_loads	{"equipos": 15.3, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 0.8, "calor_latente": 82.0, "calor_sensible": 82.0}	39	10	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	40	10	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	41	11	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 13, "potencia_propuesta": 13.0}	42	11	default
internal_loads	{"equipos": 1.4, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 4.0, "calor_latente": 131.2, "calor_sensible": 131.2}	43	11	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	44	11	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	45	12	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 12, "potencia_propuesta": 12.0}	46	12	default
internal_loads	{"equipos": 1.4, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 1.5, "calor_latente": 131.2, "calor_sensible": 131.2}	47	12	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	48	12	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	49	13	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 13, "potencia_propuesta": 13.0}	50	13	default
internal_loads	{"equipos": 1.4, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 4.0, "calor_latente": 131.2, "calor_sensible": 131.2}	51	13	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	52	13	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	53	14	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 15, "potencia_propuesta": 15.0}	54	14	default
internal_loads	{"equipos": 0.0, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 2.5, "calor_latente": 82.0, "calor_sensible": 82.0}	55	14	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	56	14	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	57	15	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 15, "potencia_propuesta": 15.0}	58	15	default
internal_loads	{"equipos": 0.0, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 1.1, "calor_latente": 82.0, "calor_sensible": 82.0}	59	15	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	60	15	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	61	16	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 15, "potencia_propuesta": 15.0}	62	16	default
internal_loads	{"equipos": 0.0, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 1.1, "calor_latente": 82.0, "calor_sensible": 82.0}	63	16	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	64	16	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	65	17	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 15, "potencia_propuesta": 15.0}	66	17	default
internal_loads	{"equipos": 0.0, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 1.1, "calor_latente": 82.0, "calor_sensible": 82.0}	67	17	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	68	17	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	69	18	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 15, "potencia_propuesta": 15.0}	70	18	default
internal_loads	{"equipos": 0.0, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 2.0, "calor_latente": 82.0, "calor_sensible": 82.0}	71	18	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	72	18	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	73	19	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 15, "potencia_propuesta": 15.0}	74	19	default
internal_loads	{"equipos": 0.0, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 4.0, "calor_latente": 287.0, "calor_sensible": 287.0}	75	19	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	76	19	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	77	20	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 20, "potencia_propuesta": 20.0}	78	20	default
internal_loads	{"equipos": 73.3, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 1.5, "calor_latente": 131.2, "calor_sensible": 131.2}	79	20	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	80	20	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	81	21	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 13, "potencia_propuesta": 13.0}	82	21	default
internal_loads	{"equipos": 2.8, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 2.0, "calor_latente": 82.0, "calor_sensible": 82.0}	83	21	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	84	21	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	85	22	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 13, "potencia_propuesta": 13.0}	86	22	default
internal_loads	{"equipos": 0.0, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 0.91, "calor_latente": 82.0, "calor_sensible": 82.0}	87	22	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	88	22	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	89	23	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 13, "potencia_propuesta": 13.0}	90	23	default
internal_loads	{"equipos": 49.5, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 15.0, "calor_latente": 147.6, "calor_sensible": 147.6}	91	23	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	92	23	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	93	24	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 10, "potencia_propuesta": 10.0}	94	24	default
internal_loads	{"equipos": 0.0, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 1.8, "calor_latente": 82.0, "calor_sensible": 82.0}	95	24	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	96	24	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	97	25	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 12, "potencia_propuesta": 12.0}	98	25	default
internal_loads	{"equipos": 4.3, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 2.5, "calor_latente": 164.0, "calor_sensible": 164.0}	99	25	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	100	25	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	101	26	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 11, "potencia_propuesta": 11.0}	102	26	default
internal_loads	{"equipos": 15.3, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 6.0, "calor_latente": 131.2, "calor_sensible": 131.2}	103	26	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	104	26	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	105	27	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 8, "potencia_propuesta": 8.0}	106	27	default
internal_loads	{"equipos": 0.0, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 8.0, "calor_latente": 82.0, "calor_sensible": 82.0}	107	27	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	108	27	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	109	28	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 12, "potencia_propuesta": 12.0}	110	28	default
internal_loads	{"equipos": 15.3, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 10.0, "calor_latente": 82.0, "calor_sensible": 82.0}	111	28	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	112	28	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	113	29	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 16, "potencia_propuesta": 16.0}	114	29	default
internal_loads	{"equipos": 0.0, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 20.0, "calor_latente": 131.2, "calor_sensible": 131.2}	115	29	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	116	29	default
ventilation_flows	{"infiltraciones": 0.5, "caudal_impuesto": {"vent_noct": 0}, "recuperador_calor": 0, "cauldal_min_salubridad": {"ida": "IDA2", "r_pers": 8.796296296296296, "ocupacion": "Sedentario"}}	117	30	default
lightning	{"estrategia": "Sin estrategia", "potencia_base": 9, "potencia_propuesta": 9.0}	118	30	default
internal_loads	{"equipos": 15.3, "horario": {"laboral": {"fin": 18, "inicio": 8}, "funcionamiento_semanal": "5x2"}, "usuarios": 3.0, "calor_latente": 82.0, "calor_sensible": 82.0}	119	30	default
schedule_weather	{"recinto": {"climatizado": "Si", "desfase_clima": 0.0}}	120	30	default
\.


--
-- TOC entry 3782 (class 0 OID 16492)
-- Dependencies: 236
-- Data for Name: calculate_piso; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.calculate_piso (id, enclosure_id, floor_id, b, rf, df, ufg_sog, psi, u_vert, rn_vert, dn_vert, r_vertical, d_vertical, psi_vertical, u_horiz, rn_horiz, dn_horiz, r_horiz, d_horiz, psi_horiz, psi_min, ls) FROM stdin;
\.


--
-- TOC entry 3814 (class 0 OID 16672)
-- Dependencies: 268
-- Data for Name: calculation_results; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.calculation_results (id, final_indicators, result_by_enclosure, co2_eq, created_at, project_id) FROM stdin;
\.


--
-- TOC entry 3768 (class 0 OID 16418)
-- Dependencies: 222
-- Data for Name: calculations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.calculations (id, project_id, reference_id, type, name, formula, "values") FROM stdin;
1	\N	1	details	generals	\N	{"r": 0.06134969325153375, "km_op": 220800.0, "is_wood": 0, "fourier_nodes": 2, "is_insulation": 0}
2	\N	2	details	generals	\N	{"r": 1.058139534883721, "km_op": 546.0, "is_wood": 0, "fourier_nodes": 1, "is_insulation": 1}
3	\N	3	details	generals	\N	{"r": 0.06134969325153375, "km_op": 220800.0, "is_wood": 0, "fourier_nodes": 2, "is_insulation": 0}
4	\N	4	details	generals	\N	{"r": 0.11395348837209303, "km_op": 58.800000000000004, "is_wood": 0, "fourier_nodes": 1, "is_insulation": 1}
5	\N	5	details	generals	\N	{"r": 0.06134969325153375, "km_op": 220800.0, "is_wood": 0, "fourier_nodes": 2, "is_insulation": 0}
6	\N	6	details	generals	\N	{"r": 0.22790697674418606, "km_op": 117.60000000000001, "is_wood": 0, "fourier_nodes": 1, "is_insulation": 1}
\.


--
-- TOC entry 3784 (class 0 OID 16499)
-- Dependencies: 238
-- Data for Name: casobase; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.casobase (id, enclosure_id, type, characteristic, item_id, data) FROM stdin;
\.


--
-- TOC entry 3810 (class 0 OID 16642)
-- Dependencies: 264
-- Data for Name: comunas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.comunas (id, nombre_comuna, latitud, longitud, zonas_termicas, region_id) FROM stdin;
1	Arica	-18.53753459774638	-69.97445241269746	{A,B,H}	3
2	Camarones	-18.92993146225496	-69.69852644539473	{A,B,H}	3
3	General Lagos	-17.82851683041105	-69.57476022402615	{H}	3
4	Putre	-18.42799850568514	-69.31180425930219	{H}	3
5	Alto Hospicio	-20.189940578351003	-70.01096495575666	{A}	9
6	Camiña	-19.37344699902097	-69.50534243164451	{B,H}	9
7	Colchane	-19.353108906045637	-68.847237814959	{H}	9
8	Huara	-19.59011247171401	-69.66771762026029	{A,B,H}	9
9	Iquique	-20.93962880611963	-70.04153081910614	{A}	9
10	Pica	-20.478011755075578	-68.91167547844803	{B,H}	9
11	Pozo Almonte	-20.76902193440412	-69.50455920775525	{B,H}	9
12	Antofagasta	-24.27478247551975	-69.41157884494896	{A,B,H}	2
13	Calama	-22.162155514521082	-68.6297316554502	{B,H}	2
14	María Elena	-22.08950775626198	-69.46035767511934	{B}	2
15	Mejillones	-22.936055849627163	-70.19837154215077	{A}	2
16	Ollagüe	-21.456475431084737	-68.31406177478594	{H}	2
17	San Pedro de Atacama	-23.401972012486237	-67.91114482861619	{B,H}	2
18	Sierra Gorda	-23.255732341363352	-69.30734850462602	{B}	2
19	Taltal	-25.313301019661456	-69.86520494694595	{A,B,H}	2
20	Tocopilla	-22.002303380715098	-70.01412395394598	{A}	2
21	Alto del Carmen	-28.992946879982266	-70.15302263655978	{B,H}	4
22	Caldera	-27.14111786304384	-70.68213913434063	{A}	4
23	Chañaral	-26.372533228591404	-70.33797837797506	{A}	4
24	Copiapó	-27.32047155211146	-69.8251125370947	{A,B,H}	4
25	Diego de Almagro	-26.236775631407717	-69.18606015054195	{B,H}	4
26	Freirina	-28.84349615575806	-71.1950173788641	{A}	4
27	Huasco	-28.257625027894697	-71.01721822282529	{A}	4
28	Tierra Amarilla	-27.86395570047458	-69.67105137768375	{B,H}	4
29	Vallenar	-28.593637605139968	-70.6013947788549	{B}	4
30	Andacollo	-30.25942783326121	-71.10063719213626	{B}	6
31	Canela	-31.40183464617101	-71.39438611857604	{C}	6
32	Combarbalá	-31.14645445094774	-70.96573723982593	{B,H}	6
33	Coquimbo	-30.22741586051679	-71.35898541148778	{C}	6
34	Illapel	-31.549368534719786	-70.97009328560829	{B,H}	6
35	La Higuera	-29.374776585420314	-70.90256464173225	{C,B}	6
36	La Serena	-29.789112942311693	-71.06081859548794	{C,B}	6
37	Los Vilos	-31.97794091878246	-71.30425222475364	{C}	6
38	Monte Patria	-30.834436987584343	-70.6503981253918	{B,H}	6
39	Ovalle	-30.673014022519062	-71.40531046332418	{C,B}	6
40	Paiguano	-30.23708638070552	-70.37029768178407	{B,H}	6
41	Punitaqui	-30.946100851881557	-71.33262610276823	{B}	6
42	Río Hurtado	-30.430531748053948	-70.65417478530489	{B,H}	6
43	Salamanca	-31.89316824225579	-70.66137254778269	{B,H}	6
44	Vicuña	-29.89161429070144	-70.38238451197817	{B,H}	6
45	Algarrobo	-33.32944439395213	-71.5993912699541	{C}	10
46	Cabildo	-32.417355481602556	-70.82353228572714	{D,H}	10
47	Calera	-32.79392087066913	-71.15689371808999	{D}	10
48	Calle Larga	-32.950769455254886	-70.54466016477576	{D}	10
49	Cartagena	-33.533821571332425	-71.4422066919395	{C}	10
50	Casablanca	-33.31566472783171	-71.43497442177366	{C}	10
51	Catemu	-32.70735639661835	-70.94464879121807	{D}	10
52	Concón	-32.953290963800185	-71.46775364127309	{C}	10
53	El Quisco	-33.415125075563715	-71.65132203469642	{C}	10
54	El Tabo	-33.48286670751827	-71.58108221480575	{C}	10
55	Hijuelas	-32.86933343789882	-71.08107349637899	{D}	10
56	Isla  de Pascua	-27.13020565630102	-109.33937968696007	{A}	10
57	Juan Fernández	-33.650730869722835	-78.84705588276846	{C}	10
58	La Cruz	-32.82539703597101	-71.24035408438317	{D}	10
59	La Ligua	-32.3535886474276	-71.27170234479586	{C,D}	10
60	Limache	-33.03077711167602	-71.27899257624283	{D}	10
61	Llaillay	-32.88810773444827	-70.90169683794018	{D}	10
62	Los Andes	-32.951118791830716	-70.23979469809973	{D,H}	10
63	Nogales	-32.69149504630877	-71.1761181805687	{D}	10
64	Olmué	-33.03565498949262	-71.11043573183878	{D}	10
65	Panquehue	-32.793737779981576	-70.82843277159614	{D}	10
66	Papudo	-32.474914189287276	-71.38026900149833	{C}	10
67	Petorca	-32.19050751910703	-70.86990513608158	{D,H}	10
68	Puchuncaví	-32.74530707673396	-71.38792724062122	{C}	10
69	Putaendo	-32.48100254799779	-70.52093967929514	{D,H}	10
70	Quillota	-32.90476849641397	-71.27245443341135	{D}	10
71	Quilpué	-33.14731766092229	-71.25420745220597	{D}	10
72	Quintero	-32.843137546479944	-71.4732766039996	{C}	10
73	Rinconada	-32.87633609431794	-70.70620171716186	{D}	10
74	San Antonio	-33.667154715702516	-71.48694519246843	{C}	10
75	San Esteban	-32.68652453795223	-70.34817220150725	{D,H}	10
76	San Felipe	-32.73640145998184	-70.75295842517095	{D}	10
77	Santa María	-32.686020523676305	-70.60969837303105	{D}	10
78	Santo Domingo	-33.80936145741913	-71.6764962944122	{C}	10
79	Valparaíso	-33.129733489201904	-71.57332903605067	{C}	10
80	Villa Alemana	-33.06772493556089	-71.33001179180582	{D}	10
81	Viña del Mar	-33.02860172258393	-71.51553689513399	{C}	10
82	Zapallar	-32.58748819171516	-71.3362780328979	{C}	10
83	Alhué	-34.04272683891573	-71.05644022833565	{D}	1
84	Buin	-33.748059364995314	-70.73894621762477	{D}	1
85	Calera de Tango	-33.623251927680585	-70.79023344411196	{D}	1
86	Cerrillos	-33.49976895244346	-70.71254350100259	{D}	1
87	Cerro Navia	-33.4224789084748	-70.74458864726701	{D}	1
88	Colina	-33.13489636099011	-70.6160969529145	{D,H}	1
89	Conchalí	-33.3837232152827	-70.67690788080331	{D}	1
90	Curacaví	-33.36649101754401	-71.08013360914047	{D}	1
91	El Bosque	-33.562894593449414	-70.67635644754176	{D}	1
92	El Monte	-33.66787610975949	-71.03353902853983	{D}	1
93	Estación Central	-33.46445988712399	-70.70099211560458	{D}	1
94	Huechuraba	-33.360386538436714	-70.63821166310451	{D}	1
95	Independencia	-33.41486650489307	-70.66529023071813	{D}	1
96	Isla de Maipo	-33.74872106008666	-70.94590632539429	{D}	1
97	La Cisterna	-33.53035068357205	-70.66415247091999	{D}	1
98	La Florida	-33.52842210304317	-70.53998405101369	{D}	1
99	La Granja	-33.5356526452177	-70.6227625328623	{D}	1
100	La Pintana	-33.58764078258616	-70.63724740657459	{D}	1
101	La Reina	-33.447294875129195	-70.53690255133088	{D}	1
102	Lampa	-33.27810783863964	-70.87515444032931	{D}	1
103	Las Condes	-33.421252524971294	-70.501318499671	{D}	1
104	Lo Barnechea	-33.299284043215685	-70.3686174113609	{D,H}	1
105	Lo Espejo	-33.52063065610371	-70.69001090265463	{D}	1
106	Lo Prado	-33.44709970084509	-70.72321159786469	{D}	1
107	Macul	-33.4896181144012	-70.60031259660468	{D}	1
108	Maipú	-33.50698074408871	-70.80976271459323	{D}	1
109	María Pinto	-33.498079901458915	-71.21039535060712	{D}	1
110	Melipilla	-33.74375376935222	-71.19369054916655	{D}	1
111	Ñuñoa	-33.45809636895743	-70.59913059273421	{D}	1
112	Padre Hurtado	-33.55753483161159	-70.87100449220928	{D}	1
113	Paine	-33.86370544428992	-70.7583451591476	{D}	1
114	Pedro Aguirre Cerda	-33.49174234738474	-70.6756510375525	{D}	1
115	Peñaflor	-33.61106006203999	-70.8937477331907	{D}	1
116	Peñalolén	-33.485466451999535	-70.52550086857403	{D}	1
117	Pirque	-33.71848391402861	-70.50682925266393	{D}	1
118	Providencia	-33.43185201065377	-70.61243800621321	{D}	1
119	Pudahuel	-33.42408032383749	-70.85483253283279	{D}	1
120	Puente Alto	-33.59118044693152	-70.55798408668652	{D}	1
121	Quilicura	-33.355710759886165	-70.7354210688533	{D}	1
122	Quinta Normal	-33.427831905391855	-70.70137416396038	{D}	1
123	Recoleta	-33.40579378204903	-70.63959051050793	{D}	1
124	Renca	-33.40191626508441	-70.72793136554846	{D}	1
125	San Bernardo	-33.62926774050344	-70.72417928520244	{D}	1
126	San Joaquín	-33.49623716819867	-70.62871091836242	{D}	1
127	San José de Maipo	-33.703840192447075	-70.09679286076478	{D,H}	1
128	San Miguel	-33.499286602897676	-70.65177098641837	{D}	1
129	San Pedro	-33.931775594306416	-71.45267025806318	{D}	1
130	San Ramón	-33.540648961197164	-70.64257446904033	{D}	1
131	Santiago	-33.45374764011004	-70.65695310722134	{D}	1
132	Talagante	-33.6820017976536	-70.89545330778965	{D}	1
133	Tiltil	-33.062720220475754	-70.8761845026105	{D}	1
134	Vitacura	-33.37954496291316	-70.57312848244567	{D}	1
135	Chépica	-34.791234617886516	-71.35937809477096	{D}	8
136	Chimbarongo	-34.751725471205546	-70.98090610288106	{D}	8
137	Codegua	-34.05707379355585	-70.54715166306266	{D,H}	8
138	Coinco	-34.282282924322836	-70.97111435137032	{D}	8
139	Coltauco	-34.259652428581084	-71.07747404934173	{D}	8
140	Doñihue	-34.19665283950145	-70.92338022469933	{D}	8
141	Graneros	-34.06563901208484	-70.74705580017218	{D}	8
142	La Estrella	-34.223110515787226	-71.60254774405803	{D}	8
143	Las Cabras	-34.16470091191503	-71.33277312916354	{D}	8
144	Litueche	-34.107082301841366	-71.73331151683958	{C}	8
145	Lolol	-34.768248080961484	-71.64882921234886	{D}	8
146	Machalí	-34.32040722926922	-70.31929897528637	{D,H}	8
147	Malloa	-34.47649946645413	-70.87291495182251	{D,H}	8
148	Marchihue	-34.37257519045857	-71.67176686495904	{D}	8
149	Mostazal	-33.95573860661179	-70.56880815660423	{D,H}	8
150	Nancagua	-34.66746393459454	-71.19196835769411	{D}	8
151	Navidad	-34.012499591348856	-71.8205802826935	{C}	8
152	Olivar	-34.211520365198474	-70.82068619943416	{D}	8
153	Palmilla	-34.52792545993669	-71.35291434965583	{D}	8
154	Paredones	-34.67336961949771	-71.91152806559857	{C}	8
155	Peralillo	-34.46602068995108	-71.49668450085956	{D}	8
156	Peumo	-34.32909450917592	-71.22182626177236	{D}	8
157	Pichidegua	-34.371176579003716	-71.33909362774082	{D}	8
158	Pichilemu	-34.38388850581374	-71.91069288141782	{C}	8
159	Placilla	-34.619001235253165	-71.08631467419298	{D}	8
160	Pumanque	-34.59587003495378	-71.69177526592007	{D}	8
161	Quinta de Tilcoco	-34.359225378111134	-70.99806215057994	{D}	8
162	Rancagua	-34.12575600847033	-70.81668737173622	{D}	8
163	Rengo	-34.454633616300626	-70.71895848597234	{D,H}	8
164	Requínoa	-34.33487573537386	-70.65919494258482	{D,H}	8
165	San Fernando	-34.743569241871285	-70.60336002685732	{D,H}	8
166	San Vicente	-34.477474684469	-71.12312136533971	{D}	8
167	Santa Cruz	-34.64270229157914	-71.40268753683242	{D}	8
168	Cauquenes	-35.97123977106156	-72.28049449314025	{E}	7
169	Chanco	-35.69894268872404	-72.48502482841235	{E}	7
170	Colbún	-36.07677134498843	-70.97941652722052	{D,H}	7
171	Constitución	-35.363033697041345	-72.27580115388703	{E}	7
172	Curepto	-35.129765741511264	-71.95302633102953	{E}	7
173	Curicó	-35.19911970118711	-70.89625665198072	{D,H}	7
174	Empedrado	-35.61351921458753	-72.28438231697211	{E}	7
175	Hualañé	-34.95263624937465	-71.70882461576582	{D}	7
176	Licantén	-34.97427699074269	-72.06035782539341	{C}	7
177	Linares	-35.95827777021491	-71.33257149376941	{D,H}	7
178	Longaví	-36.11044535685186	-71.44195713665697	{D,H}	7
179	Maule	-35.50830327323932	-71.71206059837922	{D}	7
180	Molina	-35.352847059212394	-70.91073849157594	{D,H}	7
181	Parral	-36.2621426453145	-71.6466283064966	{D,H}	7
182	Pelarco	-35.383078976106724	-71.35001020002888	{D}	7
183	Pelluhue	-35.91164829430687	-72.60744111884367	{E}	7
184	Pencahue	-35.32754519715075	-71.81614402850725	{D}	7
185	Rauco	-34.93772708192639	-71.42575839655288	{D}	7
186	Retiro	-36.00219865674757	-71.82995107326005	{D}	7
187	Río Claro	-35.26062606792112	-71.26886260005087	{D}	7
188	Romeral	-35.06853072570828	-70.71131533929733	{D,H}	7
189	Sagrada Familia	-35.10356519793964	-71.49564509844964	{D}	7
190	San Clemente	-35.71192932888567	-70.84922925599152	{D,H}	7
191	San Javier	-35.628822099350394	-71.92707116975222	{D}	7
192	San Rafael	-35.30151754420014	-71.50046948752764	{D}	7
193	Talca	-35.42786981235916	-71.60225243623422	{D}	7
194	Teno	-34.88813688832257	-71.02183620970047	{D,H}	7
195	Vichuquén	-34.841324982738925	-72.02252883497962	{C}	7
196	Villa Alegre	-35.68556242852364	-71.68293067891894	{D}	7
197	Yerbas Buenas	-35.68922695131253	-71.54411888571829	{D}	7
198	Bulnes	-36.790405730301025	-72.29002493991274	{F}	11
199	Chillán	-36.617488949385134	-72.12872101922865	{F}	11
200	Chillán Viejo	-36.68035156338371	-72.19880565643365	{F}	11
201	Cobquecura	-36.18087827738226	-72.72059728405414	{E}	11
202	Coelemu	-36.5049782320666	-72.7504198420792	{E}	11
203	Coihueco	-36.701921410765436	-71.58173842715247	{F,H}	11
204	El Carmen	-36.92511170757367	-71.84710815440413	{F}	11
205	Ninhue	-36.35675687744431	-72.409709090863	{F}	11
206	Ñiquén	-36.302293907070116	-71.897901364399	{F}	11
207	Pemuco	-36.983065836977865	-72.06784878654848	{F}	11
208	Pinto	-36.92129476692415	-71.50045938743361	{F,H}	11
209	Portezuelo	-36.546281144823894	-72.46663412352434	{F}	11
210	Quillón	-36.81845535464904	-72.5018019045677	{F}	11
211	Quirihue	-36.23560381414696	-72.5436531995767	{E}	11
212	Ránquil	-36.64046345337424	-72.58795787493003	{F}	11
213	San Carlos	-36.385742190721466	-72.01906168248519	{F}	11
214	San Fabián	-36.57968611301716	-71.28764018999954	{F,H}	11
215	San Ignacio	-36.822450288388325	-72.02939674730966	{F}	11
216	San Nicolás	-36.479609789140326	-72.22838620769163	{F}	11
217	Treguaco	-36.4280060269646	-72.65979081183272	{E}	11
218	Yungay	-37.104672412386165	-71.9305822628873	{F,H}	11
219	Alto Biobío	-37.86539758691785	-71.34744595828975	{F,H}	5
220	Antuco	-37.3274487946032	-71.36704821527162	{F,H}	5
221	Arauco	-37.28859333902454	-73.39980965033745	{E}	5
222	Cabrero	-37.061939199822575	-72.38135937321215	{F}	5
223	Cañete	-37.87366663542511	-73.3173008707997	{E}	5
224	Chiguayante	-36.900781615708325	-73.00518672080887	{E}	5
225	Concepción	-36.83430124140046	-72.95083237911541	{E}	5
226	Contulmo	-38.052459315578055	-73.21196169982096	{E}	5
227	Coronel	-37.00721013008728	-73.12558812024669	{E}	5
228	Curanilahue	-37.48290030427803	-73.2356502851394	{E}	5
229	Florida	-36.822304933395	-72.71779471582514	{F}	5
230	Hualpén	-36.78879001110515	-73.14118858048246	{E}	5
231	Hualqui	-37.04477148800152	-72.87103710426895	{E}	5
232	Laja	-37.31261407456831	-72.58252966452841	{F}	5
233	Lebu	-37.67677655567967	-73.58987102707314	{E}	5
234	Los Álamos	-37.673578479452395	-73.35694625433479	{E}	5
235	Los Ángeles	-37.40749362066667	-72.32743024787294	{F}	5
236	Lota	-37.11958028686684	-73.1049615082253	{E}	5
237	Mulchén	-37.83829564519093	-72.09779030151786	{F}	5
238	Nacimiento	-37.48548461436038	-72.82355117571154	{F}	5
239	Negrete	-37.6080841586098	-72.57635676445578	{F}	5
240	Penco	-36.74788236592716	-72.94374858534152	{E}	5
241	Quilaco	-37.960399120634506	-71.7056815709267	{F}	5
242	Quilleco	-37.436703144048735	-71.86154224236277	{F,H}	5
243	San Pedro de la Paz	-36.88091199135655	-73.0984759781022	{E}	5
244	San Rosendo	-37.21322903608989	-72.72125920998019	{F}	5
245	Santa Bárbara	-37.62320866629947	-71.74820205478612	{F,H}	5
246	Santa Juana	-37.27668551306626	-72.96005083074753	{E}	5
\.


--
-- TOC entry 3804 (class 0 OID 16599)
-- Dependencies: 258
-- Data for Name: constants; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.constants (atributs, name, type, id, user_id, create_status, is_deleted, code_ifc) FROM stdin;
{"name": "Hormigón Armado", "density": 2400.0, "conductivity": 1.63, "specific_heat": 920.0}	materials	definition materials	1	\N	default	f	MATERIAL_001
{"name": "P.E 10kg/m3", "density": 10.0, "conductivity": 0.043, "specific_heat": 1200.0}	materials	definition materials	2	\N	default	f	MATERIAL_002
{"name": "Tierra", "density": 1800.0, "conductivity": 2.0, "specific_heat": 3157.0}	materials	definition materials	3	\N	default	f	MATERIAL_003
{"name": "P.E 15kg/m3", "density": 15.0, "conductivity": 0.041, "specific_heat": 1200.0}	materials	definition materials	4	\N	default	f	MATERIAL_004
{"name": "P.E 20kg/m3", "density": 20.0, "conductivity": 0.0384, "specific_heat": 1200.0}	materials	definition materials	5	\N	default	f	MATERIAL_005
{"name": "P.E 25kg/m3", "density": 25.0, "conductivity": 0.037, "specific_heat": 1200.0}	materials	definition materials	6	\N	default	f	MATERIAL_006
{"name": "P.E 30kg/m3", "density": 30.0, "conductivity": 0.0361, "specific_heat": 1200.0}	materials	definition materials	7	\N	default	f	MATERIAL_007
{"name": "Lana Roca Gran 40kg/m3", "density": 40.0, "conductivity": 0.059, "specific_heat": 840.0}	materials	definition materials	8	\N	default	f	MATERIAL_008
{"name": "Lana Roca Gran 12kg/m3", "density": 12.0, "conductivity": 0.063, "specific_heat": 1050.0}	materials	definition materials	9	\N	default	f	MATERIAL_009
{"name": "Enlucido de yeso", "density": 1000.0, "conductivity": 0.44, "specific_heat": 837.0}	materials	definition materials	10	\N	default	f	MATERIAL_010
{"name": "Fibrocemento", "density": 1000.0, "conductivity": 0.23, "specific_heat": 831.0}	materials	definition materials	11	\N	default	f	MATERIAL_011
{"name": "Alb hecho a mano", "density": 1500.0, "conductivity": 0.5, "specific_heat": 750.0}	materials	definition materials	12	\N	default	f	MATERIAL_012
{"name": "Alb. Maq 1000kg/m3", "density": 1000.0, "conductivity": 0.46, "specific_heat": 750.0}	materials	definition materials	13	\N	default	f	MATERIAL_013
{"name": "Alb. Maq 1200kg/m3", "density": 1200.0, "conductivity": 0.52, "specific_heat": 750.0}	materials	definition materials	14	\N	default	f	MATERIAL_014
{"name": "Lana Min. Colch 50kg/m3", "density": 50.0, "conductivity": 0.041, "specific_heat": 840.0}	materials	definition materials	15	\N	default	f	MATERIAL_015
{"name": "Lana Min. Colch 70kg/m3", "density": 70.0, "conductivity": 0.038, "specific_heat": 840.0}	materials	definition materials	16	\N	default	f	MATERIAL_016
{"name": "Madera Aglomerado", "density": 420.0, "conductivity": 0.094, "specific_heat": 1420.0}	materials	definition materials	17	\N	default	f	MATERIAL_017
{"name": "Madera Alamo", "density": 380.0, "conductivity": 0.091, "specific_heat": 1759.0}	materials	definition materials	18	\N	default	f	MATERIAL_018
{"name": "Madera Alerce", "density": 560.0, "conductivity": 0.134, "specific_heat": 1759.0}	materials	definition materials	19	\N	default	f	MATERIAL_019
{"name": "Madera coigue", "density": 670.0, "conductivity": 0.145, "specific_heat": 1759.0}	materials	definition materials	20	\N	default	f	MATERIAL_020
{"name": "Madera lingue", "density": 640.0, "conductivity": 0.136, "specific_heat": 1759.0}	materials	definition materials	21	\N	default	f	MATERIAL_021
{"name": "Madera Pino Insigne", "density": 410.0, "conductivity": 0.104, "specific_heat": 1759.0}	materials	definition materials	22	\N	default	f	MATERIAL_022
{"name": "Madera Rauli", "density": 580.0, "conductivity": 0.121, "specific_heat": 1759.0}	materials	definition materials	23	\N	default	f	MATERIAL_023
{"name": "Madera Roble", "density": 800.0, "conductivity": 0.157, "specific_heat": 1759.0}	materials	definition materials	24	\N	default	f	MATERIAL_024
{"name": "Madera Tab. Fibra 1030kg/m3", "density": 1030.0, "conductivity": 0.28, "specific_heat": 2444.0}	materials	definition materials	25	\N	default	f	MATERIAL_025
{"name": "Madera Tab. Fibra 850kg/m3", "density": 850.0, "conductivity": 0.23, "specific_heat": 2444.0}	materials	definition materials	26	\N	default	f	MATERIAL_026
{"name": "Madera Tab. Fibra 930kg/m3", "density": 930.0, "conductivity": 0.26, "specific_heat": 2444.0}	materials	definition materials	27	\N	default	f	MATERIAL_027
{"name": "Rocas compactas", "density": 2750.0, "conductivity": 3.5, "specific_heat": 800.0}	materials	definition materials	28	\N	default	f	MATERIAL_028
{"name": "Rocas porosas", "density": 2100.0, "conductivity": 2.33, "specific_heat": 820.0}	materials	definition materials	29	\N	default	f	MATERIAL_029
{"name": "Vidrio plano", "density": 2500.0, "conductivity": 1.2, "specific_heat": 837.0}	materials	definition materials	30	\N	default	f	MATERIAL_030
{"name": "Yeso carton 700kg/m3", "density": 700.0, "conductivity": 0.26, "specific_heat": 840.0}	materials	definition materials	31	\N	default	f	MATERIAL_031
{"name": "Yeso carton 870kg/m3", "density": 870.0, "conductivity": 0.31, "specific_heat": 840.0}	materials	definition materials	32	\N	default	f	MATERIAL_032
{"Fourier": {"F_ref": 0.5, "dt_Fourier": 3600}, "is_wood": [{"name": "lambda_min_mad", "value": 0.08, "metric": "W/mK"}, {"name": "lambda_max_mad", "value": 0.08, "metric": "W/mK"}, {"name": "p_min_mad", "value": 0.08, "metric": "kg/m3"}, {"name": "p_max_mad", "value": 1200, "metric": "kg/m3"}, {"name": "Cp_min_mod", "value": 1400, "metric": "J/kgK"}, {"name": "e_min_mad", "value": 5.0, "metric": "cm"}, {"name": "km:op_max", "value": 1.5, "metric": "veces"}], "cp_limit": [{"value": 50000, "category": "EM", "represents": "Elemento de Madera"}, {"value": 75000, "category": "EL", "represents": "Elemento Liviano"}, {"value": 110000, "category": "EI", "represents": "Elemento Intermedio"}, {"value": 175000, "category": "EP", "represents": "Elemento Pesado"}, {"value": 250000, "category": "", "represents": ""}], "is_insulation": [{"name": "lambda_max_ais", "value": 0.1, "metric": "W/mK"}, {"name": "p_max_ais", "value": 250, "metric": "kg/m3"}], "surface_color": {"Claro": 0.3, "Oscuro": 0.9, "Intermedio": 0.6}, "insulation_position": {"0": "sa", "1": "ci", "2": "cm", "3": "ce"}, "scantillon_location": ["Muro", "Techo", "Piso"], "light_for_edge_layer": 0.35}	generals	details	33	\N	default	f	
{"frame_material": ["Madera Sin RPT", "PVC Sin RPT", "Metalico Sin RPT", "Madera Con RPT", "PVC Con RPT", "Metalico Con RPT", "Fierro"], "window_closure": ["Abatir", "Corredera", "Guillotina", "Proyectante", "Fila"], "thermal_resistances": {"rse_roof": 0.04, "rse_wall": 0.04, "rsi_roof": 0.09, "rsi_wall": 0.13, "rse_floor": 0.04, "rsi_floor": 0.17}}	generals	elements	34	\N	default	f	
{"idas": {"ida1": 400, "ida2": 600, "ida3": 1000, "ida4": 0}, "co2_pers": {"Colegio": 19, "Sedentario": 19, "Ejercicio Alto": 170, "Ejercicio Bajo": 50, "Ejercicio Medio": 100, "Jardin Infantil": 18}, "estrategia_iluminacion": {"Dimmer": 0.2, "Sectorizacion": 0.35, "Sin estrategia": 0, "Sensor de Luz Nat": 0.55}, "funcionamiento_semanal": {"0x7": "0 dias a la semana laboral", "1x6": "1 dias a la semana laboral", "2x5": "2 dias a la semana laboral", "3x4": "3 dias a la semana laboral", "4x3": "4 dias a la semana laboral", "5x2": "Lunes-Viernes", "6x1": "Lunes-Sabado", "7x0": "Lunes-Domingo"}}	enclosures	enclosures	35	\N	default	f	
{"orientations": [{"range_az": "0° ≤ Az < 22,5°", "azimut_360": 168.75, "orientation": "N"}, {"range_az": "22,5° ≤ Az < 45°", "azimut_360": 146.25, "orientation": "NE"}, {"range_az": "45° ≤ Az < 67,5°", "azimut_360": 123.75, "orientation": "NE"}, {"range_az": "67,5° ≤ Az < 90°", "azimut_360": 101.25, "orientation": "E"}, {"range_az": "90° ≤ Az < 112,5°", "azimut_360": 78.75, "orientation": "E"}, {"range_az": "112,5° ≤ Az < 135°", "azimut_360": 56.25, "orientation": "SE"}, {"range_az": "135° ≤ Az < 157,5°", "azimut_360": 33.75, "orientation": "SE"}, {"range_az": "157,5° ≤ Az < 180°", "azimut_360": 11.25, "orientation": "S"}, {"range_az": "-180° ≤ Az < -157,5°", "azimut_360": 348.75, "orientation": "S"}, {"range_az": "-157,5° ≤ Az < -135°", "azimut_360": 326.25, "orientation": "SO"}, {"range_az": "-135° ≤ Az < -112,5°", "azimut_360": 303.75, "orientation": "SO"}, {"range_az": "-112,5° ≤ Az < -90°", "azimut_360": 281.25, "orientation": "O"}, {"range_az": "-90° ≤ Az < -67,5°", "azimut_360": 258.75, "orientation": "O"}, {"range_az": "-67,5° ≤ Az < -45°", "azimut_360": 236.25, "orientation": "NO"}, {"range_az": "-45° ≤ Az < -22,5°", "azimut_360": 213.75, "orientation": "NO"}, {"range_az": "-22,5° ≤ Az < 0°", "azimut_360": 191.25, "orientation": "N"}, {"range_az": "0° ≤ Az < 22,5°", "azimut_360": 168.75, "orientation": "N"}]}	Azimut Table	orientation	36	\N	created	f	
{"tipo_de_ocupacion_acs": {"Albergue": 35, "Oficinas": 3, "Cuarteles": 40, "Fábricas": 30, "Gimnasios": 30, "Residencia": 60, "Vestuarios": 30, "Cafeterías": 2, "Restaurantes": 12, "Hotel 4 Estrellas": 80, "Hotel 5 Estrellas": 100, "Escuela con duchas": 30, "Escuela sin duchas": 6, "Camping/campamentos": 30, "Centro penitenciario": 40, "Hospitales y clínicas": 80, "Hotel/Hostal/Apart Hotel": 50, "Hostal/Pensión/Apart hotel": 40, "Ambulatorio y centros de salud": 60, "Hotel 3 Estrellas / Apart Hotel": 60}}	occupancy	acs	37	\N	default	f	
{"control_acs": [{"code": "Sistema de control por potencia", "name": "Sistema de control por potencia", "value": 0.92}, {"code": "Automático base a T° agua", "name": "Control automático basado en la medición de la temperatura del agua", "value": 1.0}], "combustibles": [{"fep": 1.9, "code": "Elect", "name": "Electricidad"}, {"fep": 1.1, "code": "Pet", "name": "Petróleo"}, {"fep": 1.1, "code": "GN", "name": "Gas natural"}, {"fep": 1.1, "code": "GL", "name": "Gas licuado"}, {"fep": 1.1, "code": "Keros", "name": "Kerosene domestico"}, {"fep": 1.1, "code": "Leña", "name": "Leña"}, {"fep": 1.1, "code": "Pellets", "name": "Pellets de madera"}, {"fep": 1.1, "code": "Carbón", "name": "Carbón"}], "control_hvac": [{"code": "Control automático", "name": "Control automático", "value": 1.0}, {"code": "Control manual", "name": "Control manual", "value": 0.8}, {"code": "Sin Sistema", "name": "Sin sistema de calefacción", "value": 0.8}], "rendimiento_acs": [{"code": "Sin Sist", "name": "Sistema por defecto - No se dispone de sistema de ACS", "value": 0.7}, {"code": "Directo-gas", "name": "Sistema de calentamiento de agua directo a gas", "value": 0.7}, {"code": "Directo-Elect", "name": "Sistema de calentamiento de agua directo a electricidad", "value": 1.0}, {"code": "Estanque-Elect", "name": "Sistema de calentamiento de agua con estanque eléctrico", "value": 1.0}, {"code": "Caldera-Conv", "name": "Sistema de calentamiento de agua con caldera convencional", "value": 0.7}, {"code": "Caldera-Cond", "name": "Sistema de calentamiento de agua con caldera a condensación", "value": 0.8}, {"code": "Bom-Cal Ag-Ag", "name": "Calentamiento de agua con bomba de calor tradicional agua - agua", "value": 1.8}, {"code": "V.R.V Ag-Ag", "name": "Calentamiento de agua con bomba de calor de flujo de refrigerante variable agua - agua", "value": 2.0}, {"code": "Bom-Cal Ai-Ag", "name": "Calentamiento de agua con bomba de calor aire - agua", "value": 1.8}, {"code": "V.R.V Ai-Ag", "name": "Calentamiento de agua con bomba de calor de flujo de refrigerante variable aire - agua", "value": 2.0}], "rendimiento_ref": [{"code": "Bom-Cal Ai-Ai <40kW", "name": "Bomba de Calor por aire", "value": 3.1}, {"code": "Bom-Cal Ai-Ai >40kW- <70kW", "name": "Bomba de Calor por aire", "value": 3.0}, {"code": "Bom-Cal Ai-Ai >70kW", "name": "Bomba de Calor por aire", "value": 2.7}, {"code": "Bom-Cal Ag-Ag <40kW", "name": "Bomba de Calor por agua o evaporación", "value": 3.3}, {"code": "Bom-Cal Ag-Ag >40kW- <70kW", "name": "Bomba de Calor por agua o evaporación", "value": 3.1}, {"code": "Bom-Cal Ag-Ag >70kW", "name": "Bomba de Calor por agua o evaporación", "value": 2.6}, {"code": "Tornillo <528kW", "name": "Tornillo enfriado por agua", "value": 5.2}, {"code": "Tornillo >528kW - <1055kW", "name": "Tornillo enfriado por agua", "value": 5.6}, {"code": "Tornillo >1055kW", "name": "Tornillo enfriado por agua", "value": 6.15}, {"code": "Comp. Cent. <528kW", "name": "Compresor centrifugo enfriado por agua", "value": 5.25}, {"code": "Comp. Cent. >528kW - <1055kW", "name": "Compresor centrifugo enfriado por agua", "value": 5.9}, {"code": "Comp. Cent. >1055kW", "name": "Compresor centrifugo enfriado por agua", "value": 6.4}], "distribucion_acs": [{"code": "Con Ais", "name": "Red de cañerías con aislación", "value": 1.0}, {"code": "Sin Ais", "name": "Red de cañerías sin aislación", "value": 0.9}, {"code": "No tiene sistema de ACS", "name": "No tiene sistema de ACS", "value": 1.0}], "distribucion_hvac": [{"code": "Sistema unitario autocontenido", "name": "Sistema unitario autocontenido", "value": 1.0}, {"code": "Sist Centralizado", "name": "Edificio con sistema centralizado", "value": 0.95}, {"code": "Calef distrital", "name": "Sistema de calefacción distrital", "value": 0.8}, {"code": "Sin Sistema", "name": "Valor por defecto si no tiene sistema de calefacción", "value": 1.0}], "rendimiento_calef": [{"code": "Sin Sist", "name": "Sistema por defecto - No se dispone de sistema de calefacción", "value": 0.45}, {"code": "Caldera-Encendido Piloto", "name": "Caldera a gas sin condensación encendido piloto control on/of", "value": 0.71}, {"code": "Caldera-Encendido Electronico", "name": "Caldera a gas sin condensación encendido electrónico control on/of", "value": 0.75}, {"code": "Caldera-Cond-Encendido electrónico", "name": "Caldera a gas con condensación encendido electrónico control modulado", "value": 0.85}, {"code": "Caldera a petróleo", "name": "Caldera a petróleo", "value": 0.8}, {"code": "Gas-Sin Evac Exterior", "name": "Equipo localizado sin evacuación de gases al exterior", "value": 0.45}, {"code": "Calefactor electrico por resistencia fijo", "name": "Calefactor electrico por resistencia fijo", "value": 1.0}, {"code": "Equipo Loc. gas con Evac. gases", "name": "Equipo localizado a gas con evacuación de gases", "value": 0.62}, {"code": "Calefactor localizado a leña", "name": "Calefactor localizado a leña", "value": 0.45}, {"code": "Calefactor a pellet", "name": "Calefactor a pellet", "value": 0.6}, {"code": "Caldera a leña", "name": "Caldera a leña", "value": 0.55}, {"code": "Caldera a pellet", "name": "Caldera a pellet", "value": 0.65}, {"code": "Bom-Cal Ai-Ai <40kW", "name": "Bomba de Calor por aire", "value": 3.3}, {"code": "Bom-Cal Ai-Ai >40kW- <70kW", "name": "Bomba de Calor por aire", "value": 3.2}, {"code": "Bom-Cal Ai-Ai >70kW", "name": "Bomba de Calor por aire", "value": 3.1}, {"code": "Bom-Cal Ag-Ag <40kW", "name": "Bomba de Calor por agua o evaporación", "value": 4.2}, {"code": "Bom-Cal Ag-Ag >40kW- <70kW", "name": "Bomba de Calor por agua o evaporación", "value": 3.6}, {"code": "Bom-Cal Ag-Ag >70kW", "name": "Bomba de Calor por agua o evaporación", "value": 3.1}], "consumos_por_fuente_de_energia": [{"code": "Elect", "name": "Electricidad", "co2_eq": 0.31}, {"code": "Pet", "name": "Petróleo", "co2_eq": 0.24}, {"code": "GN", "name": "Gas natural", "co2_eq": 0.2}, {"code": "GL", "name": "Gas licuado", "co2_eq": 0.23}, {"code": "Keros", "name": "Kerosene domestico", "co2_eq": 0.26}, {"code": "Leña", "name": "Leña", "co2_eq": null}, {"code": "Pellets", "name": "Pellets de madera", "co2_eq": null}, {"code": "Carbón", "name": "Carbón", "co2_eq": 0.5}]}	general	energy_systems	38	\N	default	f	
{"monthly": {"may": 12.0, "july": 11.0, "june": 11.0, "april": 14.0, "march": 16.0, "august": 11.7, "january": 17.5, "october": 14.4, "december": 17.0, "february": 16.0, "november": 15.5, "september": 12.5}}	red	temperature	39	\N	default	f	
{"monthly": {"may": 3720, "july": 3720, "june": 3600, "april": 3600, "march": 3720, "august": 3720, "january": 3720, "october": 3720, "december": 3720, "february": 3360, "november": 3600, "september": 3600}}	monthly	water	40	\N	default	f	
{"activity_levels": [{"name": "Sedentario", "kg_water_sec": 0.000013, "gr_water_hour": 45}, {"name": "Ejercicio Bajo", "kg_water_sec": 0.000028, "gr_water_hour": 100}, {"name": "Ejercicio Medio", "kg_water_sec": 0.000044, "gr_water_hour": 160}, {"name": "Ejercicio Alto", "kg_water_sec": 0.000069, "gr_water_hour": 250}, {"name": "Jardin Infantil", "kg_water_sec": 0.000011, "gr_water_hour": 40}, {"name": "Colegio", "kg_water_sec": 0.000013, "gr_water_hour": 45}]}	water_production	human_activity	41	\N	default	f	
\.


--
-- TOC entry 3788 (class 0 OID 16517)
-- Dependencies: 242
-- Data for Name: customizations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.customizations (id, primary_color, secondary_color, background_color, logo_url) FROM stdin;
\.


--
-- TOC entry 3786 (class 0 OID 16508)
-- Dependencies: 240
-- Data for Name: dailyschedule; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dailyschedule (hour_1, hour_2, hour_3, hour_4, hour_5, hour_6, hour_7, hour_8, hour_9, hour_10, hour_11, hour_12, hour_13, hour_14, hour_15, hour_16, hour_17, hour_18, hour_19, hour_20, hour_21, hour_22, hour_23, hour_24, id, type, perfil_id, user_id) FROM stdin;
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	1	usuarios	1	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	2	iluminacion verano	1	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	3	iluminacion invierno	1	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	4	equipos	1	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	5	usuarios	2	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	6	iluminacion verano	2	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	7	iluminacion invierno	2	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	8	equipos	2	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	9	usuarios	3	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	10	iluminacion verano	3	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	11	iluminacion invierno	3	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	12	equipos	3	\N
0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	13	usuarios	4	\N
0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	14	iluminacion verano	4	\N
0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	15	iluminacion invierno	4	\N
0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	16	equipos	4	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	17	usuarios	5	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	18	iluminacion verano	5	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	19	iluminacion invierno	5	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	20	equipos	5	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	21	usuarios	6	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	22	iluminacion verano	6	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	23	iluminacion invierno	6	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	24	equipos	6	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	25	usuarios	7	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	26	iluminacion verano	7	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	27	iluminacion invierno	7	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	28	equipos	7	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	29	usuarios	8	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	30	iluminacion verano	8	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	31	iluminacion invierno	8	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	32	equipos	8	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	33	usuarios	9	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	34	iluminacion verano	9	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	35	iluminacion invierno	9	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	36	equipos	9	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	37	usuarios	10	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	38	iluminacion verano	10	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	39	iluminacion invierno	10	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	40	equipos	10	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	41	usuarios	11	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	42	iluminacion verano	11	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	43	iluminacion invierno	11	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	44	equipos	11	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	45	usuarios	12	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	46	iluminacion verano	12	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	47	iluminacion invierno	12	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	48	equipos	12	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	49	usuarios	13	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	50	iluminacion verano	13	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	51	iluminacion invierno	13	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	52	equipos	13	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	53	usuarios	14	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	54	iluminacion verano	14	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	55	iluminacion invierno	14	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	56	equipos	14	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	57	usuarios	15	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	58	iluminacion verano	15	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	59	iluminacion invierno	15	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	60	equipos	15	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	61	usuarios	16	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	62	iluminacion verano	16	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	63	iluminacion invierno	16	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	64	equipos	16	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	65	usuarios	17	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	66	iluminacion verano	17	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	67	iluminacion invierno	17	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	68	equipos	17	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	69	usuarios	18	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	70	iluminacion verano	18	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	71	iluminacion invierno	18	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	72	equipos	18	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	73	usuarios	19	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	74	iluminacion verano	19	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	75	iluminacion invierno	19	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	76	equipos	19	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	77	usuarios	20	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	78	iluminacion verano	20	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	79	iluminacion invierno	20	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	80	equipos	20	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	81	usuarios	21	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	82	iluminacion verano	21	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	83	iluminacion invierno	21	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	84	equipos	21	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	85	usuarios	22	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	86	iluminacion verano	22	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	87	iluminacion invierno	22	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	88	equipos	22	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	89	usuarios	23	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	90	iluminacion verano	23	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	91	iluminacion invierno	23	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	92	equipos	23	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	93	usuarios	24	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	94	iluminacion verano	24	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	95	iluminacion invierno	24	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	96	equipos	24	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	97	usuarios	25	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	98	iluminacion verano	25	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	99	iluminacion invierno	25	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	100	equipos	25	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	101	usuarios	26	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	102	iluminacion verano	26	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	103	iluminacion invierno	26	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	104	equipos	26	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	105	usuarios	27	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	106	iluminacion verano	27	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	107	iluminacion invierno	27	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	108	equipos	27	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	109	usuarios	28	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	110	iluminacion verano	28	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	111	iluminacion invierno	28	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	112	equipos	28	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	113	usuarios	29	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	114	iluminacion verano	29	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	115	iluminacion invierno	29	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	116	equipos	29	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	117	usuarios	30	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	118	iluminacion verano	30	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	119	iluminacion invierno	30	\N
0	0	0	0	0	0	0	100	100	100	100	100	100	100	100	100	100	100	0	0	0	0	0	0	120	equipos	30	\N
\.


--
-- TOC entry 3820 (class 0 OID 16720)
-- Dependencies: 274
-- Data for Name: details; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.details (scantilon_location, name_detail, material_id, layer_thickness, id, project_id, detail_part_id, is_deleted, created_status) FROM stdin;
Techo	Techo Base	1	10	1	\N	1	f	default
Techo	Techo Base	2	4.55	2	\N	1	f	default
Muro	Muro Base	1	10	3	\N	2	f	default
Muro	Muro Base	2	0.49	4	\N	2	f	default
Piso	Piso Base	1	10	5	\N	3	f	default
Piso	Piso Base	2	0.98	6	\N	3	f	default
\.


--
-- TOC entry 3770 (class 0 OID 16431)
-- Dependencies: 224
-- Data for Name: details_part; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.details_part (name_detail, info, id, project_id, type, value_u, calculations, created_status, code_ifc) FROM stdin;
Techo Base	{"surface_color": {"exterior": {"name": "Intermedio", "value": 0.6}, "interior": {"name": "Intermedio", "value": 0.6}}}	1	\N	Techo	0	{}	created	TECHO_001
Muro Base	{"surface_color": {"exterior": {"name": "Intermedio", "value": 0.6}, "interior": {"name": "Intermedio", "value": 0.6}}}	2	\N	Muro	0	{}	created	MURO_001
Piso Base	{"ref_aisl_vertical": {"d": 0.0, "e_aisl": 0.0, "lambda": 0.0}, "ref_aisl_horizontal": {"d": 0.0, "e_aisl": 0.0, "lambda": 0.0}}	3	\N	Piso	0	{}	created	PISO_001
\.


--
-- TOC entry 3842 (class 0 OID 16873)
-- Dependencies: 296
-- Data for Name: divisions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.divisions (division, a, b, d, id, orientation_id, is_deleted, num_orientation) FROM stdin;
\.


--
-- TOC entry 3824 (class 0 OID 16748)
-- Dependencies: 278
-- Data for Name: doors; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.doors (door_id, characteristics, angulo_azimut, high, broad, id, enclosure_id, orientation) FROM stdin;
\.


--
-- TOC entry 3806 (class 0 OID 16614)
-- Dependencies: 260
-- Data for Name: elements; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.elements (name_element, type, atributs, u_marco, fm, id, user_id, created_status, is_deleted, calculations, code_ifc) FROM stdin;
V Base	window	{"u_vidrio": 5.7, "fs_vidrio": 0.87, "frame_type": "Fierro", "clousure_type": "Corredera"}	5.7	0.75	1	\N	default	f	{}	VENTANA_001
VM-Mad	window	{"u_vidrio": 5.8, "fs_vidrio": 0.87, "frame_type": "Madera Sin RPT", "clousure_type": "Corredera"}	2.6	0.75	2	\N	default	f	{}	VENTANA_002
VM-PVC	window	{"u_vidrio": 3.28, "fs_vidrio": 0.7743, "frame_type": "PVC Sin RPT", "clousure_type": "Corredera"}	2.8	0.8	3	\N	default	f	{}	VENTANA_003
VM-Sin RPT	window	{"u_vidrio": 3.01, "fs_vidrio": 0.7743, "frame_type": "Metalico  Sin RPT", "clousure_type": "Corredera"}	5.8	0.85	4	\N	default	f	{}	VENTANA_004
VM-Con RPT	window	{"u_vidrio": 2.85, "fs_vidrio": 0.7743, "frame_type": "Metalico Con RPT", "clousure_type": "Corredera"}	3.3	0.8	5	\N	default	f	{}	VENTANA_005
DVH con 6mm	window	{"u_vidrio": 3.28, "fs_vidrio": 0.7743, "frame_type": "PVC Sin RPT", "clousure_type": "Corredera"}	2.8	0.8	6	\N	default	f	{}	VENTANA_006
DVH con 9mm	window	{"u_vidrio": 3.01, "fs_vidrio": 0.7743, "frame_type": "PVC Sin RPT", "clousure_type": "Corredera"}	2.8	0.8	7	\N	default	f	{}	VENTANA_007
DVH con 12mm	window	{"u_vidrio": 2.85, "fs_vidrio": 0.7743, "frame_type": "PVC Sin RPT", "clousure_type": "Abatir"}	2.8	0.8	8	\N	default	f	{}	VENTANA_008
DVH con 15mm o +	window	{"u_vidrio": 2.8, "fs_vidrio": 0.7743, "frame_type": "PVC Sin RPT", "clousure_type": "Corredera"}	2.8	0.8	9	\N	default	f	{}	VENTANA_009
P Base	door	{"ventana_id": 1, "name_ventana": "V Base", "u_puerta_opaca": 2.63, "porcentaje_vidrio": 0.0}	1.25	0.0878	10	\N	default	f	{"r_puro": 0.2285912191948776, "u_vidrio": 5.7, "u_ponderado": 2.508836, "u_ponderado_opaco": 2.508836}	PUERTA_001
MS	door	{"ventana_id": 1, "name_ventana": "V Base", "u_puerta_opaca": 1.91, "porcentaje_vidrio": 0.0}	1.25	0.0878	11	\N	default	f	{"r_puro": 0.3699416431072129, "u_vidrio": 5.7, "u_ponderado": 1.852052, "u_ponderado_opaco": 1.852052}	PUERTA_002
MS < 50% Vidrio	door	{"ventana_id": 1, "name_ventana": "V Base", "u_puerta_opaca": 1.91, "porcentaje_vidrio": 0.4}	1.25	0.0878	12	\N	default	f	{"r_puro": 0.3814442324447729, "u_vidrio": 5.7, "u_ponderado": 3.368052, "u_ponderado_opaco": 1.8134199999999998}	PUERTA_003
MS < 100% Vidrio	door	{"ventana_id": 1, "name_ventana": "V Base", "u_puerta_opaca": 1.91, "porcentaje_vidrio": 0.85}	1.25	0.0878	13	\N	default	f	{"r_puro": 0.4863057859918093, "u_vidrio": 5.7, "u_ponderado": 5.073551999999999, "u_ponderado_opaco": 1.52368}	PUERTA_004
ML	door	{"ventana_id": 1, "name_ventana": "V Base", "u_puerta_opaca": 2.63, "porcentaje_vidrio": 0.0}	1.25	0.0878	14	\N	default	f	{"r_puro": 0.2285912191948776, "u_vidrio": 5.7, "u_ponderado": 2.508836, "u_ponderado_opaco": 2.508836}	PUERTA_005
ML < 50% Vidrio	door	{"ventana_id": 1, "name_ventana": "V Base", "u_puerta_opaca": 2.53, "porcentaje_vidrio": 0.45}	1.25	0.0878	15	\N	default	f	{"r_puro": 0.25998445801631753, "u_vidrio": 5.7, "u_ponderado": 3.844116, "u_ponderado_opaco": 2.3256654545454545}	PUERTA_006
ML < 100% Vidrio	door	{"ventana_id": 1, "name_ventana": "V Base", "u_puerta_opaca": 2.18, "porcentaje_vidrio": 0.85}	1.25	0.0878	16	\N	default	f	{"r_puro": 0.44138147758675494, "u_vidrio": 5.7, "u_ponderado": 5.090346, "u_ponderado_opaco": 1.6356400000000002}	PUERTA_007
\.


--
-- TOC entry 3774 (class 0 OID 16449)
-- Dependencies: 228
-- Data for Name: enclosures; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.enclosures (name, id, user_id, original_id, code, created_status, is_deleted, code_ifc) FROM stdin;
Espera	1	\N	\N	ES	default	f	OCP_001
Auditorio	2	\N	\N	AU	default	f	OCP_002
Baño	3	\N	\N	BA	default	f	OCP_003
Bodega	4	\N	\N	BO	default	f	OCP_004
Cafetería	5	\N	\N	KI	default	f	OCP_005
Comedores	6	\N	\N	CO	default	f	OCP_006
Pasillos	7	\N	\N	PA	default	f	OCP_007
Oficina	8	\N	\N	OF	default	f	OCP_008
Sala de Exposiciones	9	\N	\N	SE	default	f	OCP_009
Sala Reuniones	10	\N	\N	SR	default	f	OCP_010
Sala de Lectura	11	\N	\N	SL	default	f	OCP_011
Sitio Arqueologico	12	\N	\N	SA	default	f	OCP_012
Biblioteca	13	\N	\N	BI	default	f	OCP_013
Salas Cuna	14	\N	\N	SC	default	f	OCP_014
Sala Clase Párvulos	15	\N	\N	SP	default	f	OCP_015
Sala Educación Básica	16	\N	\N	SB	default	f	OCP_016
Sala Educación Media	17	\N	\N	SM	default	f	OCP_017
Sala Educación Especial	18	\N	\N	SN	default	f	OCP_018
Camarines, Gimnasios	19	\N	\N	CA	default	f	OCP_019
Talleres, Laboratorios	20	\N	\N	LAB	default	f	OCP_020
Biblioteca	21	\N	\N	BI2	default	f	OCP_021
Casino, Uso Múltiple	22	\N	\N	CS	default	f	OCP_022
Cocina	23	\N	\N	CC	default	f	OCP_023
Estar, Comedor, Estudio	24	\N	\N	ET	default	f	OCP_024
Dormitorios, Hogares, Internados	25	\N	\N	DO	default	f	OCP_025
Sector Ambulatorios y Diagnóstico	26	\N	\N	SD	default	f	OCP_026
Sector Habitaciones	27	\N	\N	SH	default	f	OCP_027
Oficina Administrativa	28	\N	\N	OA	default	f	OCP_028
Área Tratamiento	29	\N	\N	AT	default	f	OCP_029
Consultas	30	\N	\N	CN	default	f	OCP_030
\.


--
-- TOC entry 3818 (class 0 OID 16701)
-- Dependencies: 272
-- Data for Name: enclosures_generals; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.enclosures_generals (name_enclosure, occupation_profile_id, height, co2_sensor, level_id, id, project_id, is_deleted) FROM stdin;
\.


--
-- TOC entry 3794 (class 0 OID 16544)
-- Dependencies: 248
-- Data for Name: energy_data; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.energy_data (id, type, name, value) FROM stdin;
1	combustible	Elect	1.9
2	combustible	Pet	1
3	combustible	GN	1.1
4	combustible	GL	1.1
5	combustible	Keros	1.1
6	combustible	Leña	0.9
7	combustible	Pellets	1.1
8	combustible	Carbón	1.1
9	rendimiento_acs	Sin Sist	0.7
10	rendimiento_acs	Directo-gas	0.9
11	rendimiento_acs	Directo-Elect	1
12	rendimiento_acs	Estanque-Elect	1
13	rendimiento_acs	Caldera-Conv	0.8
14	rendimiento_acs	Caldera-Cond	0.8
15	rendimiento_acs	V.R.V Ag-Ag	0.8
16	rendimiento_acs	Bom-Cal Ag-Ag	0.8
17	distribucion_acs	Con Ais	1
18	distribucion_acs	Sin Ais	0.9
19	distribucion_acs	No tiene sistema de ACS	1
20	control_acs	Sistema de control por potencia	0.92
21	control_acs	Automático base a T° agua	1
22	rendimiento_calef	Sin Sist	0.45
23	rendimiento_calef	Caldera-Encendido Piloto	0.7
24	rendimiento_calef	Caldera-Encendido Electronico	0.71
25	rendimiento_calef	Caldera-Cond-Encendido electrónico	0.73
26	rendimiento_calef	Caldera a petróleo	0.81
27	rendimiento_calef	Gas-Sin Evac Exterior	0.86
28	rendimiento_calef	Equipo Loc. gas con Evac. gases	0.79
29	rendimiento_calef	Calefactor localizado a leña	0.79
30	rendimiento_calef	Caldera a leña	0.85
31	rendimiento_calef	Caldera a pellet	0.85
32	rendimiento_ref	Bom-Cal Ai-Ai <40kW	3.1
33	rendimiento_ref	Bom-Cal Ai-Ai <70kW	3
34	rendimiento_ref	Bom-Cal Ai-Ag <40kW	3.1
35	rendimiento_ref	Bom-Cal Ai-Ag <70kW	3
36	rendimiento_ref	Tornillo <=528kW	1.05
37	rendimiento_ref	Tornillo <=1055kW	1.05
38	rendimiento_ref	Comp. Cent. <=528kW	1.05
39	rendimiento_ref	Comp. Cent. >1055kW	1.05
40	distribucion_hvac	Sistema unitario autocontenido	1
41	distribucion_hvac	Sist Centralizado	0.95
42	distribucion_hvac	Calef distrital	0.9
43	distribucion_hvac	Sin Sistema	1
44	control_hvac	Control automático	1
45	control_hvac	Control manual	0.9
46	control_hvac	Sin Sistema	1
47	co2_eq	Elect	0.31
48	co2_eq	Pet	0.29
49	co2_eq	GN	0.25
50	co2_eq	GL	0.25
51	co2_eq	Keros	0.26
52	co2_eq	Leña	0.15
53	co2_eq	Pellets	0.2
54	co2_eq	Carbón	0.29
\.


--
-- TOC entry 3776 (class 0 OID 16463)
-- Dependencies: 230
-- Data for Name: favs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.favs (fav1, fav2_izq, fav2_der, fav3, id, item_id, type) FROM stdin;
\.


--
-- TOC entry 3840 (class 0 OID 16859)
-- Dependencies: 294
-- Data for Name: floorpo; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.floorpo (id, enclosure_id, floor_id, nombre, longitud_pt, categoria, categoria_1, categoria_2, posicion_aislamiento, e_aislamiento_1, e_aislamiento_2, codigo_pt, pt, pt_lineal, espacio_contiguo) FROM stdin;
\.


--
-- TOC entry 3826 (class 0 OID 16762)
-- Dependencies: 280
-- Data for Name: floors; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.floors (floor_id, characteristic, area, parameter, is_ventilated, id, enclosure_id, u, po6_l) FROM stdin;
\.


--
-- TOC entry 3816 (class 0 OID 16687)
-- Dependencies: 270
-- Data for Name: formulas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.formulas (id, project_id, item_id, type, name, atributs, is_deleted) FROM stdin;
1	\N	1	details	Techo Base	{"material_id": 1, "name_detail": "Techo Base", "layer_thickness": 10.0, "km_op_acumulated": 0, "scantilon_location": "Techo", "position_insulation": 0}	f
2	\N	2	details	Techo Base	{"material_id": 2, "name_detail": "Techo Base", "layer_thickness": 4.55, "km_op_acumulated": 0, "scantilon_location": "Techo", "position_insulation": 0}	f
3	\N	3	details	Muro Base	{"material_id": 1, "name_detail": "Muro Base", "layer_thickness": 10.0, "km_op_acumulated": 0, "scantilon_location": "Muro", "position_insulation": 0}	f
4	\N	4	details	Muro Base	{"material_id": 2, "name_detail": "Muro Base", "layer_thickness": 0.49, "km_op_acumulated": 0, "scantilon_location": "Muro", "position_insulation": 0}	f
5	\N	5	details	Piso Base	{"material_id": 1, "name_detail": "Piso Base", "layer_thickness": 10.0, "km_op_acumulated": 0, "scantilon_location": "Piso", "position_insulation": 0}	f
6	\N	6	details	Piso Base	{"material_id": 2, "name_detail": "Piso Base", "layer_thickness": 0.98, "km_op_acumulated": 0, "scantilon_location": "Piso", "position_insulation": 0}	f
\.


--
-- TOC entry 3812 (class 0 OID 16656)
-- Dependencies: 266
-- Data for Name: heating_config; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.heating_config (id, project_id, combustible_codigo, combustible_valor, rendimiento_codigo, rendimiento_valor, caldera_codigo, caldera_valor, distribucion_codigo, distribucion_valor, control_codigo, control_valor) FROM stdin;
\.


--
-- TOC entry 3796 (class 0 OID 16553)
-- Dependencies: 250
-- Data for Name: indicadores_finales; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.indicadores_finales (data, id, project_id, type) FROM stdin;
\.


--
-- TOC entry 3792 (class 0 OID 16535)
-- Dependencies: 246
-- Data for Name: levels; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.levels (id, name, description) FROM stdin;
1	Nivel_001	Este es el Nivel_001
2	Nivel_002	Este es el Nivel_002
3	Nivel_003	Este es el Nivel_003
4	Nivel_004	Este es el Nivel_004
5	Nivel_005	Este es el Nivel_005
6	Nivel_006	Este es el Nivel_006
7	Nivel_007	Este es el Nivel_007
8	Nivel_008	Este es el Nivel_008
9	Nivel_009	Este es el Nivel_009
10	Nivel_010	Este es el Nivel_010
11	Nivel_011	Este es el Nivel_011
12	Nivel_012	Este es el Nivel_012
13	Nivel_013	Este es el Nivel_013
14	Nivel_014	Este es el Nivel_014
15	Nivel_015	Este es el Nivel_015
\.


--
-- TOC entry 3832 (class 0 OID 16804)
-- Dependencies: 286
-- Data for Name: orientations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.orientations (azimut, id, enclosure_id, orientation, is_deleted) FROM stdin;
\.


--
-- TOC entry 3800 (class 0 OID 16571)
-- Dependencies: 254
-- Data for Name: personal_access_token; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.personal_access_token (id, user_id, token, token_type, in_used, created_at, expires_at) FROM stdin;
42	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3NTgzMTAyNDh9.z8wUzdks20TuG2wQvdH8mjJcAHlkuSJuaqpFeiYkSdA	access	t	2025-09-17 19:30:48.070104	2025-09-19 19:30:48.069702
44	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3NTgzMTA0MjJ9.DQ09d4uYLChmSJYnVRetODqJVYSrhTqtv_4zVYzJNjY	access	t	2025-09-17 19:33:42.603625	2025-09-19 19:33:42.603284
46	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3NTgzOTg2ODd9.DXjDcr-YCldxh7-C9pZWOmP44dY7oy176ln-rCL45yY	access	t	2025-09-18 20:04:47.161361	2025-09-20 20:04:47.160931
48	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3NTg0MDQ1NjJ9.pSuyL71THgX_CHL3yy35SEBxsiimOUOaJEWZ3TA7VhI	access	t	2025-09-18 21:42:42.724111	2025-09-20 21:42:42.723398
50	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3NTg0MjEzMjV9.0s08xTlsfrWe8oGQOPqAuYSW-zAKM03qBwKJvew9WcU	access	t	2025-09-19 02:22:05.912309	2025-09-21 02:22:05.911574
\.


--
-- TOC entry 3802 (class 0 OID 16585)
-- Dependencies: 256
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.projects (country, divisions, name_project, owner_name, owner_lastname, project_metadata, residential_type, building_type, main_use_type, number_levels, number_homes_per_level, built_surface, latitude, longitude, status, id, user_id, is_deleted, created_at, updated_at, are_files_processed, building_name) FROM stdin;
\.


--
-- TOC entry 3780 (class 0 OID 16485)
-- Dependencies: 234
-- Data for Name: pt_table; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.pt_table (id, enclosure_id, "P01", "P02", "P03", "P04", "P05", "P06", total_pt, pt_piso_prop, pt_piso_base, "case") FROM stdin;
\.


--
-- TOC entry 3790 (class 0 OID 16526)
-- Dependencies: 244
-- Data for Name: regiones; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.regiones (id, nombre_region) FROM stdin;
1	Región_Metropolitana_de_Santiago
2	Región_de_Antofagasta
3	Región_de_Arica_y_de_Parinacota
4	Región_de_Atacama
5	Región_de_Biobío
6	Región_de_Coquimbo
7	Región_de_Maule
8	Región_de_OHiggins
9	Región_de_Tarapacá
10	Región_de_Valparaíso
11	Región_de_Ñuble
\.


--
-- TOC entry 3798 (class 0 OID 16562)
-- Dependencies: 252
-- Data for Name: resultados_por_recinto; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.resultados_por_recinto (recinto, perfil_uso, superficie, categorias, id, enclosure_id, perfil_id, project_id, type) FROM stdin;
\.


--
-- TOC entry 3828 (class 0 OID 16776)
-- Dependencies: 282
-- Data for Name: roofs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.roofs (roof_id, characteristic, area, id, enclosure_id, u) FROM stdin;
\.


--
-- TOC entry 3772 (class 0 OID 16440)
-- Dependencies: 226
-- Data for Name: tabla_py; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tabla_py (id, enclosure_id, item_id, name, type, orientation, nodos_emisividad, nodos_area, r_puro, emisividad_x_sup, r_a_atot) FROM stdin;
\.


--
-- TOC entry 3778 (class 0 OID 16473)
-- Dependencies: 232
-- Data for Name: thermal_bridges; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.thermal_bridges (id, code_pt, type_pt, element_1, element_2, position_insulation, insulation_thickness, return_insulation, position_window, value_pt) FROM stdin;
1	P01.EP.EP.SA.0	P01	EP	EP	SA	0	0	0	0.19912017271171756
2	P01.EI.EI.SA.0	P01	EI	EI	SA	0	0	0	0.14954083257131146
3	P01.EP.EM.SA.0	P01	EP	EM	SA	0	0	0	0.21317724672328175
4	P01.EI.EM.SA.0	P01	EI	EM	SA	0	0	0	0.15474894322250066
5	P01.EP.EL.SA.0	P01	EP	EL	SA	0	0	0	0.2124719061666811
6	P01.EI.EL.SA.0	P01	EI	EL	SA	0	0	0	0.14804360266590066
7	P01.EM.EL.SA.0	P01	EM	EL	SA	0	0	0	0.05156304667219569
8	P01.EL.EL.SA.0	P01	EL	EL	SA	0	0	0	0.08335770611559612
9	P01.EP.EP.CE.0,01	P01	EP	EP	CE	0.01	0	0	0.31635869062875566
10	P01.EP.EP.CE.0,02	P01	EP	EP	CE	0.02	0	0	0.2862280883472791
11	P01.EP.EP.CE.0,03	P01	EP	EP	CE	0.03	0	0	0.2560974860658025
12	P01.EP.EP.CE.0,04	P01	EP	EP	CE	0.04	0	0	0.22596688378432594
13	P01.EP.EP.CE.0,05	P01	EP	EP	CE	0.05	0	0	0.19583628150284937
14	P01.EP.EP.CE.0,06	P01	EP	EP	CE	0.060000000000000005	0	0	0.18263699246858034
15	P01.EP.EP.CE.0,07	P01	EP	EP	CE	0.07	0	0	0.16943770343431136
16	P01.EP.EP.CE.0,08	P01	EP	EP	CE	0.08	0	0	0.15623841440004232
17	P01.EP.EP.CE.0,09	P01	EP	EP	CE	0.09	0	0	0.14303912536577335
18	P01.EP.EP.CE.0,1	P01	EP	EP	CE	0.09999999999999999	0	0	0.1298398363315043
19	P01.EP.EP.CE.0,11	P01	EP	EP	CE	0.10999999999999999	0	0	0.1166405472972353
20	P01.EP.EP.CE.0,12	P01	EP	EP	CE	0.11999999999999998	0	0	0.1034412582629663
21	P01.EP.EP.CE.0,13	P01	EP	EP	CE	0.12999999999999998	0	0	0.09024196922869732
22	P01.EP.EP.CE.0,14	P01	EP	EP	CE	0.13999999999999999	0	0	0.07704268019442828
23	P01.EP.EP.CE.0,15	P01	EP	EP	CE	0.15	0	0	0.06384339116015925
24	P01.EP.EP.CE.0,16	P01	EP	EP	CE	0.16	0	0	0.05064410212589024
25	P01.EP.EP.CE.0,17	P01	EP	EP	CE	0.17	0	0	0.037444813091621204
26	P01.EP.EP.CE.0,18	P01	EP	EP	CE	0.18000000000000002	0	0	0.02424552405735217
27	P01.EP.EP.CE.0,19	P01	EP	EP	CE	0.19000000000000003	0	0	0.011046235023083162
28	P01.EP.EP.CE.0,2	P01	EP	EP	CE	0.20000000000000004	0	0	0
29	P01.EI.EI.CE.0,01	P01	EI	EI	CE	0.01	0	0	0.1930734365062059
30	P01.EI.EI.CE.0,02	P01	EI	EI	CE	0.02	0	0	0.1826361984898665
31	P01.EI.EI.CE.0,03	P01	EI	EI	CE	0.03	0	0	0.17219896047352712
32	P01.EI.EI.CE.0,04	P01	EI	EI	CE	0.04	0	0	0.16176172245718773
33	P01.EI.EI.CE.0,05	P01	EI	EI	CE	0.05	0	0	0.15132448444084834
34	P01.EI.EI.CE.0,06	P01	EI	EI	CE	0.060000000000000005	0	0	0.14309895646627918
35	P01.EI.EI.CE.0,07	P01	EI	EI	CE	0.07	0	0	0.13487342849171
36	P01.EI.EI.CE.0,08	P01	EI	EI	CE	0.08	0	0	0.12664790051714084
37	P01.EI.EI.CE.0,09	P01	EI	EI	CE	0.09	0	0	0.11842237254257167
38	P01.EI.EI.CE.0,1	P01	EI	EI	CE	0.09999999999999999	0	0	0.1101968445680025
39	P01.EI.EI.CE.0,11	P01	EI	EI	CE	0.10999999999999999	0	0	0.10197131659343334
40	P01.EI.EI.CE.0,12	P01	EI	EI	CE	0.11999999999999998	0	0	0.09374578861886416
41	P01.EI.EI.CE.0,13	P01	EI	EI	CE	0.12999999999999998	0	0	0.08552026064429501
42	P01.EI.EI.CE.0,14	P01	EI	EI	CE	0.13999999999999999	0	0	0.07729473266972584
43	P01.EI.EI.CE.0,15	P01	EI	EI	CE	0.15	0	0	0.06906920469515665
44	P01.EI.EI.CE.0,16	P01	EI	EI	CE	0.16	0	0	0.06084367672058749
45	P01.EI.EI.CE.0,17	P01	EI	EI	CE	0.17	0	0	0.052618148746018306
46	P01.EI.EI.CE.0,18	P01	EI	EI	CE	0.18000000000000002	0	0	0.04439262077144912
47	P01.EI.EI.CE.0,19	P01	EI	EI	CE	0.19000000000000003	0	0	0.03616709279687996
48	P01.EI.EI.CE.0,2	P01	EI	EI	CE	0.20000000000000004	0	0	0.027941564822310777
49	P01.EP.EM.CE.0,01	P01	EP	EM	CE	0.01	0	0	0.26757487467608554
50	P01.EP.EM.CE.0,02	P01	EP	EM	CE	0.02	0	0	0.2419693646210745
51	P01.EP.EM.CE.0,03	P01	EP	EM	CE	0.03	0	0	0.21636385456606344
52	P01.EP.EM.CE.0,04	P01	EP	EM	CE	0.04	0	0	0.1907583445110524
53	P01.EP.EM.CE.0,05	P01	EP	EM	CE	0.05	0	0	0.16515283445604134
54	P01.EP.EM.CE.0,06	P01	EP	EM	CE	0.060000000000000005	0	0	0.15432809753224103
55	P01.EP.EM.CE.0,07	P01	EP	EM	CE	0.07	0	0	0.14350336060844068
56	P01.EP.EM.CE.0,08	P01	EP	EM	CE	0.08	0	0	0.13267862368464034
57	P01.EP.EM.CE.0,09	P01	EP	EM	CE	0.09	0	0	0.12185388676084004
58	P01.EP.EM.CE.0,1	P01	EP	EM	CE	0.09999999999999999	0	0	0.11102914983703972
59	P01.EP.EM.CE.0,11	P01	EP	EM	CE	0.10999999999999999	0	0	0.1002044129132394
60	P01.EP.EM.CE.0,12	P01	EP	EM	CE	0.11999999999999998	0	0	0.08937967598943908
61	P01.EP.EM.CE.0,13	P01	EP	EM	CE	0.12999999999999998	0	0	0.07855493906563876
62	P01.EP.EM.CE.0,14	P01	EP	EM	CE	0.13999999999999999	0	0	0.06773020214183842
63	P01.EP.EM.CE.0,15	P01	EP	EM	CE	0.15	0	0	0.056905465218038076
64	P01.EP.EM.CE.0,16	P01	EP	EM	CE	0.16	0	0	0.04608072829423773
65	P01.EP.EM.CE.0,17	P01	EP	EM	CE	0.17	0	0	0.03525599137043742
66	P01.EP.EM.CE.0,18	P01	EP	EM	CE	0.18000000000000002	0	0	0.024431254446637074
67	P01.EP.EM.CE.0,19	P01	EP	EM	CE	0.19000000000000003	0	0	0.01360651752283673
68	P01.EP.EM.CE.0,2	P01	EP	EM	CE	0.20000000000000004	0	0	0.0027817805990363875
69	P01.EI.EM.CE.0,01	P01	EI	EM	CE	0.01	0	0	0.17061567255591736
70	P01.EI.EM.CE.0,02	P01	EI	EM	CE	0.02	0	0	0.15984755340869106
71	P01.EI.EM.CE.0,03	P01	EI	EM	CE	0.03	0	0	0.14907943426146475
72	P01.EI.EM.CE.0,04	P01	EI	EM	CE	0.04	0	0	0.13831131511423844
73	P01.EI.EM.CE.0,05	P01	EI	EM	CE	0.05	0	0	0.12754319596701214
74	P01.EI.EM.CE.0,06	P01	EI	EM	CE	0.060000000000000005	0	0	0.12077250044534318
75	P01.EI.EM.CE.0,07	P01	EI	EM	CE	0.07	0	0	0.11400180492367422
76	P01.EI.EM.CE.0,08	P01	EI	EM	CE	0.08	0	0	0.10723110940200525
77	P01.EI.EM.CE.0,09	P01	EI	EM	CE	0.09	0	0	0.1004604138803363
78	P01.EI.EM.CE.0,1	P01	EI	EM	CE	0.09999999999999999	0	0	0.09368971835866735
79	P01.EI.EM.CE.0,11	P01	EI	EM	CE	0.10999999999999999	0	0	0.0869190228369984
80	P01.EI.EM.CE.0,12	P01	EI	EM	CE	0.11999999999999998	0	0	0.08014832731532945
81	P01.EI.EM.CE.0,13	P01	EI	EM	CE	0.12999999999999998	0	0	0.0733776317936605
82	P01.EI.EM.CE.0,14	P01	EI	EM	CE	0.13999999999999999	0	0	0.06660693627199153
83	P01.EI.EM.CE.0,15	P01	EI	EM	CE	0.15	0	0	0.05983624075032257
84	P01.EI.EM.CE.0,16	P01	EI	EM	CE	0.16	0	0	0.0530655452286536
85	P01.EI.EM.CE.0,17	P01	EI	EM	CE	0.17	0	0	0.04629484970698465
86	P01.EI.EM.CE.0,18	P01	EI	EM	CE	0.18000000000000002	0	0	0.039524154185315685
87	P01.EI.EM.CE.0,19	P01	EI	EM	CE	0.19000000000000003	0	0	0.032753458663646706
88	P01.EI.EM.CE.0,2	P01	EI	EM	CE	0.20000000000000004	0	0	0.025982763141977755
89	P01.EP.EL.CE.0,01	P01	EP	EL	CE	0.01	0	0	0.35077010537630704
90	P01.EP.EL.CE.0,02	P01	EP	EL	CE	0.02	0	0	0.34400443318141294
91	P01.EP.EL.CE.0,03	P01	EP	EL	CE	0.03	0	0	0.33723876098651884
92	P01.EP.EL.CE.0,04	P01	EP	EL	CE	0.04	0	0	0.33047308879162474
93	P01.EP.EL.CE.0,05	P01	EP	EL	CE	0.05	0	0	0.32370741659673063
94	P01.EP.EL.CE.0,06	P01	EP	EL	CE	0.060000000000000005	0	0	0.3240477253112385
95	P01.EP.EL.CE.0,07	P01	EP	EL	CE	0.07	0	0	0.3243880340257464
96	P01.EP.EL.CE.0,08	P01	EP	EL	CE	0.08	0	0	0.32472834274025425
97	P01.EP.EL.CE.0,09	P01	EP	EL	CE	0.09	0	0	0.32506865145476216
98	P01.EP.EL.CE.0,1	P01	EP	EL	CE	0.09999999999999999	0	0	0.32540896016927
99	P01.EP.EL.CE.0,11	P01	EP	EL	CE	0.10999999999999999	0	0	0.32574926888377786
100	P01.EP.EL.CE.0,12	P01	EP	EL	CE	0.11999999999999998	0	0	0.3260895775982858
101	P01.EP.EL.CE.0,13	P01	EP	EL	CE	0.12999999999999998	0	0	0.3264298863127936
102	P01.EP.EL.CE.0,14	P01	EP	EL	CE	0.13999999999999999	0	0	0.32677019502730154
103	P01.EP.EL.CE.0,15	P01	EP	EL	CE	0.15	0	0	0.3271105037418094
104	P01.EP.EL.CE.0,16	P01	EP	EL	CE	0.16	0	0	0.32745081245631724
105	P01.EP.EL.CE.0,17	P01	EP	EL	CE	0.17	0	0	0.32779112117082515
106	P01.EP.EL.CE.0,18	P01	EP	EL	CE	0.18000000000000002	0	0	0.328131429885333
107	P01.EP.EL.CE.0,19	P01	EP	EL	CE	0.19000000000000003	0	0	0.3284717385998409
108	P01.EP.EL.CE.0,2	P01	EP	EL	CE	0.20000000000000004	0	0	0.32881204731434877
109	P01.EI.EL.CE.0,01	P01	EI	EL	CE	0.01	0	0	0.23681090325613896
110	P01.EI.EL.CE.0,02	P01	EI	EL	CE	0.02	0	0	0.23050449696902958
111	P01.EI.EL.CE.0,03	P01	EI	EL	CE	0.03	0	0	0.2241980906819202
112	P01.EI.EL.CE.0,04	P01	EI	EL	CE	0.04	0	0	0.21789168439481083
113	P01.EI.EL.CE.0,05	P01	EI	EL	CE	0.05	0	0	0.21158527810770145
114	P01.EI.EL.CE.0,06	P01	EI	EL	CE	0.060000000000000005	0	0	0.2093921282243407
115	P01.EI.EL.CE.0,07	P01	EI	EL	CE	0.07	0	0	0.20719897834097994
116	P01.EI.EL.CE.0,08	P01	EI	EL	CE	0.08	0	0	0.20500582845761922
117	P01.EI.EL.CE.0,09	P01	EI	EL	CE	0.09	0	0	0.20281267857425847
118	P01.EI.EL.CE.0,1	P01	EI	EL	CE	0.09999999999999999	0	0	0.20061952869089772
119	P01.EI.EL.CE.0,11	P01	EI	EL	CE	0.10999999999999999	0	0	0.19842637880753697
120	P01.EI.EL.CE.0,12	P01	EI	EL	CE	0.11999999999999998	0	0	0.19623322892417622
121	P01.EI.EL.CE.0,13	P01	EI	EL	CE	0.12999999999999998	0	0	0.1940400790408155
122	P01.EI.EL.CE.0,14	P01	EI	EL	CE	0.13999999999999999	0	0	0.19184692915745474
123	P01.EI.EL.CE.0,15	P01	EI	EL	CE	0.15	0	0	0.189653779274094
124	P01.EI.EL.CE.0,16	P01	EI	EL	CE	0.16	0	0	0.18746062939073324
125	P01.EI.EL.CE.0,17	P01	EI	EL	CE	0.17	0	0	0.1852674795073725
126	P01.EI.EL.CE.0,18	P01	EI	EL	CE	0.18000000000000002	0	0	0.18307432962401177
127	P01.EI.EL.CE.0,19	P01	EI	EL	CE	0.19000000000000003	0	0	0.180881179740651
128	P01.EI.EL.CE.0,2	P01	EI	EL	CE	0.20000000000000004	0	0	0.17868802985729026
129	P01.EM.EL.CE.0,01	P01	EM	EL	CE	0.01	0	0	0.11469746969138672
130	P01.EM.EL.CE.0,02	P01	EM	EL	CE	0.02	0	0	0.10277200514528612
131	P01.EM.EL.CE.0,03	P01	EM	EL	CE	0.03	0	0	0.09084654059918551
132	P01.EM.EL.CE.0,04	P01	EM	EL	CE	0.04	0	0	0.0789210760530849
133	P01.EM.EL.CE.0,05	P01	EM	EL	CE	0.05	0	0	0.0669956115069843
134	P01.EM.EL.CE.0,06	P01	EM	EL	CE	0.060000000000000005	0	0	0.06717945201865425
135	P01.EM.EL.CE.0,07	P01	EM	EL	CE	0.07	0	0	0.0673632925303242
136	P01.EM.EL.CE.0,08	P01	EM	EL	CE	0.08	0	0	0.06754713304199415
137	P01.EM.EL.CE.0,09	P01	EM	EL	CE	0.09	0	0	0.06773097355366411
138	P01.EM.EL.CE.0,1	P01	EM	EL	CE	0.09999999999999999	0	0	0.06791481406533406
139	P01.EM.EL.CE.0,11	P01	EM	EL	CE	0.10999999999999999	0	0	0.06809865457700401
140	P01.EM.EL.CE.0,12	P01	EM	EL	CE	0.11999999999999998	0	0	0.06828249508867397
141	P01.EM.EL.CE.0,13	P01	EM	EL	CE	0.12999999999999998	0	0	0.06846633560034392
142	P01.EM.EL.CE.0,14	P01	EM	EL	CE	0.13999999999999999	0	0	0.06865017611201388
143	P01.EM.EL.CE.0,15	P01	EM	EL	CE	0.15	0	0	0.06883401662368382
144	P01.EM.EL.CE.0,16	P01	EM	EL	CE	0.16	0	0	0.06901785713535377
145	P01.EM.EL.CE.0,17	P01	EM	EL	CE	0.17	0	0	0.06920169764702373
146	P01.EM.EL.CE.0,18	P01	EM	EL	CE	0.18000000000000002	0	0	0.06938553815869368
147	P01.EM.EL.CE.0,19	P01	EM	EL	CE	0.19000000000000003	0	0	0.06956937867036364
148	P01.EM.EL.CE.0,2	P01	EM	EL	CE	0.20000000000000004	0	0	0.06975321918203359
149	P01.EP.EP.CI.0,01	P01	EP	EP	CI	0.01	0	0	0.062043162735855084
150	P01.EP.EP.CI.0,02	P01	EP	EP	CI	0.02	0	0	0.04655289229117032
151	P01.EP.EP.CI.0,03	P01	EP	EP	CI	0.03	0	0	0.03106262184648556
152	P01.EP.EP.CI.0,04	P01	EP	EP	CI	0.04	0	0	0.029321903358268703
153	P01.EP.EP.CI.0,05	P01	EP	EP	CI	0.05	0	0	0.027581184870051845
154	P01.EP.EP.CI.0,06	P01	EP	EP	CI	0.060000000000000005	0	0	0.025840466381834987
155	P01.EP.EP.CI.0,07	P01	EP	EP	CI	0.07	0	0	0.02409974789361813
156	P01.EP.EP.CI.0,08	P01	EP	EP	CI	0.08	0	0	0.02409974789361813
157	P01.EP.EP.CI.0,09	P01	EP	EP	CI	0.09	0	0	0.02409974789361813
158	P01.EP.EP.CI.0,1	P01	EP	EP	CI	0.09999999999999999	0	0	0.02409974789361813
159	P01.EP.EP.CI.0,11	P01	EP	EP	CI	0.10999999999999999	0	0	0.02409974789361813
160	P01.EP.EP.CI.0,12	P01	EP	EP	CI	0.11999999999999998	0	0	0.02409974789361813
161	P01.EP.EP.CI.0,13	P01	EP	EP	CI	0.12999999999999998	0	0	0.02409974789361813
162	P01.EP.EP.CI.0,14	P01	EP	EP	CI	0.13999999999999999	0	0	0.02409974789361813
163	P01.EP.EP.CI.0,15	P01	EP	EP	CI	0.15	0	0	0.02409974789361813
164	P01.EP.EP.CI.0,16	P01	EP	EP	CI	0.16	0	0	0.02409974789361813
165	P01.EP.EP.CI.0,17	P01	EP	EP	CI	0.17	0	0	0.02409974789361813
166	P01.EP.EP.CI.0,18	P01	EP	EP	CI	0.18000000000000002	0	0	0.02409974789361813
167	P01.EP.EP.CI.0,19	P01	EP	EP	CI	0.19000000000000003	0	0	0.02409974789361813
168	P01.EP.EP.CI.0,2	P01	EP	EP	CI	0.20000000000000004	0	0	0.02409974789361813
169	P01.EI.EI.CI.0,01	P01	EI	EI	CI	0.01	0	0	0.06588616866042152
170	P01.EI.EI.CI.0,02	P01	EI	EI	CI	0.02	0	0	0.050451075575556614
171	P01.EI.EI.CI.0,03	P01	EI	EI	CI	0.03	0	0	0.03501598249069172
172	P01.EI.EI.CI.0,04	P01	EI	EI	CI	0.04	0	0	0.024825240903088026
173	P01.EI.EI.CI.0,05	P01	EI	EI	CI	0.05	0	0	0.014634499315484335
174	P01.EI.EI.CI.0,06	P01	EI	EI	CI	0.060000000000000005	0	0	0.004443757727880644
175	P01.EI.EI.CI.0,07	P01	EI	EI	CI	0.07	0	0	0
176	P01.EI.EI.CI.0,08	P01	EI	EI	CI	0.08	0	0	0
177	P01.EI.EI.CI.0,09	P01	EI	EI	CI	0.09	0	0	0
178	P01.EI.EI.CI.0,1	P01	EI	EI	CI	0.09999999999999999	0	0	0
179	P01.EI.EI.CI.0,11	P01	EI	EI	CI	0.10999999999999999	0	0	0
180	P01.EI.EI.CI.0,12	P01	EI	EI	CI	0.11999999999999998	0	0	0
181	P01.EI.EI.CI.0,13	P01	EI	EI	CI	0.12999999999999998	0	0	0
182	P01.EI.EI.CI.0,14	P01	EI	EI	CI	0.13999999999999999	0	0	0
183	P01.EI.EI.CI.0,15	P01	EI	EI	CI	0.15	0	0	0
184	P01.EI.EI.CI.0,16	P01	EI	EI	CI	0.16	0	0	0
185	P01.EI.EI.CI.0,17	P01	EI	EI	CI	0.17	0	0	0
186	P01.EI.EI.CI.0,18	P01	EI	EI	CI	0.18000000000000002	0	0	0
187	P01.EI.EI.CI.0,19	P01	EI	EI	CI	0.19000000000000003	0	0	0
188	P01.EI.EI.CI.0,2	P01	EI	EI	CI	0.20000000000000004	0	0	0
189	P01.EP.EM.CI.0,01	P01	EP	EM	CI	0.01	0	0	0.07834140384635058
190	P01.EP.EM.CI.0,02	P01	EP	EM	CI	0.02	0	0	0.058469115824311794
191	P01.EP.EM.CI.0,03	P01	EP	EM	CI	0.03	0	0	0.03859682780227303
192	P01.EP.EM.CI.0,04	P01	EP	EM	CI	0.04	0	0	0.02569049429959081
193	P01.EP.EM.CI.0,05	P01	EP	EM	CI	0.05	0	0	0.012784160796908597
194	P01.EP.EM.CI.0,06	P01	EP	EM	CI	0.060000000000000005	0	0	0
195	P01.EP.EM.CI.0,07	P01	EP	EM	CI	0.07	0	0	0
196	P01.EP.EM.CI.0,08	P01	EP	EM	CI	0.08	0	0	0
197	P01.EP.EM.CI.0,09	P01	EP	EM	CI	0.09	0	0	0
198	P01.EP.EM.CI.0,1	P01	EP	EM	CI	0.09999999999999999	0	0	0
199	P01.EP.EM.CI.0,11	P01	EP	EM	CI	0.10999999999999999	0	0	0
200	P01.EP.EM.CI.0,12	P01	EP	EM	CI	0.11999999999999998	0	0	0
201	P01.EP.EM.CI.0,13	P01	EP	EM	CI	0.12999999999999998	0	0	0
202	P01.EP.EM.CI.0,14	P01	EP	EM	CI	0.13999999999999999	0	0	0
203	P01.EP.EM.CI.0,15	P01	EP	EM	CI	0.15	0	0	0
204	P01.EP.EM.CI.0,16	P01	EP	EM	CI	0.16	0	0	0
205	P01.EP.EM.CI.0,17	P01	EP	EM	CI	0.17	0	0	0
206	P01.EP.EM.CI.0,18	P01	EP	EM	CI	0.18000000000000002	0	0	0
207	P01.EP.EM.CI.0,19	P01	EP	EM	CI	0.19000000000000003	0	0	0
208	P01.EP.EM.CI.0,2	P01	EP	EM	CI	0.20000000000000004	0	0	0
209	P01.EI.EM.CI.0,01	P01	EI	EM	CI	0.01	0	0	0.07194633174974019
210	P01.EI.EM.CI.0,02	P01	EI	EM	CI	0.02	0	0	0.05509903503058044
211	P01.EI.EM.CI.0,03	P01	EI	EM	CI	0.03	0	0	0.03825173831142071
212	P01.EI.EM.CI.0,04	P01	EI	EM	CI	0.04	0	0	0.02576655520770444
213	P01.EI.EM.CI.0,05	P01	EI	EM	CI	0.05	0	0	0.013281372103988172
214	P01.EI.EM.CI.0,06	P01	EI	EM	CI	0.060000000000000005	0	0	0.0007961890002719102
215	P01.EI.EM.CI.0,07	P01	EI	EM	CI	0.07	0	0	0
216	P01.EI.EM.CI.0,08	P01	EI	EM	CI	0.08	0	0	0
217	P01.EI.EM.CI.0,09	P01	EI	EM	CI	0.09	0	0	0
218	P01.EI.EM.CI.0,1	P01	EI	EM	CI	0.09999999999999999	0	0	0
219	P01.EI.EM.CI.0,11	P01	EI	EM	CI	0.10999999999999999	0	0	0
220	P01.EI.EM.CI.0,12	P01	EI	EM	CI	0.11999999999999998	0	0	0
221	P01.EI.EM.CI.0,13	P01	EI	EM	CI	0.12999999999999998	0	0	0
222	P01.EI.EM.CI.0,14	P01	EI	EM	CI	0.13999999999999999	0	0	0
223	P01.EI.EM.CI.0,15	P01	EI	EM	CI	0.15	0	0	0
224	P01.EI.EM.CI.0,16	P01	EI	EM	CI	0.16	0	0	0
225	P01.EI.EM.CI.0,17	P01	EI	EM	CI	0.17	0	0	0
226	P01.EI.EM.CI.0,18	P01	EI	EM	CI	0.18000000000000002	0	0	0
227	P01.EI.EM.CI.0,19	P01	EI	EM	CI	0.19000000000000003	0	0	0
228	P01.EI.EM.CI.0,2	P01	EI	EM	CI	0.20000000000000004	0	0	0
229	P01.EP.EL.CI.0,01	P01	EP	EL	CI	0.01	0	0	0.15545403481857534
230	P01.EP.EL.CI.0,02	P01	EP	EL	CI	0.02	0	0	0.11582873751518373
231	P01.EP.EL.CI.0,03	P01	EP	EL	CI	0.03	0	0	0.07620344021179216
232	P01.EP.EL.CI.0,04	P01	EP	EL	CI	0.04	0	0	0.04715960603607218
233	P01.EP.EL.CI.0,05	P01	EP	EL	CI	0.05	0	0	0.01811577186035221
234	P01.EP.EL.CI.0,06	P01	EP	EL	CI	0.060000000000000005	0	0	0
235	P01.EP.EL.CI.0,07	P01	EP	EL	CI	0.07	0	0	0
236	P01.EP.EL.CI.0,08	P01	EP	EL	CI	0.08	0	0	0
237	P01.EP.EL.CI.0,09	P01	EP	EL	CI	0.09	0	0	0
238	P01.EP.EL.CI.0,1	P01	EP	EL	CI	0.09999999999999999	0	0	0
239	P01.EP.EL.CI.0,11	P01	EP	EL	CI	0.10999999999999999	0	0	0
240	P01.EP.EL.CI.0,12	P01	EP	EL	CI	0.11999999999999998	0	0	0
241	P01.EP.EL.CI.0,13	P01	EP	EL	CI	0.12999999999999998	0	0	0
242	P01.EP.EL.CI.0,14	P01	EP	EL	CI	0.13999999999999999	0	0	0
243	P01.EP.EL.CI.0,15	P01	EP	EL	CI	0.15	0	0	0
244	P01.EP.EL.CI.0,16	P01	EP	EL	CI	0.16	0	0	0
245	P01.EP.EL.CI.0,17	P01	EP	EL	CI	0.17	0	0	0
246	P01.EP.EL.CI.0,18	P01	EP	EL	CI	0.18000000000000002	0	0	0
247	P01.EP.EL.CI.0,19	P01	EP	EL	CI	0.19000000000000003	0	0	0
248	P01.EP.EL.CI.0,2	P01	EP	EL	CI	0.20000000000000004	0	0	0
249	P01.EI.EL.CI.0,01	P01	EI	EL	CI	0.01	0	0	0.13961983269840728
250	P01.EI.EL.CI.0,02	P01	EI	EL	CI	0.02	0	0	0.10435743324796952
251	P01.EI.EL.CI.0,03	P01	EI	EL	CI	0.03	0	0	0.0690950337975318
252	P01.EI.EL.CI.0,04	P01	EI	EL	CI	0.04	0	0	0.04648892455769983
253	P01.EI.EL.CI.0,05	P01	EI	EL	CI	0.05	0	0	0.02388281531786786
254	P01.EI.EL.CI.0,06	P01	EI	EL	CI	0.060000000000000005	0	0	0.0012767060780358996
255	P01.EI.EL.CI.0,07	P01	EI	EL	CI	0.07	0	0	0
256	P01.EI.EL.CI.0,08	P01	EI	EL	CI	0.08	0	0	0
257	P01.EI.EL.CI.0,09	P01	EI	EL	CI	0.09	0	0	0
258	P01.EI.EL.CI.0,1	P01	EI	EL	CI	0.09999999999999999	0	0	0
259	P01.EI.EL.CI.0,11	P01	EI	EL	CI	0.10999999999999999	0	0	0
260	P01.EI.EL.CI.0,12	P01	EI	EL	CI	0.11999999999999998	0	0	0
261	P01.EI.EL.CI.0,13	P01	EI	EL	CI	0.12999999999999998	0	0	0
262	P01.EI.EL.CI.0,14	P01	EI	EL	CI	0.13999999999999999	0	0	0
263	P01.EI.EL.CI.0,15	P01	EI	EL	CI	0.15	0	0	0
264	P01.EI.EL.CI.0,16	P01	EI	EL	CI	0.16	0	0	0
265	P01.EI.EL.CI.0,17	P01	EI	EL	CI	0.17	0	0	0
266	P01.EI.EL.CI.0,18	P01	EI	EL	CI	0.18000000000000002	0	0	0
267	P01.EI.EL.CI.0,19	P01	EI	EL	CI	0.19000000000000003	0	0	0
268	P01.EI.EL.CI.0,2	P01	EI	EL	CI	0.20000000000000004	0	0	0
269	P01.EM.EL.CI.0,01	P01	EM	EL	CI	0.01	0	0	0.09806889913365557
270	P01.EM.EL.CI.0,02	P01	EM	EL	CI	0.02	0	0	0.07234193904107211
271	P01.EM.EL.CI.0,03	P01	EM	EL	CI	0.03	0	0	0.04661497894848865
272	P01.EM.EL.CI.0,04	P01	EM	EL	CI	0.04	0	0	0.04309670993213599
273	P01.EM.EL.CI.0,05	P01	EM	EL	CI	0.05	0	0	0.03957844091578333
274	P01.EM.EL.CI.0,06	P01	EM	EL	CI	0.060000000000000005	0	0	0.03606017189943067
275	P01.EM.EL.CI.0,07	P01	EM	EL	CI	0.07	0	0	0.03254190288307801
276	P01.EM.EL.CI.0,08	P01	EM	EL	CI	0.08	0	0	0.03254190288307801
277	P01.EM.EL.CI.0,09	P01	EM	EL	CI	0.09	0	0	0.03254190288307801
278	P01.EM.EL.CI.0,1	P01	EM	EL	CI	0.09999999999999999	0	0	0.03254190288307801
279	P01.EM.EL.CI.0,11	P01	EM	EL	CI	0.10999999999999999	0	0	0.03254190288307801
280	P01.EM.EL.CI.0,12	P01	EM	EL	CI	0.11999999999999998	0	0	0.03254190288307801
281	P01.EM.EL.CI.0,13	P01	EM	EL	CI	0.12999999999999998	0	0	0.03254190288307801
282	P01.EM.EL.CI.0,14	P01	EM	EL	CI	0.13999999999999999	0	0	0.03254190288307801
283	P01.EM.EL.CI.0,15	P01	EM	EL	CI	0.15	0	0	0.03254190288307801
284	P01.EM.EL.CI.0,16	P01	EM	EL	CI	0.16	0	0	0.03254190288307801
285	P01.EM.EL.CI.0,17	P01	EM	EL	CI	0.17	0	0	0.03254190288307801
286	P01.EM.EL.CI.0,18	P01	EM	EL	CI	0.18000000000000002	0	0	0.03254190288307801
287	P01.EM.EL.CI.0,19	P01	EM	EL	CI	0.19000000000000003	0	0	0.03254190288307801
288	P01.EM.EL.CI.0,2	P01	EM	EL	CI	0.20000000000000004	0	0	0.03254190288307801
289	P01.EL.EL.IE.0,01	P01	EL	EL	CI	0.01	0	0	0.15815520039160758
290	P01.EL.EL.CI.0,02	P01	EL	EL	CI	0.02	0	0	0.10510081723304608
291	P01.EL.EL.IE.0,03	P01	EL	EL	CI	0.03	0	0	0.052046434074484615
292	P01.EL.EL.CI.0,04	P01	EL	EL	CI	0.04	0	0	0.05304462439756463
293	P01.EL.EL.CI.0,05	P01	EL	EL	CI	0.05	0	0	0.05404281472064465
294	P01.EL.EL.CI.0,06	P01	EL	EL	CI	0.060000000000000005	0	0	0.05504100504372467
295	P01.EL.EL.CI.0,07	P01	EL	EL	CI	0.07	0	0	0.056039195366804684
296	P01.EL.EL.CI.0,08	P01	EL	EL	CI	0.08	0	0	0.056039195366804684
297	P01.EL.EL.CI.0,09	P01	EL	EL	CI	0.09	0	0	0.056039195366804684
298	P01.EL.EL.IE.0,1	P01	EL	EL	CI	0.09999999999999999	0	0	0.056039195366804684
299	P01.EL.EL.CI.0,11	P01	EL	EL	CI	0.10999999999999999	0	0	0.056039195366804684
300	P01.EL.EL.CI.0,12	P01	EL	EL	CI	0.11999999999999998	0	0	0.056039195366804684
301	P01.EL.EL.CI.0,13	P01	EL	EL	CI	0.12999999999999998	0	0	0.056039195366804684
302	P01.EL.EL.CI.0,14	P01	EL	EL	CI	0.13999999999999999	0	0	0.056039195366804684
303	P01.EL.EL.CI.0,15	P01	EL	EL	CI	0.15	0	0	0.056039195366804684
304	P01.EL.EL.CI.0,16	P01	EL	EL	CI	0.16	0	0	0.056039195366804684
305	P01.EL.EL.CI.0,17	P01	EL	EL	CI	0.17	0	0	0.056039195366804684
306	P01.EL.EL.CI.0,18	P01	EL	EL	CI	0.18000000000000002	0	0	0.056039195366804684
307	P01.EL.EL.CI.0,19	P01	EL	EL	CI	0.19000000000000003	0	0	0.056039195366804684
308	P01.EL.EL.CI.0,2	P01	EL	EL	CI	0.20000000000000004	0	0	0.056039195366804684
309	P02.EP.EP.SA.0	P02	EP	EP	SA	0	0	0	-0.7999592262519863
310	P02.EI.EI.SA.0	P02	EI	EI	SA	0	0	0	-0.5121584175593226
311	P02.EP.EM.SA.0	P02	EP	EM	SA	0	0	0	-0.5508243357464728
312	P02.EI.EM.SA.0	P02	EI	EM	SA	0	0	0	-0.4045139735530263
313	P02.EP.EL.SA.0	P02	EP	EL	SA	0	0	0	-0.5490609263030732
314	P02.EI.EL.SA.0	P02	EI	EL	SA	0	0	0	-0.4006030641096272
315	P02.EM.EL.SA.0	P02	EM	EL	SA	0	0	0	-0.1575321325246044
316	P02.EL.EL.SA.0	P02	EL	EL	SA	0	0	0	-0.16542754876044796
317	P02.EP.EP.CI.0,01	P02	EP	EP	CI	0.01	0	0	-0.24065536308484337
318	P02.EP.EP.CI.0,02	P02	EP	EP	CI	0.02	0	0	-0.17439404408795875
319	P02.EP.EP.CI.0,03	P02	EP	EP	CI	0.03	0	0	-0.10813272509107419
320	P02.EP.EP.CI.0,04	P02	EP	EP	CI	0.04	0	0	-0.06905056757378025
321	P02.EP.EP.CI.0,05	P02	EP	EP	CI	0.05	0	0	-0.029968410056486317
322	P02.EP.EP.CI.0,06	P02	EP	EP	CI	0.060000000000000005	0	0	0
323	P02.EP.EP.CI.0,07	P02	EP	EP	CI	0.07	0	0	0
324	P02.EP.EP.CI.0,08	P02	EP	EP	CI	0.08	0	0	0
325	P02.EP.EP.CI.0,09	P02	EP	EP	CI	0.09	0	0	0
326	P02.EP.EP.CI.0,1	P02	EP	EP	CI	0.09999999999999999	0	0	0
327	P02.EP.EP.CI.0,11	P02	EP	EP	CI	0.10999999999999999	0	0	0
328	P02.EP.EP.CI.0,12	P02	EP	EP	CI	0.11999999999999998	0	0	0
329	P02.EP.EP.CI.0,13	P02	EP	EP	CI	0.12999999999999998	0	0	0
330	P02.EP.EP.CI.0,14	P02	EP	EP	CI	0.13999999999999999	0	0	0
331	P02.EP.EP.CI.0,15	P02	EP	EP	CI	0.15	0	0	0
332	P02.EP.EP.CI.0,16	P02	EP	EP	CI	0.16	0	0	0
333	P02.EP.EP.CI.0,17	P02	EP	EP	CI	0.17	0	0	0
334	P02.EP.EP.CI.0,18	P02	EP	EP	CI	0.18000000000000002	0	0	0
335	P02.EP.EP.CI.0,19	P02	EP	EP	CI	0.19000000000000003	0	0	0
336	P02.EP.EP.CI.0,2	P02	EP	EP	CI	0.20000000000000004	0	0	0
337	P02.EI.EI.CI.0,01	P02	EI	EI	CI	0.01	0	0	-0.2692427779612303
338	P02.EI.EI.CI.0,02	P02	EI	EI	CI	0.02	0	0	-0.2042970626328756
339	P02.EI.EI.CI.0,03	P02	EI	EI	CI	0.03	0	0	-0.13935134730452092
340	P02.EI.EI.CI.0,04	P02	EI	EI	CI	0.04	0	0	-0.07808352126971096
341	P02.EI.EI.CI.0,05	P02	EI	EI	CI	0.05	0	0	-0.016815695234901007
342	P02.EI.EI.CI.0,06	P02	EI	EI	CI	0.060000000000000005	0	0	0
343	P02.EI.EI.CI.0,07	P02	EI	EI	CI	0.07	0	0	0
344	P02.EI.EI.CI.0,08	P02	EI	EI	CI	0.08	0	0	0
345	P02.EI.EI.CI.0,09	P02	EI	EI	CI	0.09	0	0	0
346	P02.EI.EI.CI.0,1	P02	EI	EI	CI	0.09999999999999999	0	0	0
347	P02.EI.EI.CI.0,11	P02	EI	EI	CI	0.10999999999999999	0	0	0
348	P02.EI.EI.CI.0,12	P02	EI	EI	CI	0.11999999999999998	0	0	0
349	P02.EI.EI.CI.0,13	P02	EI	EI	CI	0.12999999999999998	0	0	0
350	P02.EI.EI.CI.0,14	P02	EI	EI	CI	0.13999999999999999	0	0	0
351	P02.EI.EI.CI.0,15	P02	EI	EI	CI	0.15	0	0	0
352	P02.EI.EI.CI.0,16	P02	EI	EI	CI	0.16	0	0	0
353	P02.EI.EI.CI.0,17	P02	EI	EI	CI	0.17	0	0	0
354	P02.EI.EI.CI.0,18	P02	EI	EI	CI	0.18000000000000002	0	0	0
355	P02.EI.EI.CI.0,19	P02	EI	EI	CI	0.19000000000000003	0	0	0
356	P02.EI.EI.CI.0,2	P02	EI	EI	CI	0.20000000000000004	0	0	0
357	P02.EP.EM.CI.0,01	P02	EP	EM	CI	0.01	0	0	-0.2025092487697635
358	P02.EP.EM.CI.0,02	P02	EP	EM	CI	0.02	0	0	-0.1127857503438485
359	P02.EP.EM.CI.0,03	P02	EP	EM	CI	0.03	0	0	-0.02306225191793354
360	P02.EP.EM.CI.0,04	P02	EP	EM	CI	0.04	0	0	-0.06675721367771636
361	P02.EP.EM.CI.0,05	P02	EP	EM	CI	0.05	0	0	-0.11045217543749919
362	P02.EP.EM.CI.0,06	P02	EP	EM	CI	0.060000000000000005	0	0	-0.15414713719728199
363	P02.EP.EM.CI.0,07	P02	EP	EM	CI	0.07	0	0	-0.1978420989570648
364	P02.EP.EM.CI.0,08	P02	EP	EM	CI	0.08	0	0	-0.1978420989570648
365	P02.EP.EM.CI.0,09	P02	EP	EM	CI	0.09	0	0	-0.1978420989570648
366	P02.EP.EM.CI.0,1	P02	EP	EM	CI	0.09999999999999999	0	0	-0.1978420989570648
367	P02.EP.EM.CI.0,11	P02	EP	EM	CI	0.10999999999999999	0	0	-0.1978420989570648
368	P02.EP.EM.CI.0,12	P02	EP	EM	CI	0.11999999999999998	0	0	-0.1978420989570648
369	P02.EP.EM.CI.0,13	P02	EP	EM	CI	0.12999999999999998	0	0	-0.1978420989570648
370	P02.EP.EM.CI.0,14	P02	EP	EM	CI	0.13999999999999999	0	0	-0.1978420989570648
371	P02.EP.EM.CI.0,15	P02	EP	EM	CI	0.15	0	0	-0.1978420989570648
372	P02.EP.EM.CI.0,16	P02	EP	EM	CI	0.16	0	0	-0.1978420989570648
373	P02.EP.EM.CI.0,17	P02	EP	EM	CI	0.17	0	0	-0.1978420989570648
374	P02.EP.EM.CI.0,18	P02	EP	EM	CI	0.18000000000000002	0	0	-0.1978420989570648
375	P02.EP.EM.CI.0,19	P02	EP	EM	CI	0.19000000000000003	0	0	-0.1978420989570648
376	P02.EP.EM.CI.0,2	P02	EP	EM	CI	0.20000000000000004	0	0	-0.1978420989570648
377	P02.EI.EM.CI.0,01	P02	EI	EM	CI	0.01	0	0	-0.2212812115259819
378	P02.EI.EM.CI.0,02	P02	EI	EM	CI	0.02	0	0	-0.14703419977531937
379	P02.EI.EM.CI.0,03	P02	EI	EM	CI	0.03	0	0	-0.07278718802465689
380	P02.EI.EM.CI.0,04	P02	EI	EM	CI	0.04	0	0	-0.07515073589527488
381	P02.EI.EM.CI.0,05	P02	EI	EM	CI	0.05	0	0	-0.07751428376589287
382	P02.EI.EM.CI.0,06	P02	EI	EM	CI	0.060000000000000005	0	0	-0.07987783163651085
383	P02.EI.EM.CI.0,07	P02	EI	EM	CI	0.07	0	0	-0.08224137950712884
384	P02.EI.EM.CI.0,08	P02	EI	EM	CI	0.08	0	0	-0.08224137950712884
385	P02.EI.EM.CI.0,09	P02	EI	EM	CI	0.09	0	0	-0.08224137950712884
386	P02.EI.EM.CI.0,1	P02	EI	EM	CI	0.09999999999999999	0	0	-0.08224137950712884
387	P02.EI.EM.CI.0,11	P02	EI	EM	CI	0.10999999999999999	0	0	-0.08224137950712884
388	P02.EI.EM.CI.0,12	P02	EI	EM	CI	0.11999999999999998	0	0	-0.08224137950712884
389	P02.EI.EM.CI.0,13	P02	EI	EM	CI	0.12999999999999998	0	0	-0.08224137950712884
390	P02.EI.EM.CI.0,14	P02	EI	EM	CI	0.13999999999999999	0	0	-0.08224137950712884
391	P02.EI.EM.CI.0,15	P02	EI	EM	CI	0.15	0	0	-0.08224137950712884
392	P02.EI.EM.CI.0,16	P02	EI	EM	CI	0.16	0	0	-0.08224137950712884
393	P02.EI.EM.CI.0,17	P02	EI	EM	CI	0.17	0	0	-0.08224137950712884
394	P02.EI.EM.CI.0,18	P02	EI	EM	CI	0.18000000000000002	0	0	-0.08224137950712884
395	P02.EI.EM.CI.0,19	P02	EI	EM	CI	0.19000000000000003	0	0	-0.08224137950712884
396	P02.EI.EM.CI.0,2	P02	EI	EM	CI	0.20000000000000004	0	0	-0.08224137950712884
397	P02.EP.EL.CI.0,01	P02	EP	EL	CI	0.01	0	0	-0.14390450412309264
398	P02.EP.EL.CI.0,02	P02	EP	EL	CI	0.02	0	0	-0.065952340175744
399	P02.EP.EL.CI.0,03	P02	EP	EL	CI	0.03	0	0	0
400	P02.EP.EL.CI.0,04	P02	EP	EL	CI	0.04	0	0	0
401	P02.EP.EL.CI.0,05	P02	EP	EL	CI	0.05	0	0	0
402	P02.EP.EL.CI.0,06	P02	EP	EL	CI	0.060000000000000005	0	0	0
403	P02.EP.EL.CI.0,07	P02	EP	EL	CI	0.07	0	0	0
404	P02.EP.EL.CI.0,08	P02	EP	EL	CI	0.08	0	0	0
405	P02.EP.EL.CI.0,09	P02	EP	EL	CI	0.09	0	0	0
406	P02.EP.EL.CI.0,1	P02	EP	EL	CI	0.09999999999999999	0	0	0
407	P02.EP.EL.CI.0,11	P02	EP	EL	CI	0.10999999999999999	0	0	0
408	P02.EP.EL.CI.0,12	P02	EP	EL	CI	0.11999999999999998	0	0	0
409	P02.EP.EL.CI.0,13	P02	EP	EL	CI	0.12999999999999998	0	0	0
410	P02.EP.EL.CI.0,14	P02	EP	EL	CI	0.13999999999999999	0	0	0
411	P02.EP.EL.CI.0,15	P02	EP	EL	CI	0.15	0	0	0
412	P02.EP.EL.CI.0,16	P02	EP	EL	CI	0.16	0	0	0
413	P02.EP.EL.CI.0,17	P02	EP	EL	CI	0.17	0	0	0
414	P02.EP.EL.CI.0,18	P02	EP	EL	CI	0.18000000000000002	0	0	0
415	P02.EP.EL.CI.0,19	P02	EP	EL	CI	0.19000000000000003	0	0	0
416	P02.EP.EL.CI.0,2	P02	EP	EL	CI	0.20000000000000004	0	0	0
417	P02.EI.EL.CI.0,01	P02	EI	EL	CI	0.01	0	0	-0.1685468469028688
418	P02.EI.EL.CI.0,02	P02	EI	EL	CI	0.02	0	0	-0.1263268855628803
419	P02.EI.EL.CI.0,03	P02	EI	EL	CI	0.03	0	0	-0.08410692422289179
420	P02.EI.EL.CI.0,04	P02	EI	EL	CI	0.04	0	0	-0.009511998730586946
421	P02.EI.EL.CI.0,05	P02	EI	EL	CI	0.05	0	0	0
422	P02.EI.EL.CI.0,06	P02	EI	EL	CI	0.060000000000000005	0	0	0
423	P02.EI.EL.CI.0,07	P02	EI	EL	CI	0.07	0	0	0
424	P02.EI.EL.CI.0,08	P02	EI	EL	CI	0.08	0	0	0
425	P02.EI.EL.CI.0,09	P02	EI	EL	CI	0.09	0	0	0
426	P02.EI.EL.CI.0,1	P02	EI	EL	CI	0.09999999999999999	0	0	0
427	P02.EI.EL.CI.0,11	P02	EI	EL	CI	0.10999999999999999	0	0	0
428	P02.EI.EL.CI.0,12	P02	EI	EL	CI	0.11999999999999998	0	0	0
429	P02.EI.EL.CI.0,13	P02	EI	EL	CI	0.12999999999999998	0	0	0
430	P02.EI.EL.CI.0,14	P02	EI	EL	CI	0.13999999999999999	0	0	0
431	P02.EI.EL.CI.0,15	P02	EI	EL	CI	0.15	0	0	0
432	P02.EI.EL.CI.0,16	P02	EI	EL	CI	0.16	0	0	0
433	P02.EI.EL.CI.0,17	P02	EI	EL	CI	0.17	0	0	0
434	P02.EI.EL.CI.0,18	P02	EI	EL	CI	0.18000000000000002	0	0	0
435	P02.EI.EL.CI.0,19	P02	EI	EL	CI	0.19000000000000003	0	0	0
436	P02.EI.EL.CI.0,2	P02	EI	EL	CI	0.20000000000000004	0	0	0
437	P02.EM.EL.CI.0,01	P02	EM	EL	CI	0.01	0	0	0
438	P02.EM.EL.CI.0,02	P02	EM	EL	CI	0.02	0	0	0
439	P02.EM.EL.CI.0,03	P02	EM	EL	CI	0.03	0	0	-0.1476187914050603
440	P02.EM.EL.CI.0,04	P02	EM	EL	CI	0.04	0	0	-0.09398025434213711
441	P02.EM.EL.CI.0,05	P02	EM	EL	CI	0.05	0	0	-0.04034171727921404
442	P02.EM.EL.CI.0,06	P02	EM	EL	CI	0.060000000000000005	0	0	0
443	P02.EM.EL.CI.0,07	P02	EM	EL	CI	0.07	0	0	0
444	P02.EM.EL.CI.0,08	P02	EM	EL	CI	0.08	0	0	0
445	P02.EM.EL.CI.0,09	P02	EM	EL	CI	0.09	0	0	0
446	P02.EM.EL.CI.0,1	P02	EM	EL	CI	0.09999999999999999	0	0	0
447	P02.EM.EL.CI.0,11	P02	EM	EL	CI	0.10999999999999999	0	0	0
448	P02.EM.EL.CI.0,12	P02	EM	EL	CI	0.11999999999999998	0	0	0
449	P02.EM.EL.CI.0,13	P02	EM	EL	CI	0.12999999999999998	0	0	0
450	P02.EM.EL.CI.0,14	P02	EM	EL	CI	0.13999999999999999	0	0	0
451	P02.EM.EL.CI.0,15	P02	EM	EL	CI	0.15	0	0	0
452	P02.EM.EL.CI.0,16	P02	EM	EL	CI	0.16	0	0	0
453	P02.EM.EL.CI.0,17	P02	EM	EL	CI	0.17	0	0	0
454	P02.EM.EL.CI.0,18	P02	EM	EL	CI	0.18000000000000002	0	0	0
455	P02.EM.EL.CI.0,19	P02	EM	EL	CI	0.19000000000000003	0	0	0
456	P02.EM.EL.CI.0,2	P02	EM	EL	CI	0.20000000000000004	0	0	0
457	P02.EP.EP.CE.0,01	P02	EP	EP	CE	0.01	0	0	-0.544883390977744
458	P02.EP.EP.CE.0,02	P02	EP	EP	CE	0.02	0	0	-0.47410156079318766
459	P02.EP.EP.CE.0,03	P02	EP	EP	CE	0.03	0	0	-0.40331973060863147
460	P02.EP.EP.CE.0,04	P02	EP	EP	CE	0.04	0	0	-0.33253790042407516
461	P02.EP.EP.CE.0,05	P02	EP	EP	CE	0.05	0	0	-0.26175607023951897
462	P02.EP.EP.CE.0,06	P02	EP	EP	CE	0.060000000000000005	0	0	-0.24499173739394847
463	P02.EP.EP.CE.0,07	P02	EP	EP	CE	0.07	0	0	-0.22822740454837795
464	P02.EP.EP.CE.0,08	P02	EP	EP	CE	0.08	0	0	-0.21146307170280745
465	P02.EP.EP.CE.0,09	P02	EP	EP	CE	0.09	0	0	-0.19469873885723696
466	P02.EP.EP.CE.0,1	P02	EP	EP	CE	0.09999999999999999	0	0	-0.17793440601166646
467	P02.EP.EP.CE.0,11	P02	EP	EP	CE	0.10999999999999999	0	0	-0.16117007316609594
468	P02.EP.EP.CE.0,12	P02	EP	EP	CE	0.11999999999999998	0	0	-0.14440574032052544
469	P02.EP.EP.CE.0,13	P02	EP	EP	CE	0.12999999999999998	0	0	-0.12764140747495495
470	P02.EP.EP.CE.0,14	P02	EP	EP	CE	0.13999999999999999	0	0	-0.11087707462938443
471	P02.EP.EP.CE.0,15	P02	EP	EP	CE	0.15	0	0	-0.0941127417838139
472	P02.EP.EP.CE.0,16	P02	EP	EP	CE	0.16	0	0	-0.07734840893824341
473	P02.EP.EP.CE.0,17	P02	EP	EP	CE	0.17	0	0	-0.060584076092672856
474	P02.EP.EP.CE.0,18	P02	EP	EP	CE	0.18000000000000002	0	0	-0.04381974324710236
475	P02.EP.EP.CE.0,19	P02	EP	EP	CE	0.19000000000000003	0	0	-0.02705541040153181
476	P02.EP.EP.CE.0,2	P02	EP	EP	CE	0.20000000000000004	0	0	-0.010291077555961314
477	P02.EI.EI.CE.0,01	P02	EI	EI	CE	0.01	0	0	-0.42443629580701536
478	P02.EI.EI.CE.0,02	P02	EI	EI	CE	0.02	0	0	-0.3770960335547274
479	P02.EI.EI.CE.0,03	P02	EI	EI	CE	0.03	0	0	-0.3297557713024394
480	P02.EI.EI.CE.0,04	P02	EI	EI	CE	0.04	0	0	-0.2824155090501514
481	P02.EI.EI.CE.0,05	P02	EI	EI	CE	0.05	0	0	-0.2350752467978634
482	P02.EI.EI.CE.0,06	P02	EI	EI	CE	0.060000000000000005	0	0	-0.22148872242521586
483	P02.EI.EI.CE.0,07	P02	EI	EI	CE	0.07	0	0	-0.20790219805256832
484	P02.EI.EI.CE.0,08	P02	EI	EI	CE	0.08	0	0	-0.1943156736799208
485	P02.EI.EI.CE.0,09	P02	EI	EI	CE	0.09	0	0	-0.18072914930727327
486	P02.EI.EI.CE.0,1	P02	EI	EI	CE	0.09999999999999999	0	0	-0.16714262493462573
487	P02.EI.EI.CE.0,11	P02	EI	EI	CE	0.10999999999999999	0	0	-0.15355610056197821
488	P02.EI.EI.CE.0,12	P02	EI	EI	CE	0.11999999999999998	0	0	-0.13996957618933067
489	P02.EI.EI.CE.0,13	P02	EI	EI	CE	0.12999999999999998	0	0	-0.12638305181668316
490	P02.EI.EI.CE.0,14	P02	EI	EI	CE	0.13999999999999999	0	0	-0.11279652744403562
491	P02.EI.EI.CE.0,15	P02	EI	EI	CE	0.15	0	0	-0.09921000307138805
492	P02.EI.EI.CE.0,16	P02	EI	EI	CE	0.16	0	0	-0.08562347869874051
493	P02.EI.EI.CE.0,17	P02	EI	EI	CE	0.17	0	0	-0.07203695432609297
494	P02.EI.EI.CE.0,18	P02	EI	EI	CE	0.18000000000000002	0	0	-0.05845042995344543
495	P02.EI.EI.CE.0,19	P02	EI	EI	CE	0.19000000000000003	0	0	-0.04486390558079789
496	P02.EI.EI.CE.0,2	P02	EI	EI	CE	0.20000000000000004	0	0	-0.03127738120815032
497	P02.EP.EM.CE.0,01	P02	EP	EM	CE	0.01	0	0	-0.4372185266626638
498	P02.EP.EM.CE.0,02	P02	EP	EM	CE	0.02	0	0	-0.3736772372699305
499	P02.EP.EM.CE.0,03	P02	EP	EM	CE	0.03	0	0	-0.3101359478771972
500	P02.EP.EM.CE.0,04	P02	EP	EM	CE	0.04	0	0	-0.24659465848446394
501	P02.EP.EM.CE.0,05	P02	EP	EM	CE	0.05	0	0	-0.18305336909173064
502	P02.EP.EM.CE.0,06	P02	EP	EM	CE	0.060000000000000005	0	0	-0.17611590569650504
503	P02.EP.EM.CE.0,07	P02	EP	EM	CE	0.07	0	0	-0.16917844230127943
504	P02.EP.EM.CE.0,08	P02	EP	EM	CE	0.08	0	0	-0.16224097890605382
505	P02.EP.EM.CE.0,09	P02	EP	EM	CE	0.09	0	0	-0.15530351551082822
506	P02.EP.EM.CE.0,1	P02	EP	EM	CE	0.09999999999999999	0	0	-0.1483660521156026
507	P02.EP.EM.CE.0,11	P02	EP	EM	CE	0.10999999999999999	0	0	-0.141428588720377
508	P02.EP.EM.CE.0,12	P02	EP	EM	CE	0.11999999999999998	0	0	-0.1344911253251514
509	P02.EP.EM.CE.0,13	P02	EP	EM	CE	0.12999999999999998	0	0	-0.1275536619299258
510	P02.EP.EM.CE.0,14	P02	EP	EM	CE	0.13999999999999999	0	0	-0.1206161985347002
511	P02.EP.EM.CE.0,15	P02	EP	EM	CE	0.15	0	0	-0.11367873513947457
512	P02.EP.EM.CE.0,16	P02	EP	EM	CE	0.16	0	0	-0.10674127174424897
513	P02.EP.EM.CE.0,17	P02	EP	EM	CE	0.17	0	0	-0.09980380834902335
514	P02.EP.EM.CE.0,18	P02	EP	EM	CE	0.18000000000000002	0	0	-0.09286634495379774
515	P02.EP.EM.CE.0,19	P02	EP	EM	CE	0.19000000000000003	0	0	-0.08592888155857212
516	P02.EP.EM.CE.0,2	P02	EP	EM	CE	0.20000000000000004	0	0	-0.07899141816334651
517	P02.EI.EM.CE.0,01	P02	EI	EM	CE	0.01	0	0	-0.34006222937176744
518	P02.EI.EM.CE.0,02	P02	EI	EM	CE	0.02	0	0	-0.2982467863715514
519	P02.EI.EM.CE.0,03	P02	EI	EM	CE	0.03	0	0	-0.25643134337133533
520	P02.EI.EM.CE.0,04	P02	EI	EM	CE	0.04	0	0	-0.21461590037111927
521	P02.EI.EM.CE.0,05	P02	EI	EM	CE	0.05	0	0	-0.17280045737090322
522	P02.EI.EM.CE.0,06	P02	EI	EM	CE	0.060000000000000005	0	0	-0.16646358380876045
523	P02.EI.EM.CE.0,07	P02	EI	EM	CE	0.07	0	0	-0.16012671024661768
524	P02.EI.EM.CE.0,08	P02	EI	EM	CE	0.08	0	0	-0.15378983668447493
525	P02.EI.EM.CE.0,09	P02	EI	EM	CE	0.09	0	0	-0.14745296312233216
526	P02.EI.EM.CE.0,1	P02	EI	EM	CE	0.09999999999999999	0	0	-0.1411160895601894
527	P02.EI.EM.CE.0,11	P02	EI	EM	CE	0.10999999999999999	0	0	-0.13477921599804665
528	P02.EI.EM.CE.0,12	P02	EI	EM	CE	0.11999999999999998	0	0	-0.12844234243590388
529	P02.EI.EM.CE.0,13	P02	EI	EM	CE	0.12999999999999998	0	0	-0.12210546887376111
530	P02.EI.EM.CE.0,14	P02	EI	EM	CE	0.13999999999999999	0	0	-0.11576859531161834
531	P02.EI.EM.CE.0,15	P02	EI	EM	CE	0.15	0	0	-0.10943172174947557
532	P02.EI.EM.CE.0,16	P02	EI	EM	CE	0.16	0	0	-0.1030948481873328
533	P02.EI.EM.CE.0,17	P02	EI	EM	CE	0.17	0	0	-0.09675797462519004
534	P02.EI.EM.CE.0,18	P02	EI	EM	CE	0.18000000000000002	0	0	-0.09042110106304727
535	P02.EI.EM.CE.0,19	P02	EI	EM	CE	0.19000000000000003	0	0	-0.0840842275009045
536	P02.EI.EM.CE.0,2	P02	EI	EM	CE	0.20000000000000004	0	0	-0.07774735393876173
537	P02.EP.EL.CE.0,01	P02	EP	EL	CE	0.01	0	0	-0.32187579596244253
538	P02.EP.EL.CE.0,02	P02	EP	EL	CE	0.02	0	0	-0.27382394154452283
539	P02.EP.EL.CE.0,03	P02	EP	EL	CE	0.03	0	0	-0.22577208712660315
540	P02.EP.EL.CE.0,04	P02	EP	EL	CE	0.04	0	0	-0.17772023270868342
541	P02.EP.EL.CE.0,05	P02	EP	EL	CE	0.05	0	0	-0.12966837829076372
542	P02.EP.EL.CE.0,06	P02	EP	EL	CE	0.060000000000000005	0	0	-0.12430320098928538
543	P02.EP.EL.CE.0,07	P02	EP	EL	CE	0.07	0	0	-0.11893802368780704
544	P02.EP.EL.CE.0,08	P02	EP	EL	CE	0.08	0	0	-0.1135728463863287
545	P02.EP.EL.CE.0,09	P02	EP	EL	CE	0.09	0	0	-0.10820766908485036
546	P02.EP.EL.CE.0,1	P02	EP	EL	CE	0.09999999999999999	0	0	-0.10284249178337201
547	P02.EP.EL.CE.0,11	P02	EP	EL	CE	0.10999999999999999	0	0	-0.09747731448189367
548	P02.EP.EL.CE.0,12	P02	EP	EL	CE	0.11999999999999998	0	0	-0.09211213718041535
549	P02.EP.EL.CE.0,13	P02	EP	EL	CE	0.12999999999999998	0	0	-0.086746959878937
550	P02.EP.EL.CE.0,14	P02	EP	EL	CE	0.13999999999999999	0	0	-0.08138178257745866
551	P02.EP.EL.CE.0,15	P02	EP	EL	CE	0.15	0	0	-0.07601660527598031
552	P02.EP.EL.CE.0,16	P02	EP	EL	CE	0.16	0	0	-0.07065142797450197
553	P02.EP.EL.CE.0,17	P02	EP	EL	CE	0.17	0	0	-0.06528625067302363
554	P02.EP.EL.CE.0,18	P02	EP	EL	CE	0.18000000000000002	0	0	-0.05992107337154527
555	P02.EP.EL.CE.0,19	P02	EP	EL	CE	0.19000000000000003	0	0	-0.05455589607006693
556	P02.EP.EL.CE.0,2	P02	EP	EL	CE	0.20000000000000004	0	0	-0.049190718768588576
557	P02.EI.EL.CE.0,01	P02	EI	EL	CE	0.01	0	0	-0.24272824867154608
558	P02.EI.EL.CE.0,02	P02	EI	EL	CE	0.02	0	0	-0.21360331374429886
559	P02.EI.EL.CE.0,03	P02	EI	EL	CE	0.03	0	0	-0.18447837881705165
560	P02.EI.EL.CE.0,04	P02	EI	EL	CE	0.04	0	0	-0.15535344388980443
561	P02.EI.EL.CE.0,05	P02	EI	EL	CE	0.05	0	0	-0.12622850896255722
562	P02.EI.EL.CE.0,06	P02	EI	EL	CE	0.060000000000000005	0	0	-0.12069031301563754
563	P02.EI.EL.CE.0,07	P02	EI	EL	CE	0.07	0	0	-0.11515211706871789
564	P02.EI.EL.CE.0,08	P02	EI	EL	CE	0.08	0	0	-0.10961392112179821
565	P02.EI.EL.CE.0,09	P02	EI	EL	CE	0.09	0	0	-0.10407572517487856
566	P02.EI.EL.CE.0,1	P02	EI	EL	CE	0.09999999999999999	0	0	-0.09853752922795889
567	P02.EI.EL.CE.0,11	P02	EI	EL	CE	0.10999999999999999	0	0	-0.09299933328103924
568	P02.EI.EL.CE.0,12	P02	EI	EL	CE	0.11999999999999998	0	0	-0.08746113733411956
569	P02.EI.EL.CE.0,13	P02	EI	EL	CE	0.12999999999999998	0	0	-0.0819229413871999
570	P02.EI.EL.CE.0,14	P02	EI	EL	CE	0.13999999999999999	0	0	-0.07638474544028023
571	P02.EI.EL.CE.0,15	P02	EI	EL	CE	0.15	0	0	-0.07084654949336056
572	P02.EI.EL.CE.0,16	P02	EI	EL	CE	0.16	0	0	-0.06530835354644089
573	P02.EI.EL.CE.0,17	P02	EI	EL	CE	0.17	0	0	-0.059770157599521215
574	P02.EI.EL.CE.0,18	P02	EI	EL	CE	0.18000000000000002	0	0	-0.05423196165260155
575	P02.EI.EL.CE.0,19	P02	EI	EL	CE	0.19000000000000003	0	0	-0.048693765705681874
576	P02.EI.EL.CE.0,2	P02	EI	EL	CE	0.20000000000000004	0	0	-0.0431555697587622
577	P02.EM.EL.CE.0,01	P02	EM	EL	CE	0.01	0	0	-0.08557589264292842
578	P02.EM.EL.CE.0,02	P02	EM	EL	CE	0.02	0	0	-0.08749336442693639
579	P02.EM.EL.CE.0,03	P02	EM	EL	CE	0.03	0	0	-0.08941083621094437
580	P02.EM.EL.CE.0,04	P02	EM	EL	CE	0.04	0	0	-0.09132830799495234
581	P02.EM.EL.CE.0,05	P02	EM	EL	CE	0.05	0	0	-0.09324577977896031
582	P02.EM.EL.CE.0,06	P02	EM	EL	CE	0.060000000000000005	0	0	-0.08902121648269914
583	P02.EM.EL.CE.0,07	P02	EM	EL	CE	0.07	0	0	-0.08479665318643796
584	P02.EM.EL.CE.0,08	P02	EM	EL	CE	0.08	0	0	-0.08057208989017678
585	P02.EM.EL.CE.0,09	P02	EM	EL	CE	0.09	0	0	-0.07634752659391561
586	P02.EM.EL.CE.0,1	P02	EM	EL	CE	0.09999999999999999	0	0	-0.07212296329765444
587	P02.EM.EL.CE.0,11	P02	EM	EL	CE	0.10999999999999999	0	0	-0.06789840000139327
588	P02.EM.EL.CE.0,12	P02	EM	EL	CE	0.11999999999999998	0	0	-0.0636738367051321
589	P02.EM.EL.CE.0,13	P02	EM	EL	CE	0.12999999999999998	0	0	-0.05944927340887093
590	P02.EM.EL.CE.0,14	P02	EM	EL	CE	0.13999999999999999	0	0	-0.05522471011260975
591	P02.EM.EL.CE.0,15	P02	EM	EL	CE	0.15	0	0	-0.05100014681634857
592	P02.EM.EL.CE.0,16	P02	EM	EL	CE	0.16	0	0	-0.046775583520087385
593	P02.EM.EL.CE.0,17	P02	EM	EL	CE	0.17	0	0	-0.042551020223826216
594	P02.EM.EL.CE.0,18	P02	EM	EL	CE	0.18000000000000002	0	0	-0.038326456927565034
595	P02.EM.EL.CE.0,19	P02	EM	EL	CE	0.19000000000000003	0	0	-0.03410189363130385
596	P02.EM.EL.CE.0,2	P02	EM	EL	CE	0.20000000000000004	0	0	-0.02987733033504268
597	P02.EL.EL.IE.0,01	P02	EL	EL	CE	0.01	0	0	-0.2864858884537691
598	P02.EL.EL.CE.0,02	P02	EL	EL	CE	0.02	0	0	-0.23273050838263976
599	P02.EL.EL.CE.0,03	P02	EL	EL	CE	0.03	0	0	-0.17897512831151044
600	P02.EL.EL.CE.0,04	P02	EL	EL	CE	0.04	0	0	-0.12521974824038107
601	P02.EL.EL.IE.0,05	P02	EL	EL	CE	0.05	0	0	-0.07146436816925172
602	P02.EL.EL.CE.0,06	P02	EL	EL	CE	0.060000000000000005	0	0	-0.06722907800260924
603	P02.EL.EL.CE.0,07	P02	EL	EL	CE	0.07	0	0	-0.06299378783596676
604	P02.EL.EL.CE.0,08	P02	EL	EL	CE	0.08	0	0	-0.05875849766932428
605	P02.EL.EL.CE.0,09	P02	EL	EL	CE	0.09	0	0	-0.0545232075026818
606	P02.EL.EL.IE.0,1	P02	EL	EL	CE	0.09999999999999999	0	0	-0.05028791733603933
607	P02.EL.EL.CE.0,11	P02	EL	EL	CE	0.10999999999999999	0	0	-0.04605262716939685
608	P02.EL.EL.CE.0,12	P02	EL	EL	CE	0.11999999999999998	0	0	-0.04181733700275437
609	P02.EL.EL.CE.0,13	P02	EL	EL	CE	0.12999999999999998	0	0	-0.03758204683611189
610	P02.EL.EL.CE.0,14	P02	EL	EL	CE	0.13999999999999999	0	0	-0.03334675666946941
611	P02.EL.EL.CE.0,15	P02	EL	EL	CE	0.15	0	0	-0.02911146650282692
612	P02.EL.EL.CE.0,16	P02	EL	EL	CE	0.16	0	0	-0.02487617633618444
613	P02.EL.EL.CE.0,17	P02	EL	EL	CE	0.17	0	0	-0.02064088616954196
614	P02.EL.EL.CE.0,18	P02	EL	EL	CE	0.18000000000000002	0	0	-0.016405596002899467
615	P02.EL.EL.CE.0,19	P02	EL	EL	CE	0.19000000000000003	0	0	-0.012170305836256987
616	P02.EL.EL.CE.0,2	P02	EL	EL	CE	0.20000000000000004	0	0	-0.007935015669614506
617	P03.EP.EP.SA.0	P03	EP	EP	SA	0	0	0	0.18636453972381517
618	P03.EI.EM.SA.0	P03	EI	EM	SA	0	0	0	0.12385683250599389
619	P03.EP.EL.SA.0	P03	EP	EL	SA	0	0	0	0.1387354732298629
620	P03.EI.EL.SA.0	P03	EI	EL	SA	0	0	0	0.12458933250599458
621	P03.EM.EL.SA.0	P03	EM	EL	SA	0	0	0	0.0711295476303957
622	P03.EL.EL.SA.0	P03	EL	EL	SA	0	0	0	0.09959632867757318
623	P03.EP.EP.CI.0,01	P03	EP	EP	CI	0.01	0	0	0.12261133009325498
624	P03.EP.EP.CI.0,02	P03	EP	EP	CI	0.02	0	0	0.061305665046627475
625	P03.EP.EP.CI.0,03	P03	EP	EP	CI	0.03	0	0	0
626	P03.EP.EP.CI.0,04	P03	EP	EP	CI	0.04	0	0	0.14668175555044738
627	P03.EP.EP.CI.0,05	P03	EP	EP	CI	0.05	0	0	0.29336351110089476
628	P03.EP.EP.CI.0,06	P03	EP	EP	CI	0.060000000000000005	0	0	0.44004526665134214
629	P03.EP.EP.CI.0,07	P03	EP	EP	CI	0.07	0	0	0.5867270222017896
630	P03.EP.EP.CI.0,08	P03	EP	EP	CI	0.08	0	0	0.5867270222017896
631	P03.EP.EP.CI.0,09	P03	EP	EP	CI	0.09	0	0	0.5867270222017896
632	P03.EP.EP.CI.0,1	P03	EP	EP	CI	0.09999999999999999	0	0	0.5867270222017896
633	P03.EP.EP.CI.0,11	P03	EP	EP	CI	0.10999999999999999	0	0	0.5867270222017896
634	P03.EP.EP.CI.0,12	P03	EP	EP	CI	0.11999999999999998	0	0	0.5867270222017896
635	P03.EP.EP.CI.0,13	P03	EP	EP	CI	0.12999999999999998	0	0	0.5867270222017896
636	P03.EP.EP.CI.0,14	P03	EP	EP	CI	0.13999999999999999	0	0	0.5867270222017896
637	P03.EP.EP.CI.0,15	P03	EP	EP	CI	0.15	0	0	0.5867270222017896
638	P03.EP.EP.CI.0,16	P03	EP	EP	CI	0.16	0	0	0.5867270222017896
639	P03.EP.EP.CI.0,17	P03	EP	EP	CI	0.17	0	0	0.5867270222017896
640	P03.EP.EP.CI.0,18	P03	EP	EP	CI	0.18000000000000002	0	0	0.5867270222017896
641	P03.EP.EP.CI.0,19	P03	EP	EP	CI	0.19000000000000003	0	0	0.5867270222017896
642	P03.EP.EP.CI.0,2	P03	EP	EP	CI	0.20000000000000004	0	0	0.5867270222017896
643	P03.EI.EI.CI.0,01	P03	EI	EI	CI	0.01	0	0	0.1132597757351328
644	P03.EI.EI.CI.0,02	P03	EI	EI	CI	0.02	0	0	0.056629887867566384
645	P03.EI.EI.CI.0,03	P03	EI	EI	CI	0.03	0	0	0
646	P03.EI.EI.CI.0,04	P03	EI	EI	CI	0.04	0	0	0.11519202140045992
647	P03.EI.EI.CI.0,05	P03	EI	EI	CI	0.05	0	0	0.23038404280091984
648	P03.EI.EI.CI.0,06	P03	EI	EI	CI	0.060000000000000005	0	0	0.34557606420137976
649	P03.EI.EI.CI.0,07	P03	EI	EI	CI	0.07	0	0	0.4607680856018397
650	P03.EI.EI.CI.0,08	P03	EI	EI	CI	0.08	0	0	0.4607680856018397
651	P03.EI.EI.CI.0,09	P03	EI	EI	CI	0.09	0	0	0.4607680856018397
652	P03.EI.EI.CI.0,1	P03	EI	EI	CI	0.09999999999999999	0	0	0.4607680856018397
653	P03.EI.EI.CI.0,11	P03	EI	EI	CI	0.10999999999999999	0	0	0.4607680856018397
654	P03.EI.EI.CI.0,12	P03	EI	EI	CI	0.11999999999999998	0	0	0.4607680856018397
655	P03.EI.EI.CI.0,13	P03	EI	EI	CI	0.12999999999999998	0	0	0.4607680856018397
656	P03.EI.EI.CI.0,14	P03	EI	EI	CI	0.13999999999999999	0	0	0.4607680856018397
657	P03.EI.EI.CI.0,15	P03	EI	EI	CI	0.15	0	0	0.4607680856018397
658	P03.EI.EI.CI.0,16	P03	EI	EI	CI	0.16	0	0	0.4607680856018397
659	P03.EI.EI.CI.0,17	P03	EI	EI	CI	0.17	0	0	0.4607680856018397
660	P03.EI.EI.CI.0,18	P03	EI	EI	CI	0.18000000000000002	0	0	0.4607680856018397
661	P03.EI.EI.CI.0,19	P03	EI	EI	CI	0.19000000000000003	0	0	0.4607680856018397
662	P03.EI.EI.CI.0,2	P03	EI	EI	CI	0.20000000000000004	0	0	0.4607680856018397
663	P03.EP.EM.CI.0,01	P03	EP	EM	CI	0.01	0	0	0.07772514982550494
664	P03.EP.EM.CI.0,02	P03	EP	EM	CI	0.02	0	0	0.038862574912752454
665	P03.EP.EM.CI.0,03	P03	EP	EM	CI	0.03	0	0	0
666	P03.EP.EM.CI.0,04	P03	EP	EM	CI	0.04	0	0	0.06333396515991893
667	P03.EP.EM.CI.0,05	P03	EP	EM	CI	0.05	0	0	0.12666793031983795
668	P03.EP.EM.CI.0,06	P03	EP	EM	CI	0.060000000000000005	0	0	0.1900018954797569
669	P03.EP.EM.CI.0,07	P03	EP	EM	CI	0.07	0	0	0.25333586063967584
670	P03.EP.EM.CI.0,08	P03	EP	EM	CI	0.08	0	0	0.25333586063967584
671	P03.EP.EM.CI.0,09	P03	EP	EM	CI	0.09	0	0	0.25333586063967584
672	P03.EP.EM.CI.0,1	P03	EP	EM	CI	0.09999999999999999	0	0	0.25333586063967584
673	P03.EP.EM.CI.0,11	P03	EP	EM	CI	0.10999999999999999	0	0	0.25333586063967584
674	P03.EP.EM.CI.0,12	P03	EP	EM	CI	0.11999999999999998	0	0	0.25333586063967584
675	P03.EP.EM.CI.0,13	P03	EP	EM	CI	0.12999999999999998	0	0	0.25333586063967584
676	P03.EP.EM.CI.0,14	P03	EP	EM	CI	0.13999999999999999	0	0	0.25333586063967584
677	P03.EP.EM.CI.0,15	P03	EP	EM	CI	0.15	0	0	0.25333586063967584
678	P03.EP.EM.CI.0,16	P03	EP	EM	CI	0.16	0	0	0.25333586063967584
679	P03.EP.EM.CI.0,17	P03	EP	EM	CI	0.17	0	0	0.25333586063967584
680	P03.EP.EM.CI.0,18	P03	EP	EM	CI	0.18000000000000002	0	0	0.25333586063967584
681	P03.EP.EM.CI.0,19	P03	EP	EM	CI	0.19000000000000003	0	0	0.25333586063967584
682	P03.EP.EM.CI.0,2	P03	EP	EM	CI	0.20000000000000004	0	0	0.25333586063967584
683	P03.EI.EM.CI.0,01	P03	EI	EM	CI	0.01	0	0	0.07710294534959594
684	P03.EI.EM.CI.0,02	P03	EI	EM	CI	0.02	0	0	0.03855147267479796
685	P03.EI.EM.CI.0,03	P03	EI	EM	CI	0.03	0	0	0
686	P03.EI.EM.CI.0,04	P03	EI	EM	CI	0.04	0	0	0.05834585981668827
687	P03.EI.EM.CI.0,05	P03	EI	EM	CI	0.05	0	0	0.11669171963337654
688	P03.EI.EM.CI.0,06	P03	EI	EM	CI	0.060000000000000005	0	0	0.17503757945006482
689	P03.EI.EM.CI.0,07	P03	EI	EM	CI	0.07	0	0	0.2333834392667531
690	P03.EI.EM.CI.0,08	P03	EI	EM	CI	0.08	0	0	0.2333834392667531
691	P03.EI.EM.CI.0,09	P03	EI	EM	CI	0.09	0	0	0.2333834392667531
692	P03.EI.EM.CI.0,1	P03	EI	EM	CI	0.09999999999999999	0	0	0.2333834392667531
693	P03.EI.EM.CI.0,11	P03	EI	EM	CI	0.10999999999999999	0	0	0.2333834392667531
694	P03.EI.EM.CI.0,12	P03	EI	EM	CI	0.11999999999999998	0	0	0.2333834392667531
695	P03.EI.EM.CI.0,13	P03	EI	EM	CI	0.12999999999999998	0	0	0.2333834392667531
696	P03.EI.EM.CI.0,14	P03	EI	EM	CI	0.13999999999999999	0	0	0.2333834392667531
697	P03.EI.EM.CI.0,15	P03	EI	EM	CI	0.15	0	0	0.2333834392667531
698	P03.EI.EM.CI.0,16	P03	EI	EM	CI	0.16	0	0	0.2333834392667531
699	P03.EI.EM.CI.0,17	P03	EI	EM	CI	0.17	0	0	0.2333834392667531
700	P03.EI.EM.CI.0,18	P03	EI	EM	CI	0.18000000000000002	0	0	0.2333834392667531
701	P03.EI.EM.CI.0,19	P03	EI	EM	CI	0.19000000000000003	0	0	0.2333834392667531
702	P03.EI.EM.CI.0,2	P03	EI	EM	CI	0.20000000000000004	0	0	0.2333834392667531
703	P03.EP.EL.CI.0,01	P03	EP	EL	CI	0.01	0	0	0.07975514982550447
704	P03.EP.EL.CI.0,02	P03	EP	EL	CI	0.02	0	0	0.03987757491275222
705	P03.EP.EL.CI.0,03	P03	EP	EL	CI	0.03	0	0	0
706	P03.EP.EL.CI.0,04	P03	EP	EL	CI	0.04	0	0	0.0912364651599189
707	P03.EP.EL.CI.0,05	P03	EP	EL	CI	0.05	0	0	0.1824729303198378
708	P03.EP.EL.CI.0,06	P03	EP	EL	CI	0.060000000000000005	0	0	0.27370939547975665
709	P03.EP.EL.CI.0,07	P03	EP	EL	CI	0.07	0	0	0.36494586063967555
710	P03.EP.EL.CI.0,08	P03	EP	EL	CI	0.08	0	0	0.36494586063967555
711	P03.EP.EL.CI.0,09	P03	EP	EL	CI	0.09	0	0	0.36494586063967555
712	P03.EP.EL.CI.0,1	P03	EP	EL	CI	0.09999999999999999	0	0	0.36494586063967555
713	P03.EP.EL.CI.0,11	P03	EP	EL	CI	0.10999999999999999	0	0	0.36494586063967555
714	P03.EP.EL.CI.0,12	P03	EP	EL	CI	0.11999999999999998	0	0	0.36494586063967555
715	P03.EP.EL.CI.0,13	P03	EP	EL	CI	0.12999999999999998	0	0	0.36494586063967555
716	P03.EP.EL.CI.0,14	P03	EP	EL	CI	0.13999999999999999	0	0	0.36494586063967555
717	P03.EP.EL.CI.0,15	P03	EP	EL	CI	0.15	0	0	0.36494586063967555
718	P03.EP.EL.CI.0,16	P03	EP	EL	CI	0.16	0	0	0.36494586063967555
719	P03.EP.EL.CI.0,17	P03	EP	EL	CI	0.17	0	0	0.36494586063967555
720	P03.EP.EL.CI.0,18	P03	EP	EL	CI	0.18000000000000002	0	0	0.36494586063967555
721	P03.EP.EL.CI.0,19	P03	EP	EL	CI	0.19000000000000003	0	0	0.36494586063967555
722	P03.EP.EL.CI.0,2	P03	EP	EL	CI	0.20000000000000004	0	0	0.36494586063967555
723	P03.EI.EL.CI.0,01	P03	EI	EL	CI	0.01	0	0	0.07868544534959554
724	P03.EI.EL.CI.0,02	P03	EI	EL	CI	0.02	0	0	0.039342722674797756
725	P03.EI.EL.CI.0,03	P03	EI	EL	CI	0.03	0	0	0
726	P03.EI.EL.CI.0,04	P03	EI	EL	CI	0.04	0	0	0.08170335981668841
727	P03.EI.EL.CI.0,05	P03	EI	EL	CI	0.05	0	0	0.16340671963337683
728	P03.EI.EL.CI.0,06	P03	EI	EL	CI	0.060000000000000005	0	0	0.24511007945006524
729	P03.EI.EL.CI.0,07	P03	EI	EL	CI	0.07	0	0	0.3268134392667537
730	P03.EI.EL.CI.0,08	P03	EI	EL	CI	0.08	0	0	0.3268134392667537
731	P03.EI.EL.CI.0,09	P03	EI	EL	CI	0.09	0	0	0.3268134392667537
732	P03.EI.EL.CI.0,1	P03	EI	EL	CI	0.09999999999999999	0	0	0.3268134392667537
733	P03.EI.EL.CI.0,11	P03	EI	EL	CI	0.10999999999999999	0	0	0.3268134392667537
734	P03.EI.EL.CI.0,12	P03	EI	EL	CI	0.11999999999999998	0	0	0.3268134392667537
735	P03.EI.EL.CI.0,13	P03	EI	EL	CI	0.12999999999999998	0	0	0.3268134392667537
736	P03.EI.EL.CI.0,14	P03	EI	EL	CI	0.13999999999999999	0	0	0.3268134392667537
737	P03.EI.EL.CI.0,15	P03	EI	EL	CI	0.15	0	0	0.3268134392667537
738	P03.EI.EL.CI.0,16	P03	EI	EL	CI	0.16	0	0	0.3268134392667537
739	P03.EI.EL.CI.0,17	P03	EI	EL	CI	0.17	0	0	0.3268134392667537
740	P03.EI.EL.CI.0,18	P03	EI	EL	CI	0.18000000000000002	0	0	0.3268134392667537
741	P03.EI.EL.CI.0,19	P03	EI	EL	CI	0.19000000000000003	0	0	0.3268134392667537
742	P03.EI.EL.CI.0,2	P03	EI	EL	CI	0.20000000000000004	0	0	0.3268134392667537
743	P03.EM.EL.CI.0,01	P03	EM	EL	CI	0.01	0	0	0.06045930782400788
744	P03.EM.EL.CI.0,02	P03	EM	EL	CI	0.02	0	0	0.030229653912003933
745	P03.EM.EL.CI.0,03	P03	EM	EL	CI	0.03	0	0	0
746	P03.EM.EL.CI.0,04	P03	EM	EL	CI	0.04	0	0	0.0587904900516093
747	P03.EM.EL.CI.0,05	P03	EM	EL	CI	0.05	0	0	0.1175809801032186
748	P03.EM.EL.CI.0,06	P03	EM	EL	CI	0.060000000000000005	0	0	0.1763714701548279
749	P03.EM.EL.CI.0,07	P03	EM	EL	CI	0.07	0	0	0.2351619602064372
750	P03.EM.EL.CI.0,08	P03	EM	EL	CI	0.08	0	0	0.2351619602064372
751	P03.EM.EL.CI.0,09	P03	EM	EL	CI	0.09	0	0	0.2351619602064372
752	P03.EM.EL.CI.0,1	P03	EM	EL	CI	0.09999999999999999	0	0	0.2351619602064372
753	P03.EM.EL.CI.0,11	P03	EM	EL	CI	0.10999999999999999	0	0	0.2351619602064372
754	P03.EM.EL.CI.0,12	P03	EM	EL	CI	0.11999999999999998	0	0	0.2351619602064372
755	P03.EM.EL.CI.0,13	P03	EM	EL	CI	0.12999999999999998	0	0	0.2351619602064372
756	P03.EM.EL.CI.0,14	P03	EM	EL	CI	0.13999999999999999	0	0	0.2351619602064372
757	P03.EM.EL.CI.0,15	P03	EM	EL	CI	0.15	0	0	0.2351619602064372
758	P03.EM.EL.CI.0,16	P03	EM	EL	CI	0.16	0	0	0.2351619602064372
759	P03.EM.EL.CI.0,17	P03	EM	EL	CI	0.17	0	0	0.2351619602064372
760	P03.EM.EL.CI.0,18	P03	EM	EL	CI	0.18000000000000002	0	0	0.2351619602064372
761	P03.EM.EL.CI.0,19	P03	EM	EL	CI	0.19000000000000003	0	0	0.2351619602064372
762	P03.EM.EL.CI.0,2	P03	EM	EL	CI	0.20000000000000004	0	0	0.2351619602064372
763	P03.EP.EP.CE.0,01	P03	EP	EP	CE	0.01	0	0	0.2008113300932548
764	P03.EP.EP.CE.0,02	P03	EP	EP	CE	0.02	0	0	0.17497237196712273
765	P03.EP.EP.CE.0,03	P03	EP	EP	CE	0.03	0	0	0.14913341384099066
766	P03.EP.EP.CE.0,04	P03	EP	EP	CE	0.04	0	0	0.12329445571485859
767	P03.EP.EP.CE.0,05	P03	EP	EP	CE	0.05	0	0	0.09745549758872651
768	P03.EP.EP.CE.0,06	P03	EP	EP	CE	0.060000000000000005	0	0	0.0894444991810707
769	P03.EP.EP.CE.0,07	P03	EP	EP	CE	0.07	0	0	0.08143350077341487
770	P03.EP.EP.CE.0,08	P03	EP	EP	CE	0.08	0	0	0.07342250236575905
771	P03.EP.EP.CE.0,09	P03	EP	EP	CE	0.09	0	0	0.06541150395810323
772	P03.EP.EP.CE.0,1	P03	EP	EP	CE	0.09999999999999999	0	0	0.0574005055504474
773	P03.EP.EP.CE.0,11	P03	EP	EP	CE	0.10999999999999999	0	0	0.04938950714279158
774	P03.EP.EP.CE.0,12	P03	EP	EP	CE	0.11999999999999998	0	0	0.041378508735135766
775	P03.EP.EP.CE.0,13	P03	EP	EP	CE	0.12999999999999998	0	0	0.03336751032747995
776	P03.EP.EP.CE.0,14	P03	EP	EP	CE	0.13999999999999999	0	0	0.025356511919824118
777	P03.EP.EP.CE.0,15	P03	EP	EP	CE	0.15	0	0	0.017345513512168287
778	P03.EP.EP.CE.0,16	P03	EP	EP	CE	0.16	0	0	0.00933451510451247
779	P03.EP.EP.CE.0,17	P03	EP	EP	CE	0.17	0	0	0.0013235166968566248
780	P03.EP.EP.CE.0,18	P03	EP	EP	CE	0.18000000000000002	0	0	0
781	P03.EP.EP.CE.0,19	P03	EP	EP	CE	0.19000000000000003	0	0	0
782	P03.EP.EP.CE.0,2	P03	EP	EP	CE	0.20000000000000004	0	0	0
783	P03.EI.EI.CE.0,01	P03	EI	EI	CE	0.01	0	0	0.15550977573513292
784	P03.EI.EI.CE.0,02	P03	EI	EI	CE	0.02	0	0	0.1425551419750024
785	P03.EI.EI.CE.0,03	P03	EI	EI	CE	0.03	0	0	0.1296005082148719
786	P03.EI.EI.CE.0,04	P03	EI	EI	CE	0.04	0	0	0.1166458744547414
787	P03.EI.EI.CE.0,05	P03	EI	EI	CE	0.05	0	0	0.10369124069461089
788	P03.EI.EI.CE.0,06	P03	EI	EI	CE	0.060000000000000005	0	0	0.09359764683578069
789	P03.EI.EI.CE.0,07	P03	EI	EI	CE	0.07	0	0	0.08350405297695049
790	P03.EI.EI.CE.0,08	P03	EI	EI	CE	0.08	0	0	0.07341045911812029
791	P03.EI.EI.CE.0,09	P03	EI	EI	CE	0.09	0	0	0.0633168652592901
792	P03.EI.EI.CE.0,1	P03	EI	EI	CE	0.09999999999999999	0	0	0.05322327140045992
793	P03.EI.EI.CE.0,11	P03	EI	EI	CE	0.10999999999999999	0	0	0.04312967754162972
794	P03.EI.EI.CE.0,12	P03	EI	EI	CE	0.11999999999999998	0	0	0.03303608368279953
795	P03.EI.EI.CE.0,13	P03	EI	EI	CE	0.12999999999999998	0	0	0.022942489823969348
796	P03.EI.EI.CE.0,14	P03	EI	EI	CE	0.13999999999999999	0	0	0.012848895965139134
797	P03.EI.EI.CE.0,15	P03	EI	EI	CE	0.15	0	0	0.002755302106308921
798	P03.EI.EI.CE.0,16	P03	EI	EI	CE	0.16	0	0	0
799	P03.EI.EI.CE.0,17	P03	EI	EI	CE	0.17	0	0	0
800	P03.EI.EI.CE.0,18	P03	EI	EI	CE	0.18000000000000002	0	0	0
801	P03.EI.EI.CE.0,19	P03	EI	EI	CE	0.19000000000000003	0	0	0
802	P03.EI.EI.CE.0,2	P03	EI	EI	CE	0.20000000000000004	0	0	0
803	P03.EP.EM.CE.0,01	P03	EP	EM	CE	0.01	0	0	0.13991264982550522
804	P03.EP.EM.CE.0,02	P03	EP	EM	CE	0.02	0	0	0.12309295127704523
805	P03.EP.EM.CE.0,03	P03	EP	EM	CE	0.03	0	0	0.10627325272858523
806	P03.EP.EM.CE.0,04	P03	EP	EM	CE	0.04	0	0	0.08945355418012524
807	P03.EP.EM.CE.0,05	P03	EP	EM	CE	0.05	0	0	0.07263385563166525
808	P03.EP.EM.CE.0,06	P03	EP	EM	CE	0.060000000000000005	0	0	0.06582137753731598
809	P03.EP.EM.CE.0,07	P03	EP	EM	CE	0.07	0	0	0.059008899442966715
810	P03.EP.EM.CE.0,08	P03	EP	EM	CE	0.08	0	0	0.05219642134861746
811	P03.EP.EM.CE.0,09	P03	EP	EM	CE	0.09	0	0	0.0453839432542682
812	P03.EP.EM.CE.0,1	P03	EP	EM	CE	0.09999999999999999	0	0	0.03857146515991894
813	P03.EP.EM.CE.0,11	P03	EP	EM	CE	0.10999999999999999	0	0	0.03175898706556969
814	P03.EP.EM.CE.0,12	P03	EP	EM	CE	0.11999999999999998	0	0	0.02494650897122043
815	P03.EP.EM.CE.0,13	P03	EP	EM	CE	0.12999999999999998	0	0	0.01813403087687117
816	P03.EP.EM.CE.0,14	P03	EP	EM	CE	0.13999999999999999	0	0	0.011321552782521907
817	P03.EP.EM.CE.0,15	P03	EP	EM	CE	0.15	0	0	0.004509074688172632
818	P03.EP.EM.CE.0,16	P03	EP	EM	CE	0.16	0	0	0
819	P03.EP.EM.CE.0,17	P03	EP	EM	CE	0.17	0	0	0
820	P03.EP.EM.CE.0,18	P03	EP	EM	CE	0.18000000000000002	0	0	0
821	P03.EP.EM.CE.0,19	P03	EP	EM	CE	0.19000000000000003	0	0	0
822	P03.EP.EM.CE.0,2	P03	EP	EM	CE	0.20000000000000004	0	0	0
823	P03.EI.EM.CE.0,01	P03	EI	EM	CE	0.01	0	0	0.109852945349596
824	P03.EI.EM.CE.0,02	P03	EI	EM	CE	0.02	0	0	0.09882555121757008
825	P03.EI.EM.CE.0,03	P03	EI	EM	CE	0.03	0	0	0.08779815708554417
826	P03.EI.EM.CE.0,04	P03	EI	EM	CE	0.04	0	0	0.07677076295351826
827	P03.EI.EM.CE.0,05	P03	EI	EM	CE	0.05	0	0	0.06574336882149234
828	P03.EI.EM.CE.0,06	P03	EI	EM	CE	0.060000000000000005	0	0	0.059796367020531545
829	P03.EI.EM.CE.0,07	P03	EI	EM	CE	0.07	0	0	0.053849365219570754
830	P03.EI.EM.CE.0,08	P03	EI	EM	CE	0.08	0	0	0.04790236341860996
831	P03.EI.EM.CE.0,09	P03	EI	EM	CE	0.09	0	0	0.04195536161764917
832	P03.EI.EM.CE.0,1	P03	EI	EM	CE	0.09999999999999999	0	0	0.03600835981668838
833	P03.EI.EM.CE.0,11	P03	EI	EM	CE	0.10999999999999999	0	0	0.030061358015727582
834	P03.EI.EM.CE.0,12	P03	EI	EM	CE	0.11999999999999998	0	0	0.02411435621476679
835	P03.EI.EM.CE.0,13	P03	EI	EM	CE	0.12999999999999998	0	0	0.018167354413806
836	P03.EI.EM.CE.0,14	P03	EI	EM	CE	0.13999999999999999	0	0	0.012220352612845209
837	P03.EI.EM.CE.0,15	P03	EI	EM	CE	0.15	0	0	0.006273350811884404
838	P03.EI.EM.CE.0,16	P03	EI	EM	CE	0.16	0	0	0.0003263490109236128
839	P03.EI.EM.CE.0,17	P03	EI	EM	CE	0.17	0	0	0
840	P03.EI.EM.CE.0,18	P03	EI	EM	CE	0.18000000000000002	0	0	0
841	P03.EI.EM.CE.0,19	P03	EI	EM	CE	0.19000000000000003	0	0	0
842	P03.EI.EM.CE.0,2	P03	EI	EM	CE	0.20000000000000004	0	0	0
843	P03.EP.EL.CE.0,01	P03	EP	EL	CE	0.01	0	0	0.13998514982550514
844	P03.EP.EL.CE.0,02	P03	EP	EL	CE	0.02	0	0	0.12377857627704514
845	P03.EP.EL.CE.0,03	P03	EP	EL	CE	0.03	0	0	0.10757200272858514
846	P03.EP.EL.CE.0,04	P03	EP	EL	CE	0.04	0	0	0.09136542918012514
847	P03.EP.EL.CE.0,05	P03	EP	EL	CE	0.05	0	0	0.07515885563166513
848	P03.EP.EL.CE.0,06	P03	EP	EL	CE	0.060000000000000005	0	0	0.0678483775373159
849	P03.EP.EL.CE.0,07	P03	EP	EL	CE	0.07	0	0	0.060537899442966656
850	P03.EP.EL.CE.0,08	P03	EP	EL	CE	0.08	0	0	0.05322742134861742
851	P03.EP.EL.CE.0,09	P03	EP	EL	CE	0.09	0	0	0.04591694325426819
852	P03.EP.EL.CE.0,1	P03	EP	EL	CE	0.09999999999999999	0	0	0.038606465159918946
853	P03.EP.EL.CE.0,11	P03	EP	EL	CE	0.10999999999999999	0	0	0.031295987065569714
854	P03.EP.EL.CE.0,12	P03	EP	EL	CE	0.11999999999999998	0	0	0.02398550897122048
855	P03.EP.EL.CE.0,13	P03	EP	EL	CE	0.12999999999999998	0	0	0.01667503087687125
856	P03.EP.EL.CE.0,14	P03	EP	EL	CE	0.13999999999999999	0	0	0.009364552782522004
857	P03.EP.EL.CE.0,15	P03	EP	EL	CE	0.15	0	0	0.002054074688172758
858	P03.EP.EL.CE.0,16	P03	EP	EL	CE	0.16	0	0	0
859	P03.EP.EL.CE.0,17	P03	EP	EL	CE	0.17	0	0	0
860	P03.EP.EL.CE.0,18	P03	EP	EL	CE	0.18000000000000002	0	0	0
861	P03.EP.EL.CE.0,19	P03	EP	EL	CE	0.19000000000000003	0	0	0
862	P03.EP.EL.CE.0,2	P03	EP	EL	CE	0.20000000000000004	0	0	0
863	P03.EI.EL.CE.0,01	P03	EI	EL	CE	0.01	0	0	0.11022544534959566
864	P03.EI.EL.CE.0,02	P03	EI	EL	CE	0.02	0	0	0.09969711371756984
865	P03.EI.EL.CE.0,03	P03	EI	EL	CE	0.03	0	0	0.08916878208554402
866	P03.EI.EL.CE.0,04	P03	EI	EL	CE	0.04	0	0	0.0786404504535182
867	P03.EI.EL.CE.0,05	P03	EI	EL	CE	0.05	0	0	0.06811211882149237
868	P03.EI.EL.CE.0,06	P03	EI	EL	CE	0.060000000000000005	0	0	0.061672367020531554
869	P03.EI.EL.CE.0,07	P03	EI	EL	CE	0.07	0	0	0.05523261521957074
870	P03.EI.EL.CE.0,08	P03	EI	EL	CE	0.08	0	0	0.04879286341860993
871	P03.EI.EL.CE.0,09	P03	EI	EL	CE	0.09	0	0	0.042353111617649125
872	P03.EI.EL.CE.0,1	P03	EI	EL	CE	0.09999999999999999	0	0	0.035913359816688306
873	P03.EI.EL.CE.0,11	P03	EI	EL	CE	0.10999999999999999	0	0	0.0294736080157275
874	P03.EI.EL.CE.0,12	P03	EI	EL	CE	0.11999999999999998	0	0	0.023033856214766696
875	P03.EI.EL.CE.0,13	P03	EI	EL	CE	0.12999999999999998	0	0	0.016594104413805877
876	P03.EI.EL.CE.0,14	P03	EI	EL	CE	0.13999999999999999	0	0	0.010154352612845058
877	P03.EI.EL.CE.0,15	P03	EI	EL	CE	0.15	0	0	0.003714600811884239
878	P03.EI.EL.CE.0,16	P03	EI	EL	CE	0.16	0	0	0
879	P03.EI.EL.CE.0,17	P03	EI	EL	CE	0.17	0	0	0
880	P03.EI.EL.CE.0,18	P03	EI	EL	CE	0.18000000000000002	0	0	0
881	P03.EI.EL.CE.0,19	P03	EI	EL	CE	0.19000000000000003	0	0	0
882	P03.EI.EL.CE.0,2	P03	EI	EL	CE	0.20000000000000004	0	0	0
883	P03.EM.EL.CE.0,01	P03	EM	EL	CE	0.01	0	0	0.06349930782400781
884	P03.EM.EL.CE.0,02	P03	EM	EL	CE	0.02	0	0	0.06051213097855593
885	P03.EM.EL.CE.0,03	P03	EM	EL	CE	0.03	0	0	0.057524954133104045
886	P03.EM.EL.CE.0,04	P03	EM	EL	CE	0.04	0	0	0.05453777728765216
887	P03.EM.EL.CE.0,05	P03	EM	EL	CE	0.05	0	0	0.05155060044220028
888	P03.EM.EL.CE.0,06	P03	EM	EL	CE	0.060000000000000005	0	0	0.047032578364082075
889	P03.EM.EL.CE.0,07	P03	EM	EL	CE	0.07	0	0	0.04251455628596387
890	P03.EM.EL.CE.0,08	P03	EM	EL	CE	0.08	0	0	0.03799653420784568
891	P03.EM.EL.CE.0,09	P03	EM	EL	CE	0.09	0	0	0.03347851212972748
892	P03.EM.EL.CE.0,1	P03	EM	EL	CE	0.09999999999999999	0	0	0.028960490051609285
893	P03.EM.EL.CE.0,11	P03	EM	EL	CE	0.10999999999999999	0	0	0.024442467973491082
894	P03.EM.EL.CE.0,12	P03	EM	EL	CE	0.11999999999999998	0	0	0.019924445895372886
895	P03.EM.EL.CE.0,13	P03	EM	EL	CE	0.12999999999999998	0	0	0.01540642381725469
896	P03.EM.EL.CE.0,14	P03	EM	EL	CE	0.13999999999999999	0	0	0.01088840173913648
897	P03.EM.EL.CE.0,15	P03	EM	EL	CE	0.15	0	0	0.006370379661018277
898	P03.EM.EL.CE.0,16	P03	EM	EL	CE	0.16	0	0	0.0018523575829000744
899	P03.EM.EL.CE.0,17	P03	EM	EL	CE	0.17	0	0	0
900	P03.EM.EL.CE.0,18	P03	EM	EL	CE	0.18000000000000002	0	0	0
901	P03.EM.EL.CE.0,19	P03	EM	EL	CE	0.19000000000000003	0	0	0
902	P03.EM.EL.CE.0,2	P03	EM	EL	CE	0.20000000000000004	0	0	0
903	P03.EL.EL.IE.0,01	P03	EL	EL	CE	0.01	0	0	0.19430340596891904
904	P03.EL.EL.CE.0,02	P03	EL	EL	CE	0.02	0	0	0.18870859516149202
905	P03.EL.EL.CE.0,03	P03	EL	EL	CE	0.03	0	0	0.183113784354065
906	P03.EL.EL.CE.0,04	P03	EL	EL	CE	0.04	0	0	0.17751897354663798
907	P03.EL.EL.IE.0,05	P03	EL	EL	CE	0.05	0	0	0.17192416273921096
908	P03.EL.EL.CE.0,06	P03	EL	EL	CE	0.060000000000000005	0	0	0.14635312589752128
909	P03.EL.EL.CE.0,07	P03	EL	EL	CE	0.07	0	0	0.12078208905583163
910	P03.EL.EL.CE.0,08	P03	EL	EL	CE	0.08	0	0	0.09521105221414197
911	P03.EL.EL.CE.0,09	P03	EL	EL	CE	0.09	0	0	0.06964001537245232
912	P03.EL.EL.IE.0,1	P03	EL	EL	CE	0.09999999999999999	0	0	0.04406897853076264
913	P03.EL.EL.CE.0,11	P03	EL	EL	CE	0.10999999999999999	0	0	0.018497941689072983
914	P03.EL.EL.CE.0,12	P03	EL	EL	CE	0.11999999999999998	0	0	0
915	P03.EL.EL.CE.0,13	P03	EL	EL	CE	0.12999999999999998	0	0	0
916	P03.EL.EL.CE.0,14	P03	EL	EL	CE	0.13999999999999999	0	0	0
917	P03.EL.EL.CE.0,15	P03	EL	EL	CE	0.15	0	0	0
918	P03.EL.EL.CE.0,16	P03	EL	EL	CE	0.16	0	0	0
919	P03.EL.EL.CE.0,17	P03	EL	EL	CE	0.17	0	0	0
920	P03.EL.EL.CE.0,18	P03	EL	EL	CE	0.18000000000000002	0	0	0
921	P03.EL.EL.CE.0,19	P03	EL	EL	CE	0.19000000000000003	0	0	0
922	P03.EL.EL.CE.0,2	P03	EL	EL	CE	0.20000000000000004	0	0	0
923	P04.EP.EP.SA.0	P04	EP	EP	SA	0	0	0	0.6443645397238154
924	P04.EP.EM.SA.0	P04	EP	EM	SA	0	0	0	0.5687395397238149
925	P04.EI.EM.SA.0	P04	EI	EM	SA	0	0	0	0.36635566586109913
926	P04.EP.EL.SA.0	P04	EP	EL	SA	0	0	0	0.5906395397238153
927	P04.EI.EL.SA.0	P04	EI	EL	SA	0	0	0	0.37985566586109965
928	P04.EP.EP.CE.0,01	P04	EP	EP	CE	0.01	0	0	0.6093822827257833
929	P04.EP.EP.CE.0,02	P04	EP	EP	CE	0.02	0	0	0.5671507580768335
930	P04.EP.EP.CE.0,03	P04	EP	EP	CE	0.03	0	0	0.5249192334278836
931	P04.EP.EP.CE.0,04	P04	EP	EP	CE	0.04	0	0	0.48268770877893363
932	P04.EP.EP.CE.0,05	P04	EP	EP	CE	0.05	0	0	0.44045618412998366
933	P04.EP.EP.CE.0,06	P04	EP	EP	CE	0.060000000000000005	0	0	0.39832374177735286
934	P04.EP.EP.CE.0,07	P04	EP	EP	CE	0.07	0	0	0.356191299424722
935	P04.EP.EP.CE.0,08	P04	EP	EP	CE	0.08	0	0	0.3140588570720912
936	P04.EP.EP.CE.0,09	P04	EP	EP	CE	0.09	0	0	0.2719264147194604
937	P04.EP.EP.CE.0,1	P04	EP	EP	CE	0.09999999999999999	0	0	0.22979397236682958
938	P04.EP.EP.CE.0,11	P04	EP	EP	CE	0.10999999999999999	0	0	0.18766153001419877
939	P04.EP.EP.CE.0,12	P04	EP	EP	CE	0.11999999999999998	0	0	0.14552908766156802
940	P04.EP.EP.CE.0,13	P04	EP	EP	CE	0.12999999999999998	0	0	0.10339664530893722
941	P04.EP.EP.CE.0,14	P04	EP	EP	CE	0.13999999999999999	0	0	0.0612642029563063
942	P04.EP.EP.CE.0,15	P04	EP	EP	CE	0.15	0	0	0.019131760603675496
943	P04.EP.EP.CE.0,16	P04	EP	EP	CE	0.16	0	0	0
944	P04.EP.EP.CE.0,17	P04	EP	EP	CE	0.17	0	0	0
945	P04.EP.EP.CE.0,18	P04	EP	EP	CE	0.18000000000000002	0	0	0
946	P04.EP.EP.CE.0,19	P04	EP	EP	CE	0.19000000000000003	0	0	0
947	P04.EP.EP.CE.0,2	P04	EP	EP	CE	0.20000000000000004	0	0	0
948	P04.EP.EM.CE.0,01	P04	EP	EM	CE	0.01	0	0	0.3223822827257834
949	P04.EP.EM.CE.0,02	P04	EP	EM	CE	0.02	0	0	0.28418200807683347
950	P04.EP.EM.CE.0,03	P04	EP	EM	CE	0.03	0	0	0.24598173342788354
951	P04.EP.EM.CE.0,04	P04	EP	EM	CE	0.04	0	0	0.20778145877893361
952	P04.EP.EM.CE.0,05	P04	EP	EM	CE	0.05	0	0	0.1695811841299837
953	P04.EP.EM.CE.0,06	P04	EP	EM	CE	0.060000000000000005	0	0	0.15228624177735284
954	P04.EP.EM.CE.0,07	P04	EP	EM	CE	0.07	0	0	0.13499129942472202
955	P04.EP.EM.CE.0,08	P04	EP	EM	CE	0.08	0	0	0.1176963570720912
956	P04.EP.EM.CE.0,09	P04	EP	EM	CE	0.09	0	0	0.10040141471946037
957	P04.EP.EM.CE.0,1	P04	EP	EM	CE	0.09999999999999999	0	0	0.08310647236682958
958	P04.EP.EM.CE.0,11	P04	EP	EM	CE	0.10999999999999999	0	0	0.06581153001419876
959	P04.EP.EM.CE.0,12	P04	EP	EM	CE	0.11999999999999998	0	0	0.04851658766156794
960	P04.EP.EM.CE.0,13	P04	EP	EM	CE	0.12999999999999998	0	0	0.031221645308937118
961	P04.EP.EM.CE.0,14	P04	EP	EM	CE	0.13999999999999999	0	0	0.01392670295630627
962	P04.EP.EM.CE.0,15	P04	EP	EM	CE	0.15	0	0	0
963	P04.EP.EM.CE.0,16	P04	EP	EM	CE	0.16	0	0	0
964	P04.EP.EM.CE.0,17	P04	EP	EM	CE	0.17	0	0	0
965	P04.EP.EM.CE.0,18	P04	EP	EM	CE	0.18000000000000002	0	0	0
966	P04.EP.EM.CE.0,19	P04	EP	EM	CE	0.19000000000000003	0	0	0
967	P04.EP.EM.CE.0,2	P04	EP	EM	CE	0.20000000000000004	0	0	0
968	P04.EI.EM.CE.0,01	P04	EI	EM	CE	0.01	0	0	0.2548558840631916
969	P04.EI.EM.CE.0,02	P04	EI	EM	CE	0.02	0	0	0.2295772543749111
970	P04.EI.EM.CE.0,03	P04	EI	EM	CE	0.03	0	0	0.20429862468663063
971	P04.EI.EM.CE.0,04	P04	EI	EM	CE	0.04	0	0	0.17901999499835014
972	P04.EI.EM.CE.0,05	P04	EI	EM	CE	0.05	0	0	0.15374136531006966
973	P04.EI.EM.CE.0,06	P04	EI	EM	CE	0.060000000000000005	0	0	0.1389614281428534
974	P04.EI.EM.CE.0,07	P04	EI	EM	CE	0.07	0	0	0.12418149097563712
975	P04.EI.EM.CE.0,08	P04	EI	EM	CE	0.08	0	0	0.10940155380842087
976	P04.EI.EM.CE.0,09	P04	EI	EM	CE	0.09	0	0	0.09462161664120461
977	P04.EI.EM.CE.0,1	P04	EI	EM	CE	0.09999999999999999	0	0	0.07984167947398835
978	P04.EI.EM.CE.0,11	P04	EI	EM	CE	0.10999999999999999	0	0	0.06506174230677211
979	P04.EI.EM.CE.0,12	P04	EI	EM	CE	0.11999999999999998	0	0	0.05028180513955585
980	P04.EI.EM.CE.0,13	P04	EI	EM	CE	0.12999999999999998	0	0	0.03550186797233959
981	P04.EI.EM.CE.0,14	P04	EI	EM	CE	0.13999999999999999	0	0	0.02072193080512333
982	P04.EI.EM.CE.0,15	P04	EI	EM	CE	0.15	0	0	0.005941993637907039
983	P04.EI.EM.CE.0,16	P04	EI	EM	CE	0.16	0	0	0
984	P04.EI.EM.CE.0,17	P04	EI	EM	CE	0.17	0	0	0
985	P04.EI.EM.CE.0,18	P04	EI	EM	CE	0.18000000000000002	0	0	0
986	P04.EI.EM.CE.0,19	P04	EI	EM	CE	0.19000000000000003	0	0	0
987	P04.EI.EM.CE.0,2	P04	EI	EM	CE	0.20000000000000004	0	0	0
988	P04.EP.EL.CE.0,01	P04	EP	EL	CE	0.01	0	0	0.3807197827257829
989	P04.EP.EL.CE.0,02	P04	EP	EL	CE	0.02	0	0	0.3426851330768331
990	P04.EP.EL.CE.0,03	P04	EP	EL	CE	0.03	0	0	0.30465048342788337
991	P04.EP.EL.CE.0,04	P04	EP	EL	CE	0.04	0	0	0.2666158337789336
992	P04.EP.EL.CE.0,05	P04	EP	EL	CE	0.05	0	0	0.22858118412998385
993	P04.EP.EL.CE.0,06	P04	EP	EL	CE	0.060000000000000005	0	0	0.20776624177735298
994	P04.EP.EL.CE.0,07	P04	EP	EL	CE	0.07	0	0	0.1869512994247221
995	P04.EP.EL.CE.0,08	P04	EP	EL	CE	0.08	0	0	0.16613635707209126
996	P04.EP.EL.CE.0,09	P04	EP	EL	CE	0.09	0	0	0.14532141471946042
997	P04.EP.EL.CE.0,1	P04	EP	EL	CE	0.09999999999999999	0	0	0.12450647236682957
998	P04.EP.EL.CE.0,11	P04	EP	EL	CE	0.10999999999999999	0	0	0.1036915300141987
999	P04.EP.EL.CE.0,12	P04	EP	EL	CE	0.11999999999999998	0	0	0.08287658766156786
1000	P04.EP.EL.CE.0,13	P04	EP	EL	CE	0.12999999999999998	0	0	0.062061645308936986
1001	P04.EP.EL.CE.0,14	P04	EP	EL	CE	0.13999999999999999	0	0	0.041246702956306114
1002	P04.EP.EL.CE.0,15	P04	EP	EL	CE	0.15	0	0	0.020431760603675242
1003	P04.EP.EL.CE.0,16	P04	EP	EL	CE	0.16	0	0	0
1004	P04.EP.EL.CE.0,17	P04	EP	EL	CE	0.17	0	0	0
1005	P04.EP.EL.CE.0,18	P04	EP	EL	CE	0.18000000000000002	0	0	0
1006	P04.EP.EL.CE.0,19	P04	EP	EL	CE	0.19000000000000003	0	0	0
1007	P04.EP.EL.CE.0,2	P04	EP	EL	CE	0.20000000000000004	0	0	0
1008	P04.EI.EL.CE.0,01	P04	EI	EL	CE	0.01	0	0	0.29071838406319195
1009	P04.EI.EL.CE.0,02	P04	EI	EL	CE	0.02	0	0	0.26808350437491135
1010	P04.EI.EL.CE.0,03	P04	EI	EL	CE	0.03	0	0	0.24544862468663076
1011	P04.EI.EL.CE.0,04	P04	EI	EL	CE	0.04	0	0	0.22281374499835016
1012	P04.EI.EL.CE.0,05	P04	EI	EL	CE	0.05	0	0	0.20017886531006956
1013	P04.EI.EL.CE.0,06	P04	EI	EL	CE	0.060000000000000005	0	0	0.18324142814285332
1014	P04.EI.EL.CE.0,07	P04	EI	EL	CE	0.07	0	0	0.16630399097563706
1015	P04.EI.EL.CE.0,08	P04	EI	EL	CE	0.08	0	0	0.14936655380842082
1016	P04.EI.EL.CE.0,09	P04	EI	EL	CE	0.09	0	0	0.13242911664120458
1017	P04.EI.EL.CE.0,1	P04	EI	EL	CE	0.09999999999999999	0	0	0.11549167947398833
1018	P04.EI.EL.CE.0,11	P04	EI	EL	CE	0.10999999999999999	0	0	0.09855424230677207
1019	P04.EI.EL.CE.0,12	P04	EI	EL	CE	0.11999999999999998	0	0	0.08161680513955583
1020	P04.EI.EL.CE.0,13	P04	EI	EL	CE	0.12999999999999998	0	0	0.06467936797233959
1021	P04.EI.EL.CE.0,14	P04	EI	EL	CE	0.13999999999999999	0	0	0.04774193080512332
1022	P04.EI.EL.CE.0,15	P04	EI	EL	CE	0.15	0	0	0.03080449363790705
1023	P04.EI.EL.CE.0,16	P04	EI	EL	CE	0.16	0	0	0.013867056470690808
1024	P04.EI.EL.CE.0,17	P04	EI	EL	CE	0.17	0	0	0
1025	P04.EI.EL.CE.0,18	P04	EI	EL	CE	0.18000000000000002	0	0	0
1026	P04.EI.EL.CE.0,19	P04	EI	EL	CE	0.19000000000000003	0	0	0
1027	P04.EI.EL.CE.0,2	P04	EI	EL	CE	0.20000000000000004	0	0	0
1028	P05.EP.VI.SA.0.Sin.Interior	P05	EP	VI	SA	0	"Sin"	"Interior"	0.18742198161275692
1029	P05.EI.VI.SA.0.Sin.Interior	P05	EI	VI	SA	0	"Sin"	"Interior"	0.1730891443896665
1030	P05.EM.VI.SA.0.Sin.Interior	P05	EM	VI	SA	0	"Sin"	"Interior"	0.08885241550777323
1031	P05.EL.VI.SA.0.Sin.Interior	P05	EL	VI	SA	0	"Sin"	"Interior"	0.09150203711154958
1032	P05.EP.VI.CI.0,01.Sin.Interior	P05	EP	VI	CI	0.01	"Sin"	"Interior"	0.11963595613677835
1033	P05.EP.VI.CI.0,02.Sin.Interior	P05	EP	VI	CI	0.02	"Sin"	"Interior"	0.11755761365051542
1034	P05.EP.VI.CI.0,03.Sin.Interior	P05	EP	VI	CI	0.03	"Sin"	"Interior"	0.1154792711642525
1035	P05.EP.VI.CI.0,04.Sin.Interior	P05	EP	VI	CI	0.04	"Sin"	"Interior"	0.13461625368120655
1036	P05.EP.VI.CI.0,05.Sin.Interior	P05	EP	VI	CI	0.05	"Sin"	"Interior"	0.15375323619816061
1037	P05.EP.VI.CI.0,06.Sin.Interior	P05	EP	VI	CI	0.060000000000000005	"Sin"	"Interior"	0.17289021871511467
1038	P05.EP.VI.CI.0,07.Sin.Interior	P05	EP	VI	CI	0.07	"Sin"	"Interior"	0.19202720123206873
1039	P05.EP.VI.CI.0,08.Sin.Interior	P05	EP	VI	CI	0.08	"Sin"	"Interior"	0.19202720123206873
1040	P05.EP.VI.CI.0,09.Sin.Interior	P05	EP	VI	CI	0.09	"Sin"	"Interior"	0.19202720123206873
1041	P05.EP.VI.CI.0,1.Sin.Interior	P05	EP	VI	CI	0.09999999999999999	"Sin"	"Interior"	0.19202720123206873
1042	P05.EP.VI.CI.0,11.Sin.Interior	P05	EP	VI	CI	0.10999999999999999	"Sin"	"Interior"	0.19202720123206873
1043	P05.EP.VI.CI.0,12.Sin.Interior	P05	EP	VI	CI	0.11999999999999998	"Sin"	"Interior"	0.19202720123206873
1044	P05.EP.VI.CI.0,13.Sin.Interior	P05	EP	VI	CI	0.12999999999999998	"Sin"	"Interior"	0.19202720123206873
1045	P05.EP.VI.CI.0,14.Sin.Interior	P05	EP	VI	CI	0.13999999999999999	"Sin"	"Interior"	0.19202720123206873
1046	P05.EP.VI.CI.0,15.Sin.Interior	P05	EP	VI	CI	0.15	"Sin"	"Interior"	0.19202720123206873
1047	P05.EP.VI.CI.0,16.Sin.Interior	P05	EP	VI	CI	0.16	"Sin"	"Interior"	0.19202720123206873
1048	P05.EP.VI.CI.0,17.Sin.Interior	P05	EP	VI	CI	0.17	"Sin"	"Interior"	0.19202720123206873
1049	P05.EP.VI.CI.0,18.Sin.Interior	P05	EP	VI	CI	0.18000000000000002	"Sin"	"Interior"	0.19202720123206873
1050	P05.EP.VI.CI.0,19.Sin.Interior	P05	EP	VI	CI	0.19000000000000003	"Sin"	"Interior"	0.19202720123206873
1051	P05.EP.VI.CI.0,2.Sin.Interior	P05	EP	VI	CI	0.20000000000000004	"Sin"	"Interior"	0.19202720123206873
1052	P05.EI.VI.CI.0,01.Sin.Interior	P05	EI	VI	CI	0.01	"Sin"	"Interior"	0.10976045378103727
1053	P05.EI.VI.CI.0,02.Sin.Interior	P05	EI	VI	CI	0.02	"Sin"	"Interior"	0.10321884121353442
1054	P05.EI.VI.CI.0,03.Sin.Interior	P05	EI	VI	CI	0.03	"Sin"	"Interior"	0.09667722864603157
1055	P05.EI.VI.CI.0,04.Sin.Interior	P05	EI	VI	CI	0.04	"Sin"	"Interior"	0.11059882981634894
1056	P05.EI.VI.CI.0,05.Sin.Interior	P05	EI	VI	CI	0.05	"Sin"	"Interior"	0.12452043098666632
1057	P05.EI.VI.CI.0,06.Sin.Interior	P05	EI	VI	CI	0.060000000000000005	"Sin"	"Interior"	0.1384420321569837
1058	P05.EI.VI.CI.0,07.Sin.Interior	P05	EI	VI	CI	0.07	"Sin"	"Interior"	0.15236363332730107
1059	P05.EI.VI.CI.0,08.Sin.Interior	P05	EI	VI	CI	0.08	"Sin"	"Interior"	0.15236363332730107
1060	P05.EI.VI.CI.0,09.Sin.Interior	P05	EI	VI	CI	0.09	"Sin"	"Interior"	0.15236363332730107
1061	P05.EI.VI.CI.0,1.Sin.Interior	P05	EI	VI	CI	0.09999999999999999	"Sin"	"Interior"	0.15236363332730107
1062	P05.EI.VI.CI.0,11.Sin.Interior	P05	EI	VI	CI	0.10999999999999999	"Sin"	"Interior"	0.15236363332730107
1063	P05.EI.VI.CI.0,12.Sin.Interior	P05	EI	VI	CI	0.11999999999999998	"Sin"	"Interior"	0.15236363332730107
1064	P05.EI.VI.CI.0,13.Sin.Interior	P05	EI	VI	CI	0.12999999999999998	"Sin"	"Interior"	0.15236363332730107
1065	P05.EI.VI.CI.0,14.Sin.Interior	P05	EI	VI	CI	0.13999999999999999	"Sin"	"Interior"	0.15236363332730107
1066	P05.EI.VI.CI.0,15.Sin.Interior	P05	EI	VI	CI	0.15	"Sin"	"Interior"	0.15236363332730107
1067	P05.EI.VI.CI.0,16.Sin.Interior	P05	EI	VI	CI	0.16	"Sin"	"Interior"	0.15236363332730107
1068	P05.EI.VI.CI.0,17.Sin.Interior	P05	EI	VI	CI	0.17	"Sin"	"Interior"	0.15236363332730107
1069	P05.EI.VI.CI.0,18.Sin.Interior	P05	EI	VI	CI	0.18000000000000002	"Sin"	"Interior"	0.15236363332730107
1070	P05.EI.VI.CI.0,19.Sin.Interior	P05	EI	VI	CI	0.19000000000000003	"Sin"	"Interior"	0.15236363332730107
1071	P05.EI.VI.CI.0,2.Sin.Interior	P05	EI	VI	CI	0.20000000000000004	"Sin"	"Interior"	0.15236363332730107
1072	P05.EM.VI.CI.0,01.Sin.Interior	P05	EM	VI	CI	0.01	"Sin"	"Interior"	0.07224899982020094
1073	P05.EM.VI.CI.0,02.Sin.Interior	P05	EM	VI	CI	0.02	"Sin"	"Interior"	0.06765316306243552
1074	P05.EM.VI.CI.0,03.Sin.Interior	P05	EM	VI	CI	0.03	"Sin"	"Interior"	0.06305732630467009
1075	P05.EM.VI.CI.0,04.Sin.Interior	P05	EM	VI	CI	0.04	"Sin"	"Interior"	0.07553942467683283
1076	P05.EM.VI.CI.0,05.Sin.Interior	P05	EM	VI	CI	0.05	"Sin"	"Interior"	0.08802152304899558
1077	P05.EM.VI.CI.0,06.Sin.Interior	P05	EM	VI	CI	0.060000000000000005	"Sin"	"Interior"	0.10050362142115832
1078	P05.EM.VI.CI.0,07.Sin.Interior	P05	EM	VI	CI	0.07	"Sin"	"Interior"	0.11298571979332106
1079	P05.EM.VI.CI.0,08.Sin.Interior	P05	EM	VI	CI	0.08	"Sin"	"Interior"	0.11298571979332106
1080	P05.EM.VI.CI.0,09.Sin.Interior	P05	EM	VI	CI	0.09	"Sin"	"Interior"	0.11298571979332106
1081	P05.EM.VI.CI.0,1.Sin.Interior	P05	EM	VI	CI	0.09999999999999999	"Sin"	"Interior"	0.11298571979332106
1082	P05.EM.VI.CI.0,11.Sin.Interior	P05	EM	VI	CI	0.10999999999999999	"Sin"	"Interior"	0.11298571979332106
1083	P05.EM.VI.CI.0,12.Sin.Interior	P05	EM	VI	CI	0.11999999999999998	"Sin"	"Interior"	0.11298571979332106
1084	P05.EM.VI.CI.0,13.Sin.Interior	P05	EM	VI	CI	0.12999999999999998	"Sin"	"Interior"	0.11298571979332106
1085	P05.EM.VI.CI.0,14.Sin.Interior	P05	EM	VI	CI	0.13999999999999999	"Sin"	"Interior"	0.11298571979332106
1086	P05.EM.VI.CI.0,15.Sin.Interior	P05	EM	VI	CI	0.15	"Sin"	"Interior"	0.11298571979332106
1087	P05.EM.VI.CI.0,16.Sin.Interior	P05	EM	VI	CI	0.16	"Sin"	"Interior"	0.11298571979332106
1088	P05.EM.VI.CI.0,17.Sin.Interior	P05	EM	VI	CI	0.17	"Sin"	"Interior"	0.11298571979332106
1089	P05.EM.VI.CI.0,18.Sin.Interior	P05	EM	VI	CI	0.18000000000000002	"Sin"	"Interior"	0.11298571979332106
1090	P05.EM.VI.CI.0,19.Sin.Interior	P05	EM	VI	CI	0.19000000000000003	"Sin"	"Interior"	0.11298571979332106
1091	P05.EM.VI.CI.0,2.Sin.Interior	P05	EM	VI	CI	0.20000000000000004	"Sin"	"Interior"	0.11298571979332106
1092	P05.EP.VI.CE.0,01.Sin.Interior	P05	EP	VI	CE	0.01	"Sin"	"Interior"	0.5180922061367781
1093	P05.EP.VI.CE.0,02.Sin.Interior	P05	EP	VI	CE	0.02	"Sin"	"Interior"	0.5979430226902203
1094	P05.EP.VI.CE.0,03.Sin.Interior	P05	EP	VI	CE	0.03	"Sin"	"Interior"	0.6777938392436624
1095	P05.EP.VI.CE.0,04.Sin.Interior	P05	EP	VI	CE	0.04	"Sin"	"Interior"	0.7576446557971046
1096	P05.EP.VI.CE.0,05.Sin.Interior	P05	EP	VI	CE	0.05	"Sin"	"Interior"	0.8374954723505468
1097	P05.EP.VI.CE.0,06.Sin.Interior	P05	EP	VI	CE	0.060000000000000005	"Sin"	"Interior"	0.8555608786166787
1098	P05.EP.VI.CE.0,07.Sin.Interior	P05	EP	VI	CE	0.07	"Sin"	"Interior"	0.8736262848828107
1099	P05.EP.VI.CE.0,08.Sin.Interior	P05	EP	VI	CE	0.08	"Sin"	"Interior"	0.8916916911489425
1100	P05.EP.VI.CE.0,09.Sin.Interior	P05	EP	VI	CE	0.09	"Sin"	"Interior"	0.9097570974150745
1101	P05.EP.VI.CE.0,1.Sin.Interior	P05	EP	VI	CE	0.09999999999999999	"Sin"	"Interior"	0.9278225036812064
1102	P05.EP.VI.CE.0,11.Sin.Interior	P05	EP	VI	CE	0.10999999999999999	"Sin"	"Interior"	0.9458879099473383
1103	P05.EP.VI.CE.0,12.Sin.Interior	P05	EP	VI	CE	0.11999999999999998	"Sin"	"Interior"	0.9639533162134702
1104	P05.EP.VI.CE.0,13.Sin.Interior	P05	EP	VI	CE	0.12999999999999998	"Sin"	"Interior"	0.9820187224796022
1105	P05.EP.VI.CE.0,14.Sin.Interior	P05	EP	VI	CE	0.13999999999999999	"Sin"	"Interior"	1.0000841287457343
1106	P05.EP.VI.CE.0,15.Sin.Interior	P05	EP	VI	CE	0.15	"Sin"	"Interior"	1.0181495350118661
1107	P05.EP.VI.CE.0,16.Sin.Interior	P05	EP	VI	CE	0.16	"Sin"	"Interior"	1.036214941277998
1108	P05.EP.VI.CE.0,17.Sin.Interior	P05	EP	VI	CE	0.17	"Sin"	"Interior"	1.05428034754413
1109	P05.EP.VI.CE.0,18.Sin.Interior	P05	EP	VI	CE	0.18000000000000002	"Sin"	"Interior"	1.0723457538102619
1110	P05.EP.VI.CE.0,19.Sin.Interior	P05	EP	VI	CE	0.19000000000000003	"Sin"	"Interior"	1.090411160076394
1111	P05.EP.VI.CE.0,2.Sin.Interior	P05	EP	VI	CE	0.20000000000000004	"Sin"	"Interior"	1.1084765663425258
1112	P05.EI.VI.CE.0,01.Sin.Interior	P05	EI	VI	CE	0.01	"Sin"	"Interior"	0.30590420378103733
1113	P05.EI.VI.CE.0,02.Sin.Interior	P05	EI	VI	CE	0.02	"Sin"	"Interior"	0.3473193088431288
1114	P05.EI.VI.CE.0,03.Sin.Interior	P05	EI	VI	CE	0.03	"Sin"	"Interior"	0.38873441390522023
1115	P05.EI.VI.CE.0,04.Sin.Interior	P05	EI	VI	CE	0.04	"Sin"	"Interior"	0.4301495189673117
1116	P05.EI.VI.CE.0,05.Sin.Interior	P05	EI	VI	CE	0.05	"Sin"	"Interior"	0.47156462402940313
1117	P05.EI.VI.CE.0,06.Sin.Interior	P05	EI	VI	CE	0.060000000000000005	"Sin"	"Interior"	0.48349146518679226
1118	P05.EI.VI.CE.0,07.Sin.Interior	P05	EI	VI	CE	0.07	"Sin"	"Interior"	0.4954183063441814
1119	P05.EI.VI.CE.0,08.Sin.Interior	P05	EI	VI	CE	0.08	"Sin"	"Interior"	0.5073451475015706
1120	P05.EI.VI.CE.0,09.Sin.Interior	P05	EI	VI	CE	0.09	"Sin"	"Interior"	0.5192719886589596
1121	P05.EI.VI.CE.0,1.Sin.Interior	P05	EI	VI	CE	0.09999999999999999	"Sin"	"Interior"	0.5311988298163488
1122	P05.EI.VI.CE.0,11.Sin.Interior	P05	EI	VI	CE	0.10999999999999999	"Sin"	"Interior"	0.543125670973738
1123	P05.EI.VI.CE.0,12.Sin.Interior	P05	EI	VI	CE	0.11999999999999998	"Sin"	"Interior"	0.555052512131127
1124	P05.EI.VI.CE.0,13.Sin.Interior	P05	EI	VI	CE	0.12999999999999998	"Sin"	"Interior"	0.5669793532885161
1125	P05.EI.VI.CE.0,14.Sin.Interior	P05	EI	VI	CE	0.13999999999999999	"Sin"	"Interior"	0.5789061944459053
1126	P05.EI.VI.CE.0,15.Sin.Interior	P05	EI	VI	CE	0.15	"Sin"	"Interior"	0.5908330356032945
1127	P05.EI.VI.CE.0,16.Sin.Interior	P05	EI	VI	CE	0.16	"Sin"	"Interior"	0.6027598767606837
1128	P05.EI.VI.CE.0,17.Sin.Interior	P05	EI	VI	CE	0.17	"Sin"	"Interior"	0.6146867179180727
1129	P05.EI.VI.CE.0,18.Sin.Interior	P05	EI	VI	CE	0.18000000000000002	"Sin"	"Interior"	0.6266135590754619
1130	P05.EI.VI.CE.0,19.Sin.Interior	P05	EI	VI	CE	0.19000000000000003	"Sin"	"Interior"	0.6385404002328511
1131	P05.EI.VI.CE.0,2.Sin.Interior	P05	EI	VI	CE	0.20000000000000004	"Sin"	"Interior"	0.6504672413902401
1132	P05.EM.VI.CE.0,01.Sin.Interior	P05	EM	VI	CE	0.01	"Sin"	"Interior"	0.10714899982020087
1133	P05.EM.VI.CE.0,02.Sin.Interior	P05	EM	VI	CE	0.02	"Sin"	"Interior"	0.11730213042785775
1134	P05.EM.VI.CE.0,03.Sin.Interior	P05	EM	VI	CE	0.03	"Sin"	"Interior"	0.12745526103551463
1135	P05.EM.VI.CE.0,04.Sin.Interior	P05	EM	VI	CE	0.04	"Sin"	"Interior"	0.1376083916431715
1136	P05.EM.VI.CE.0,05.Sin.Interior	P05	EM	VI	CE	0.05	"Sin"	"Interior"	0.1477615222508284
1137	P05.EM.VI.CE.0,06.Sin.Interior	P05	EM	VI	CE	0.060000000000000005	"Sin"	"Interior"	0.15088085273602933
1138	P05.EM.VI.CE.0,07.Sin.Interior	P05	EM	VI	CE	0.07	"Sin"	"Interior"	0.15400018322123027
1139	P05.EM.VI.CE.0,08.Sin.Interior	P05	EM	VI	CE	0.08	"Sin"	"Interior"	0.15711951370643124
1140	P05.EM.VI.CE.0,09.Sin.Interior	P05	EM	VI	CE	0.09	"Sin"	"Interior"	0.16023884419163217
1141	P05.EM.VI.CE.0,1.Sin.Interior	P05	EM	VI	CE	0.09999999999999999	"Sin"	"Interior"	0.1633581746768331
1142	P05.EM.VI.CE.0,11.Sin.Interior	P05	EM	VI	CE	0.10999999999999999	"Sin"	"Interior"	0.16647750516203405
1143	P05.EM.VI.CE.0,12.Sin.Interior	P05	EM	VI	CE	0.11999999999999998	"Sin"	"Interior"	0.169596835647235
1144	P05.EM.VI.CE.0,13.Sin.Interior	P05	EM	VI	CE	0.12999999999999998	"Sin"	"Interior"	0.17271616613243593
1145	P05.EM.VI.CE.0,14.Sin.Interior	P05	EM	VI	CE	0.13999999999999999	"Sin"	"Interior"	0.1758354966176369
1146	P05.EM.VI.CE.0,15.Sin.Interior	P05	EM	VI	CE	0.15	"Sin"	"Interior"	0.17895482710283783
1147	P05.EM.VI.CE.0,16.Sin.Interior	P05	EM	VI	CE	0.16	"Sin"	"Interior"	0.18207415758803877
1148	P05.EM.VI.CE.0,17.Sin.Interior	P05	EM	VI	CE	0.17	"Sin"	"Interior"	0.1851934880732397
1149	P05.EM.VI.CE.0,18.Sin.Interior	P05	EM	VI	CE	0.18000000000000002	"Sin"	"Interior"	0.18831281855844068
1150	P05.EM.VI.CE.0,19.Sin.Interior	P05	EM	VI	CE	0.19000000000000003	"Sin"	"Interior"	0.19143214904364161
1151	P05.EM.VI.CE.0,2.Sin.Interior	P05	EM	VI	CE	0.20000000000000004	"Sin"	"Interior"	0.19455147952884255
1152	P05.EP.VI.CE.0,01.Con.Interior	P05	EP	VI	CE	0.01	"Con"	"Interior"	0.23565569311266898
1153	P05.EP.VI.CE.0,02.Con.Interior	P05	EP	VI	CE	0.02	"Con"	"Interior"	0.23914055458872274
1154	P05.EP.VI.CE.0,03.Con.Interior	P05	EP	VI	CE	0.03	"Con"	"Interior"	0.2426254160647765
1155	P05.EP.VI.CE.0,04.Con.Interior	P05	EP	VI	CE	0.04	"Con"	"Interior"	0.24611027754083026
1156	P05.EP.VI.CE.0,05.Con.Interior	P05	EP	VI	CE	0.05	"Con"	"Interior"	0.24959513901688402
1157	P05.EP.VI.CE.0,06.Con.Interior	P05	EP	VI	CE	0.060000000000000005	"Con"	"Interior"	0.2533739220500764
1158	P05.EP.VI.CE.0,07.Con.Interior	P05	EP	VI	CE	0.07	"Con"	"Interior"	0.2571527050832688
1159	P05.EP.VI.CE.0,08.Con.Interior	P05	EP	VI	CE	0.08	"Con"	"Interior"	0.26093148811646116
1160	P05.EP.VI.CE.0,09.Con.Interior	P05	EP	VI	CE	0.09	"Con"	"Interior"	0.26471027114965356
1161	P05.EP.VI.CE.0,1.Con.Interior	P05	EP	VI	CE	0.09999999999999999	"Con"	"Interior"	0.26848905418284597
1162	P05.EP.VI.CE.0,11.Con.Interior	P05	EP	VI	CE	0.10999999999999999	"Con"	"Interior"	0.27226783721603837
1163	P05.EP.VI.CE.0,12.Con.Interior	P05	EP	VI	CE	0.11999999999999998	"Con"	"Interior"	0.27604662024923077
1164	P05.EP.VI.CE.0,13.Con.Interior	P05	EP	VI	CE	0.12999999999999998	"Con"	"Interior"	0.2798254032824231
1165	P05.EP.VI.CE.0,14.Con.Interior	P05	EP	VI	CE	0.13999999999999999	"Con"	"Interior"	0.2836041863156155
1166	P05.EP.VI.CE.0,15.Con.Interior	P05	EP	VI	CE	0.15	"Con"	"Interior"	0.2873829693488079
1167	P05.EP.VI.CE.0,16.Con.Interior	P05	EP	VI	CE	0.16	"Con"	"Interior"	0.2911617523820003
1168	P05.EP.VI.CE.0,17.Con.Interior	P05	EP	VI	CE	0.17	"Con"	"Interior"	0.2949405354151927
1169	P05.EP.VI.CE.0,18.Con.Interior	P05	EP	VI	CE	0.18000000000000002	"Con"	"Interior"	0.29871931844838506
1170	P05.EP.VI.CE.0,19.Con.Interior	P05	EP	VI	CE	0.19000000000000003	"Con"	"Interior"	0.3024981014815775
1171	P05.EP.VI.CE.0,2.Con.Interior	P05	EP	VI	CE	0.20000000000000004	"Con"	"Interior"	0.30627688451476986
1172	P05.EI.VI.CE.0,01.Con.Interior	P05	EI	VI	CE	0.01	"Con"	"Interior"	0.18649894075692774
1173	P05.EI.VI.CE.0,02.Con.Interior	P05	EI	VI	CE	0.02	"Con"	"Interior"	0.19416840324163087
1174	P05.EI.VI.CE.0,03.Con.Interior	P05	EI	VI	CE	0.03	"Con"	"Interior"	0.201837865726334
1175	P05.EI.VI.CE.0,04.Con.Interior	P05	EI	VI	CE	0.04	"Con"	"Interior"	0.20950732821103712
1176	P05.EI.VI.CE.0,05.Con.Interior	P05	EI	VI	CE	0.05	"Con"	"Interior"	0.21717679069574025
1177	P05.EI.VI.CE.0,06.Con.Interior	P05	EI	VI	CE	0.060000000000000005	"Con"	"Interior"	0.22266325862018962
1178	P05.EI.VI.CE.0,07.Con.Interior	P05	EI	VI	CE	0.07	"Con"	"Interior"	0.228149726544639
1179	P05.EI.VI.CE.0,08.Con.Interior	P05	EI	VI	CE	0.08	"Con"	"Interior"	0.2336361944690884
1180	P05.EI.VI.CE.0,09.Con.Interior	P05	EI	VI	CE	0.09	"Con"	"Interior"	0.23912266239353777
1181	P05.EI.VI.CE.0,1.Con.Interior	P05	EI	VI	CE	0.09999999999999999	"Con"	"Interior"	0.24460913031798714
1182	P05.EI.VI.CE.0,11.Con.Interior	P05	EI	VI	CE	0.10999999999999999	"Con"	"Interior"	0.25009559824243655
1183	P05.EI.VI.CE.0,12.Con.Interior	P05	EI	VI	CE	0.11999999999999998	"Con"	"Interior"	0.2555820661668859
1184	P05.EI.VI.CE.0,13.Con.Interior	P05	EI	VI	CE	0.12999999999999998	"Con"	"Interior"	0.26106853409133524
1185	P05.EI.VI.CE.0,14.Con.Interior	P05	EI	VI	CE	0.13999999999999999	"Con"	"Interior"	0.26655500201578464
1186	P05.EI.VI.CE.0,15.Con.Interior	P05	EI	VI	CE	0.15	"Con"	"Interior"	0.27204146994023404
1187	P05.EI.VI.CE.0,16.Con.Interior	P05	EI	VI	CE	0.16	"Con"	"Interior"	0.27752793786468344
1188	P05.EI.VI.CE.0,17.Con.Interior	P05	EI	VI	CE	0.17	"Con"	"Interior"	0.2830144057891328
1189	P05.EI.VI.CE.0,18.Con.Interior	P05	EI	VI	CE	0.18000000000000002	"Con"	"Interior"	0.2885008737135822
1190	P05.EI.VI.CE.0,19.Con.Interior	P05	EI	VI	CE	0.19000000000000003	"Con"	"Interior"	0.2939873416380316
1191	P05.EI.VI.CE.0,2.Con.Interior	P05	EI	VI	CE	0.20000000000000004	"Con"	"Interior"	0.29947380956248093
1192	P05.EM.VI.CE.0,01.Con.Interior	P05	EM	VI	CE	0.01	"Con"	"Interior"	0.10285103788431238
1193	P05.EM.VI.CE.0,02.Con.Interior	P05	EM	VI	CE	0.02	"Con"	"Interior"	0.11226643616679166
1194	P05.EM.VI.CE.0,03.Con.Interior	P05	EM	VI	CE	0.03	"Con"	"Interior"	0.12168183444927094
1195	P05.EM.VI.CE.0,04.Con.Interior	P05	EM	VI	CE	0.04	"Con"	"Interior"	0.13109723273175022
1196	P05.EM.VI.CE.0,05.Con.Interior	P05	EM	VI	CE	0.05	"Con"	"Interior"	0.1405126310142295
1197	P05.EM.VI.CE.0,06.Con.Interior	P05	EM	VI	CE	0.060000000000000005	"Con"	"Interior"	0.14388917308001767
1198	P05.EM.VI.CE.0,07.Con.Interior	P05	EM	VI	CE	0.07	"Con"	"Interior"	0.14726571514580583
1199	P05.EM.VI.CE.0,08.Con.Interior	P05	EM	VI	CE	0.08	"Con"	"Interior"	0.15064225721159402
1200	P05.EM.VI.CE.0,09.Con.Interior	P05	EM	VI	CE	0.09	"Con"	"Interior"	0.15401879927738218
1201	P05.EM.VI.CE.0,1.Con.Interior	P05	EM	VI	CE	0.09999999999999999	"Con"	"Interior"	0.15739534134317035
1202	P05.EM.VI.CE.0,11.Con.Interior	P05	EM	VI	CE	0.10999999999999999	"Con"	"Interior"	0.1607718834089585
1203	P05.EM.VI.CE.0,12.Con.Interior	P05	EM	VI	CE	0.11999999999999998	"Con"	"Interior"	0.16414842547474667
1204	P05.EM.VI.CE.0,13.Con.Interior	P05	EM	VI	CE	0.12999999999999998	"Con"	"Interior"	0.16752496754053484
1205	P05.EM.VI.CE.0,14.Con.Interior	P05	EM	VI	CE	0.13999999999999999	"Con"	"Interior"	0.170901509606323
1206	P05.EM.VI.CE.0,15.Con.Interior	P05	EM	VI	CE	0.15	"Con"	"Interior"	0.1742780516721112
1207	P05.EM.VI.CE.0,16.Con.Interior	P05	EM	VI	CE	0.16	"Con"	"Interior"	0.17765459373789935
1208	P05.EM.VI.CE.0,17.Con.Interior	P05	EM	VI	CE	0.17	"Con"	"Interior"	0.18103113580368752
1209	P05.EM.VI.CE.0,18.Con.Interior	P05	EM	VI	CE	0.18000000000000002	"Con"	"Interior"	0.1844076778694757
1210	P05.EM.VI.CE.0,19.Con.Interior	P05	EM	VI	CE	0.19000000000000003	"Con"	"Interior"	0.18778421993526387
1211	P05.EM.VI.CE.0,2.Con.Interior	P05	EM	VI	CE	0.20000000000000004	"Con"	"Interior"	0.19116076200105203
1212	P05.EL.VI.IE.0,01.Con.Interior	P05	EL	VI	CE	0.01	"Con"	"Interior"	0.21647490532900182
1213	P05.EL.VI.CE.0,02.Con.Interior	P05	EL	VI	CE	0.02	"Con"	"Interior"	0.21306564428938946
1214	P05.EL.VI.CE.0,03.Con.Interior	P05	EL	VI	CE	0.03	"Con"	"Interior"	0.2096563832497771
1215	P05.EL.VI.CE.0,04.Con.Interior	P05	EL	VI	CE	0.04	"Con"	"Interior"	0.20624712221016472
1216	P05.EL.VI.IE.0,05.Con.Interior	P05	EL	VI	CE	0.05	"Con"	"Interior"	0.20283786117055236
1217	P05.EL.VI.CE.0,06.Con.Interior	P05	EL	VI	CE	0.060000000000000005	"Con"	"Interior"	0.1997883428344605
1218	P05.EL.VI.CE.0,07.Con.Interior	P05	EL	VI	CE	0.07	"Con"	"Interior"	0.19673882449836863
1219	P05.EL.VI.CE.0,08.Con.Interior	P05	EL	VI	CE	0.08	"Con"	"Interior"	0.19368930616227678
1220	P05.EL.VI.CE.0,09.Con.Interior	P05	EL	VI	CE	0.09	"Con"	"Interior"	0.1906397878261849
1221	P05.EL.VI.IE.0,1.Con.Interior	P05	EL	VI	CE	0.09999999999999999	"Con"	"Interior"	0.18759026949009305
1222	P05.EL.VI.CE.0,11.Con.Interior	P05	EL	VI	CE	0.10999999999999999	"Con"	"Interior"	0.1845407511540012
1223	P05.EL.VI.CE.0,12.Con.Interior	P05	EL	VI	CE	0.11999999999999998	"Con"	"Interior"	0.18149123281790935
1224	P05.EL.VI.CE.0,13.Con.Interior	P05	EL	VI	CE	0.12999999999999998	"Con"	"Interior"	0.17844171448181748
1225	P05.EL.VI.CE.0,14.Con.Interior	P05	EL	VI	CE	0.13999999999999999	"Con"	"Interior"	0.1753921961457256
1226	P05.EL.VI.CE.0,15.Con.Interior	P05	EL	VI	CE	0.15	"Con"	"Interior"	0.17234267780963375
1227	P05.EL.VI.CE.0,16.Con.Interior	P05	EL	VI	CE	0.16	"Con"	"Interior"	0.1692931594735419
1228	P05.EL.VI.CE.0,17.Con.Interior	P05	EL	VI	CE	0.17	"Con"	"Interior"	0.16624364113745002
1229	P05.EL.VI.CE.0,18.Con.Interior	P05	EL	VI	CE	0.18000000000000002	"Con"	"Interior"	0.16319412280135814
1230	P05.EL.VI.CE.0,19.Con.Interior	P05	EL	VI	CE	0.19000000000000003	"Con"	"Interior"	0.1601446044652663
1231	P05.EL.VI.CE.0,2.Con.Interior	P05	EL	VI	CE	0.20000000000000004	"Con"	"Interior"	0.15709508612917444
1232	P05.EP.VI.SA.0.Sin.Centrada	P05	EP	VI	SA	0	"Sin"	"Centrada"	0.26281573161275684
1233	P05.EI.VI.SA.0.Sin.Centrada	P05	EI	VI	SA	0	"Sin"	"Centrada"	1.2652953943896668
1234	P05.EM.VI.SA.0.Sin.Centrada	P05	EM	VI	SA	0	"Sin"	"Centrada"	0.06743991550777295
1235	P05.EL.VI.SA.0.Sin.Centrada	P05	EL	VI	SA	0	"Sin"	"Centrada"	0.08212703711155012
1236	P05.EP.VI.CI.0,01.Sin.Centrada	P05	EP	VI	CI	0.01	"Sin"	"Centrada"	0.34040470613677787
1237	P05.EP.VI.CI.0,02.Sin.Centrada	P05	EP	VI	CI	0.02	"Sin"	"Centrada"	0.3668044886505153
1238	P05.EP.VI.CI.0,03.Sin.Centrada	P05	EP	VI	CI	0.03	"Sin"	"Centrada"	0.3932042711642527
1239	P05.EP.VI.CI.0,04.Sin.Centrada	P05	EP	VI	CI	0.04	"Sin"	"Centrada"	0.4352350036812065
1240	P05.EP.VI.CI.0,05.Sin.Centrada	P05	EP	VI	CI	0.05	"Sin"	"Centrada"	0.47726573619816026
1241	P05.EP.VI.CI.0,06.Sin.Centrada	P05	EP	VI	CI	0.060000000000000005	"Sin"	"Centrada"	0.519296468715114
1242	P05.EP.VI.CI.0,07.Sin.Centrada	P05	EP	VI	CI	0.07	"Sin"	"Centrada"	0.5613272012320678
1243	P05.EP.VI.CI.0,08.Sin.Centrada	P05	EP	VI	CI	0.08	"Sin"	"Centrada"	0.5613272012320678
1244	P05.EP.VI.CI.0,09.Sin.Centrada	P05	EP	VI	CI	0.09	"Sin"	"Centrada"	0.5613272012320678
1245	P05.EP.VI.CI.0,1.Sin.Centrada	P05	EP	VI	CI	0.09999999999999999	"Sin"	"Centrada"	0.5613272012320678
1246	P05.EP.VI.CI.0,11.Sin.Centrada	P05	EP	VI	CI	0.10999999999999999	"Sin"	"Centrada"	0.5613272012320678
1247	P05.EP.VI.CI.0,12.Sin.Centrada	P05	EP	VI	CI	0.11999999999999998	"Sin"	"Centrada"	0.5613272012320678
1248	P05.EP.VI.CI.0,13.Sin.Centrada	P05	EP	VI	CI	0.12999999999999998	"Sin"	"Centrada"	0.5613272012320678
1249	P05.EP.VI.CI.0,14.Sin.Centrada	P05	EP	VI	CI	0.13999999999999999	"Sin"	"Centrada"	0.5613272012320678
1250	P05.EP.VI.CI.0,15.Sin.Centrada	P05	EP	VI	CI	0.15	"Sin"	"Centrada"	0.5613272012320678
1251	P05.EP.VI.CI.0,16.Sin.Centrada	P05	EP	VI	CI	0.16	"Sin"	"Centrada"	0.5613272012320678
1252	P05.EP.VI.CI.0,17.Sin.Centrada	P05	EP	VI	CI	0.17	"Sin"	"Centrada"	0.5613272012320678
1253	P05.EP.VI.CI.0,18.Sin.Centrada	P05	EP	VI	CI	0.18000000000000002	"Sin"	"Centrada"	0.5613272012320678
1254	P05.EP.VI.CI.0,19.Sin.Centrada	P05	EP	VI	CI	0.19000000000000003	"Sin"	"Centrada"	0.5613272012320678
1255	P05.EP.VI.CI.0,2.Sin.Centrada	P05	EP	VI	CI	0.20000000000000004	"Sin"	"Centrada"	0.5613272012320678
1256	P05.EI.VI.CI.0,01.Sin.Centrada	P05	EI	VI	CI	0.01	"Sin"	"Centrada"	0.20955420378103717
1257	P05.EI.VI.CI.0,02.Sin.Centrada	P05	EI	VI	CI	0.02	"Sin"	"Centrada"	0.23097821621353432
1258	P05.EI.VI.CI.0,03.Sin.Centrada	P05	EI	VI	CI	0.03	"Sin"	"Centrada"	0.25240222864603146
1259	P05.EI.VI.CI.0,04.Sin.Centrada	P05	EI	VI	CI	0.04	"Sin"	"Centrada"	0.3019238298163489
1260	P05.EI.VI.CI.0,05.Sin.Centrada	P05	EI	VI	CI	0.05	"Sin"	"Centrada"	0.35144543098666636
1261	P05.EI.VI.CI.0,06.Sin.Centrada	P05	EI	VI	CI	0.060000000000000005	"Sin"	"Centrada"	0.4009670321569838
1262	P05.EI.VI.CI.0,07.Sin.Centrada	P05	EI	VI	CI	0.07	"Sin"	"Centrada"	0.45048863332730127
1263	P05.EI.VI.CI.0,08.Sin.Centrada	P05	EI	VI	CI	0.08	"Sin"	"Centrada"	0.45048863332730127
1264	P05.EI.VI.CI.0,09.Sin.Centrada	P05	EI	VI	CI	0.09	"Sin"	"Centrada"	0.45048863332730127
1265	P05.EI.VI.CI.0,1.Sin.Centrada	P05	EI	VI	CI	0.09999999999999999	"Sin"	"Centrada"	0.45048863332730127
1266	P05.EI.VI.CI.0,11.Sin.Centrada	P05	EI	VI	CI	0.10999999999999999	"Sin"	"Centrada"	0.45048863332730127
1267	P05.EI.VI.CI.0,12.Sin.Centrada	P05	EI	VI	CI	0.11999999999999998	"Sin"	"Centrada"	0.45048863332730127
1268	P05.EI.VI.CI.0,13.Sin.Centrada	P05	EI	VI	CI	0.12999999999999998	"Sin"	"Centrada"	0.45048863332730127
1269	P05.EI.VI.CI.0,14.Sin.Centrada	P05	EI	VI	CI	0.13999999999999999	"Sin"	"Centrada"	0.45048863332730127
1270	P05.EI.VI.CI.0,15.Sin.Centrada	P05	EI	VI	CI	0.15	"Sin"	"Centrada"	0.45048863332730127
1271	P05.EI.VI.CI.0,16.Sin.Centrada	P05	EI	VI	CI	0.16	"Sin"	"Centrada"	0.45048863332730127
1272	P05.EI.VI.CI.0,17.Sin.Centrada	P05	EI	VI	CI	0.17	"Sin"	"Centrada"	0.45048863332730127
1273	P05.EI.VI.CI.0,18.Sin.Centrada	P05	EI	VI	CI	0.18000000000000002	"Sin"	"Centrada"	0.45048863332730127
1274	P05.EI.VI.CI.0,19.Sin.Centrada	P05	EI	VI	CI	0.19000000000000003	"Sin"	"Centrada"	0.45048863332730127
1275	P05.EI.VI.CI.0,2.Sin.Centrada	P05	EI	VI	CI	0.20000000000000004	"Sin"	"Centrada"	0.45048863332730127
1276	P05.EM.VI.CI.0,01.Sin.Centrada	P05	EM	VI	CI	0.01	"Sin"	"Centrada"	0.07870524982020122
1277	P05.EM.VI.CI.0,02.Sin.Centrada	P05	EM	VI	CI	0.02	"Sin"	"Centrada"	0.09099066306243575
1278	P05.EM.VI.CI.0,03.Sin.Centrada	P05	EM	VI	CI	0.03	"Sin"	"Centrada"	0.10327607630467028
1279	P05.EM.VI.CI.0,04.Sin.Centrada	P05	EM	VI	CI	0.04	"Sin"	"Centrada"	0.10898942467683304
1280	P05.EM.VI.CI.0,05.Sin.Centrada	P05	EM	VI	CI	0.05	"Sin"	"Centrada"	0.11470277304899579
1281	P05.EM.VI.CI.0,06.Sin.Centrada	P05	EM	VI	CI	0.060000000000000005	"Sin"	"Centrada"	0.12041612142115854
1282	P05.EM.VI.CI.0,07.Sin.Centrada	P05	EM	VI	CI	0.07	"Sin"	"Centrada"	0.1261294697933213
1283	P05.EM.VI.CI.0,08.Sin.Centrada	P05	EM	VI	CI	0.08	"Sin"	"Centrada"	0.1261294697933213
1284	P05.EM.VI.CI.0,09.Sin.Centrada	P05	EM	VI	CI	0.09	"Sin"	"Centrada"	0.1261294697933213
1285	P05.EM.VI.CI.0,1.Sin.Centrada	P05	EM	VI	CI	0.09999999999999999	"Sin"	"Centrada"	0.1261294697933213
1286	P05.EM.VI.CI.0,11.Sin.Centrada	P05	EM	VI	CI	0.10999999999999999	"Sin"	"Centrada"	0.1261294697933213
1287	P05.EM.VI.CI.0,12.Sin.Centrada	P05	EM	VI	CI	0.11999999999999998	"Sin"	"Centrada"	0.1261294697933213
1288	P05.EM.VI.CI.0,13.Sin.Centrada	P05	EM	VI	CI	0.12999999999999998	"Sin"	"Centrada"	0.1261294697933213
1289	P05.EM.VI.CI.0,14.Sin.Centrada	P05	EM	VI	CI	0.13999999999999999	"Sin"	"Centrada"	0.1261294697933213
1290	P05.EM.VI.CI.0,15.Sin.Centrada	P05	EM	VI	CI	0.15	"Sin"	"Centrada"	0.1261294697933213
1291	P05.EM.VI.CI.0,16.Sin.Centrada	P05	EM	VI	CI	0.16	"Sin"	"Centrada"	0.1261294697933213
1292	P05.EM.VI.CI.0,17.Sin.Centrada	P05	EM	VI	CI	0.17	"Sin"	"Centrada"	0.1261294697933213
1293	P05.EM.VI.CI.0,18.Sin.Centrada	P05	EM	VI	CI	0.18000000000000002	"Sin"	"Centrada"	0.1261294697933213
1294	P05.EM.VI.CI.0,19.Sin.Centrada	P05	EM	VI	CI	0.19000000000000003	"Sin"	"Centrada"	0.1261294697933213
1295	P05.EM.VI.CI.0,2.Sin.Centrada	P05	EM	VI	CI	0.20000000000000004	"Sin"	"Centrada"	0.1261294697933213
1296	P05.EP.VI.CE.0,01.Sin.Centrada	P05	EP	VI	CE	0.01	"Sin"	"Centrada"	0.4218672061367785
1297	P05.EP.VI.CE.0,02.Sin.Centrada	P05	EP	VI	CE	0.02	"Sin"	"Centrada"	0.47640864769022073
1298	P05.EP.VI.CE.0,03.Sin.Centrada	P05	EP	VI	CE	0.03	"Sin"	"Centrada"	0.5309500892436629
1299	P05.EP.VI.CE.0,04.Sin.Centrada	P05	EP	VI	CE	0.04	"Sin"	"Centrada"	0.5854915307971051
1300	P05.EP.VI.CE.0,05.Sin.Centrada	P05	EP	VI	CE	0.05	"Sin"	"Centrada"	0.6400329723505473
1301	P05.EP.VI.CE.0,06.Sin.Centrada	P05	EP	VI	CE	0.060000000000000005	"Sin"	"Centrada"	0.6536133786166791
1302	P05.EP.VI.CE.0,07.Sin.Centrada	P05	EP	VI	CE	0.07	"Sin"	"Centrada"	0.667193784882811
1303	P05.EP.VI.CE.0,08.Sin.Centrada	P05	EP	VI	CE	0.08	"Sin"	"Centrada"	0.6807741911489428
1304	P05.EP.VI.CE.0,09.Sin.Centrada	P05	EP	VI	CE	0.09	"Sin"	"Centrada"	0.6943545974150747
1305	P05.EP.VI.CE.0,1.Sin.Centrada	P05	EP	VI	CE	0.09999999999999999	"Sin"	"Centrada"	0.7079350036812064
1306	P05.EP.VI.CE.0,11.Sin.Centrada	P05	EP	VI	CE	0.10999999999999999	"Sin"	"Centrada"	0.7215154099473382
1307	P05.EP.VI.CE.0,12.Sin.Centrada	P05	EP	VI	CE	0.11999999999999998	"Sin"	"Centrada"	0.73509581621347
1308	P05.EP.VI.CE.0,13.Sin.Centrada	P05	EP	VI	CE	0.12999999999999998	"Sin"	"Centrada"	0.7486762224796019
1309	P05.EP.VI.CE.0,14.Sin.Centrada	P05	EP	VI	CE	0.13999999999999999	"Sin"	"Centrada"	0.7622566287457337
1310	P05.EP.VI.CE.0,15.Sin.Centrada	P05	EP	VI	CE	0.15	"Sin"	"Centrada"	0.7758370350118655
1311	P05.EP.VI.CE.0,16.Sin.Centrada	P05	EP	VI	CE	0.16	"Sin"	"Centrada"	0.7894174412779973
1312	P05.EP.VI.CE.0,17.Sin.Centrada	P05	EP	VI	CE	0.17	"Sin"	"Centrada"	0.8029978475441292
1313	P05.EP.VI.CE.0,18.Sin.Centrada	P05	EP	VI	CE	0.18000000000000002	"Sin"	"Centrada"	0.8165782538102611
1314	P05.EP.VI.CE.0,19.Sin.Centrada	P05	EP	VI	CE	0.19000000000000003	"Sin"	"Centrada"	0.8301586600763928
1315	P05.EP.VI.CE.0,2.Sin.Centrada	P05	EP	VI	CE	0.20000000000000004	"Sin"	"Centrada"	0.8437390663425246
1316	P05.EI.VI.CE.0,01.Sin.Centrada	P05	EI	VI	CE	0.01	"Sin"	"Centrada"	0.23293545378103708
1317	P05.EI.VI.CE.0,02.Sin.Centrada	P05	EI	VI	CE	0.02	"Sin"	"Centrada"	0.2622318088431286
1318	P05.EI.VI.CE.0,03.Sin.Centrada	P05	EI	VI	CE	0.03	"Sin"	"Centrada"	0.2915281639052201
1319	P05.EI.VI.CE.0,04.Sin.Centrada	P05	EI	VI	CE	0.04	"Sin"	"Centrada"	0.32082451896731157
1320	P05.EI.VI.CE.0,05.Sin.Centrada	P05	EI	VI	CE	0.05	"Sin"	"Centrada"	0.35012087402940306
1321	P05.EI.VI.CE.0,06.Sin.Centrada	P05	EI	VI	CE	0.060000000000000005	"Sin"	"Centrada"	0.35943271518679215
1322	P05.EI.VI.CE.0,07.Sin.Centrada	P05	EI	VI	CE	0.07	"Sin"	"Centrada"	0.36874455634418124
1323	P05.EI.VI.CE.0,08.Sin.Centrada	P05	EI	VI	CE	0.08	"Sin"	"Centrada"	0.3780563975015704
1324	P05.EI.VI.CE.0,09.Sin.Centrada	P05	EI	VI	CE	0.09	"Sin"	"Centrada"	0.3873682386589595
1325	P05.EI.VI.CE.0,1.Sin.Centrada	P05	EI	VI	CE	0.09999999999999999	"Sin"	"Centrada"	0.39668007981634856
1326	P05.EI.VI.CE.0,11.Sin.Centrada	P05	EI	VI	CE	0.10999999999999999	"Sin"	"Centrada"	0.40599192097373765
1327	P05.EI.VI.CE.0,12.Sin.Centrada	P05	EI	VI	CE	0.11999999999999998	"Sin"	"Centrada"	0.41530376213112674
1328	P05.EI.VI.CE.0,13.Sin.Centrada	P05	EI	VI	CE	0.12999999999999998	"Sin"	"Centrada"	0.42461560328851583
1329	P05.EI.VI.CE.0,14.Sin.Centrada	P05	EI	VI	CE	0.13999999999999999	"Sin"	"Centrada"	0.4339274444459049
1330	P05.EI.VI.CE.0,15.Sin.Centrada	P05	EI	VI	CE	0.15	"Sin"	"Centrada"	0.44323928560329406
1331	P05.EI.VI.CE.0,16.Sin.Centrada	P05	EI	VI	CE	0.16	"Sin"	"Centrada"	0.4525511267606832
1332	P05.EI.VI.CE.0,17.Sin.Centrada	P05	EI	VI	CE	0.17	"Sin"	"Centrada"	0.46186296791807224
1333	P05.EI.VI.CE.0,18.Sin.Centrada	P05	EI	VI	CE	0.18000000000000002	"Sin"	"Centrada"	0.4711748090754614
1334	P05.EI.VI.CE.0,19.Sin.Centrada	P05	EI	VI	CE	0.19000000000000003	"Sin"	"Centrada"	0.48048665023285053
1335	P05.EI.VI.CE.0,2.Sin.Centrada	P05	EI	VI	CE	0.20000000000000004	"Sin"	"Centrada"	0.48979849139023957
1336	P05.EM.VI.CE.0,01.Sin.Centrada	P05	EM	VI	CE	0.01	"Sin"	"Centrada"	0.07879274982020101
1337	P05.EM.VI.CE.0,02.Sin.Centrada	P05	EM	VI	CE	0.02	"Sin"	"Centrada"	0.0855318179278578
1338	P05.EM.VI.CE.0,03.Sin.Centrada	P05	EM	VI	CE	0.03	"Sin"	"Centrada"	0.09227088603551459
1339	P05.EM.VI.CE.0,04.Sin.Centrada	P05	EM	VI	CE	0.04	"Sin"	"Centrada"	0.09900995414317137
1340	P05.EM.VI.CE.0,05.Sin.Centrada	P05	EM	VI	CE	0.05	"Sin"	"Centrada"	0.10574902225082816
1341	P05.EM.VI.CE.0,06.Sin.Centrada	P05	EM	VI	CE	0.060000000000000005	"Sin"	"Centrada"	0.10889085273602914
1342	P05.EM.VI.CE.0,07.Sin.Centrada	P05	EM	VI	CE	0.07	"Sin"	"Centrada"	0.11203268322123013
1343	P05.EM.VI.CE.0,08.Sin.Centrada	P05	EM	VI	CE	0.08	"Sin"	"Centrada"	0.1151745137064311
1344	P05.EM.VI.CE.0,09.Sin.Centrada	P05	EM	VI	CE	0.09	"Sin"	"Centrada"	0.11831634419163209
1345	P05.EM.VI.CE.0,1.Sin.Centrada	P05	EM	VI	CE	0.09999999999999999	"Sin"	"Centrada"	0.12145817467683306
1346	P05.EM.VI.CE.0,11.Sin.Centrada	P05	EM	VI	CE	0.10999999999999999	"Sin"	"Centrada"	0.12460000516203404
1347	P05.EM.VI.CE.0,12.Sin.Centrada	P05	EM	VI	CE	0.11999999999999998	"Sin"	"Centrada"	0.127741835647235
1348	P05.EM.VI.CE.0,13.Sin.Centrada	P05	EM	VI	CE	0.12999999999999998	"Sin"	"Centrada"	0.130883666132436
1349	P05.EM.VI.CE.0,14.Sin.Centrada	P05	EM	VI	CE	0.13999999999999999	"Sin"	"Centrada"	0.134025496617637
1350	P05.EM.VI.CE.0,15.Sin.Centrada	P05	EM	VI	CE	0.15	"Sin"	"Centrada"	0.13716732710283797
1351	P05.EM.VI.CE.0,16.Sin.Centrada	P05	EM	VI	CE	0.16	"Sin"	"Centrada"	0.14030915758803894
1352	P05.EM.VI.CE.0,17.Sin.Centrada	P05	EM	VI	CE	0.17	"Sin"	"Centrada"	0.14345098807323992
1353	P05.EM.VI.CE.0,18.Sin.Centrada	P05	EM	VI	CE	0.18000000000000002	"Sin"	"Centrada"	0.14659281855844092
1354	P05.EM.VI.CE.0,19.Sin.Centrada	P05	EM	VI	CE	0.19000000000000003	"Sin"	"Centrada"	0.1497346490436419
1355	P05.EM.VI.CE.0,2.Sin.Centrada	P05	EM	VI	CE	0.20000000000000004	"Sin"	"Centrada"	0.15287647952884287
1356	P05.EP.VI.CI.0,01.Con.Centrada	P05	EP	VI	CI	0.01	"Con"	"Centrada"	0.1857738290982489
1357	P05.EP.VI.CI.0,02.Con.Centrada	P05	EP	VI	CI	0.02	"Con"	"Centrada"	0.16705223911960942
1358	P05.EP.VI.CI.0,03.Con.Centrada	P05	EP	VI	CI	0.03	"Con"	"Centrada"	0.14833064914096994
1359	P05.EP.VI.CI.0,04.Con.Centrada	P05	EP	VI	CI	0.04	"Con"	"Centrada"	0.1627378336534817
1360	P05.EP.VI.CI.0,05.Con.Centrada	P05	EP	VI	CI	0.05	"Con"	"Centrada"	0.17714501816599348
1361	P05.EP.VI.CI.0,06.Con.Centrada	P05	EP	VI	CI	0.060000000000000005	"Con"	"Centrada"	0.19155220267850526
1362	P05.EP.VI.CI.0,07.Con.Centrada	P05	EP	VI	CI	0.07	"Con"	"Centrada"	0.20595938719101703
1363	P05.EP.VI.CI.0,08.Con.Centrada	P05	EP	VI	CI	0.08	"Con"	"Centrada"	0.20595938719101703
1364	P05.EP.VI.CI.0,09.Con.Centrada	P05	EP	VI	CI	0.09	"Con"	"Centrada"	0.20595938719101703
1365	P05.EP.VI.CI.0,1.Con.Centrada	P05	EP	VI	CI	0.09999999999999999	"Con"	"Centrada"	0.20595938719101703
1366	P05.EP.VI.CI.0,11.Con.Centrada	P05	EP	VI	CI	0.10999999999999999	"Con"	"Centrada"	0.20595938719101703
1367	P05.EP.VI.CI.0,12.Con.Centrada	P05	EP	VI	CI	0.11999999999999998	"Con"	"Centrada"	0.20595938719101703
1368	P05.EP.VI.CI.0,13.Con.Centrada	P05	EP	VI	CI	0.12999999999999998	"Con"	"Centrada"	0.20595938719101703
1369	P05.EP.VI.CI.0,14.Con.Centrada	P05	EP	VI	CI	0.13999999999999999	"Con"	"Centrada"	0.20595938719101703
1370	P05.EP.VI.CI.0,15.Con.Centrada	P05	EP	VI	CI	0.15	"Con"	"Centrada"	0.20595938719101703
1371	P05.EP.VI.CI.0,16.Con.Centrada	P05	EP	VI	CI	0.16	"Con"	"Centrada"	0.20595938719101703
1372	P05.EP.VI.CI.0,17.Con.Centrada	P05	EP	VI	CI	0.17	"Con"	"Centrada"	0.20595938719101703
1373	P05.EP.VI.CI.0,18.Con.Centrada	P05	EP	VI	CI	0.18000000000000002	"Con"	"Centrada"	0.20595938719101703
1374	P05.EP.VI.CI.0,19.Con.Centrada	P05	EP	VI	CI	0.19000000000000003	"Con"	"Centrada"	0.20595938719101703
1375	P05.EP.VI.CI.0,2.Con.Centrada	P05	EP	VI	CI	0.20000000000000004	"Con"	"Centrada"	0.20595938719101703
1376	P05.EI.VI.CI.0,01.Con.Centrada	P05	EI	VI	CI	0.01	"Con"	"Centrada"	0.13654832674250716
1377	P05.EI.VI.CI.0,02.Con.Centrada	P05	EI	VI	CI	0.02	"Con"	"Centrada"	0.13275721668262808
1378	P05.EI.VI.CI.0,03.Con.Centrada	P05	EI	VI	CI	0.03	"Con"	"Centrada"	0.128966106622749
1379	P05.EI.VI.CI.0,04.Con.Centrada	P05	EI	VI	CI	0.04	"Con"	"Centrada"	0.14583915978862283
1380	P05.EI.VI.CI.0,05.Con.Centrada	P05	EI	VI	CI	0.05	"Con"	"Centrada"	0.16271221295449667
1381	P05.EI.VI.CI.0,06.Con.Centrada	P05	EI	VI	CI	0.060000000000000005	"Con"	"Centrada"	0.1795852661203705
1382	P05.EI.VI.CI.0,07.Con.Centrada	P05	EI	VI	CI	0.07	"Con"	"Centrada"	0.19645831928624435
1383	P05.EI.VI.CI.0,08.Con.Centrada	P05	EI	VI	CI	0.08	"Con"	"Centrada"	0.19645831928624435
1384	P05.EI.VI.CI.0,09.Con.Centrada	P05	EI	VI	CI	0.09	"Con"	"Centrada"	0.19645831928624435
1385	P05.EI.VI.CI.0,1.Con.Centrada	P05	EI	VI	CI	0.09999999999999999	"Con"	"Centrada"	0.19645831928624435
1386	P05.EI.VI.CI.0,11.Con.Centrada	P05	EI	VI	CI	0.10999999999999999	"Con"	"Centrada"	0.19645831928624435
1387	P05.EI.VI.CI.0,12.Con.Centrada	P05	EI	VI	CI	0.11999999999999998	"Con"	"Centrada"	0.19645831928624435
1388	P05.EI.VI.CI.0,13.Con.Centrada	P05	EI	VI	CI	0.12999999999999998	"Con"	"Centrada"	0.19645831928624435
1389	P05.EI.VI.CI.0,14.Con.Centrada	P05	EI	VI	CI	0.13999999999999999	"Con"	"Centrada"	0.19645831928624435
1390	P05.EI.VI.CI.0,15.Con.Centrada	P05	EI	VI	CI	0.15	"Con"	"Centrada"	0.19645831928624435
1391	P05.EI.VI.CI.0,16.Con.Centrada	P05	EI	VI	CI	0.16	"Con"	"Centrada"	0.19645831928624435
1392	P05.EI.VI.CI.0,17.Con.Centrada	P05	EI	VI	CI	0.17	"Con"	"Centrada"	0.19645831928624435
1393	P05.EI.VI.CI.0,18.Con.Centrada	P05	EI	VI	CI	0.18000000000000002	"Con"	"Centrada"	0.19645831928624435
1394	P05.EI.VI.CI.0,19.Con.Centrada	P05	EI	VI	CI	0.19000000000000003	"Con"	"Centrada"	0.19645831928624435
1395	P05.EI.VI.CI.0,2.Con.Centrada	P05	EI	VI	CI	0.20000000000000004	"Con"	"Centrada"	0.19645831928624435
1396	P05.EM.VI.CI.0,01.Con.Centrada	P05	EM	VI	CI	0.01	"Con"	"Centrada"	0.07953475168394686
1397	P05.EM.VI.CI.0,02.Con.Centrada	P05	EM	VI	CI	0.02	"Con"	"Centrada"	0.09252410112533194
1398	P05.EM.VI.CI.0,03.Con.Centrada	P05	EM	VI	CI	0.03	"Con"	"Centrada"	0.10551345056671703
1399	P05.EM.VI.CI.0,04.Con.Centrada	P05	EM	VI	CI	0.04	"Con"	"Centrada"	0.0848306230485605
1400	P05.EM.VI.CI.0,05.Con.Centrada	P05	EM	VI	CI	0.05	"Con"	"Centrada"	0.06414779553040396
1401	P05.EM.VI.CI.0,06.Con.Centrada	P05	EM	VI	CI	0.060000000000000005	"Con"	"Centrada"	0.04346496801224743
1402	P05.EM.VI.CI.0,07.Con.Centrada	P05	EM	VI	CI	0.07	"Con"	"Centrada"	0.022782140494090913
1403	P05.EM.VI.CI.0,08.Con.Centrada	P05	EM	VI	CI	0.08	"Con"	"Centrada"	0.022782140494090913
1404	P05.EM.VI.CI.0,09.Con.Centrada	P05	EM	VI	CI	0.09	"Con"	"Centrada"	0.022782140494090913
1405	P05.EM.VI.CI.0,1.Con.Centrada	P05	EM	VI	CI	0.09999999999999999	"Con"	"Centrada"	0.022782140494090913
1406	P05.EM.VI.CI.0,11.Con.Centrada	P05	EM	VI	CI	0.10999999999999999	"Con"	"Centrada"	0.022782140494090913
1407	P05.EM.VI.CI.0,12.Con.Centrada	P05	EM	VI	CI	0.11999999999999998	"Con"	"Centrada"	0.022782140494090913
1408	P05.EM.VI.CI.0,13.Con.Centrada	P05	EM	VI	CI	0.12999999999999998	"Con"	"Centrada"	0.022782140494090913
1409	P05.EM.VI.CI.0,14.Con.Centrada	P05	EM	VI	CI	0.13999999999999999	"Con"	"Centrada"	0.022782140494090913
1410	P05.EM.VI.CI.0,15.Con.Centrada	P05	EM	VI	CI	0.15	"Con"	"Centrada"	0.022782140494090913
1411	P05.EM.VI.CI.0,16.Con.Centrada	P05	EM	VI	CI	0.16	"Con"	"Centrada"	0.022782140494090913
1412	P05.EM.VI.CI.0,17.Con.Centrada	P05	EM	VI	CI	0.17	"Con"	"Centrada"	0.022782140494090913
1413	P05.EM.VI.CI.0,18.Con.Centrada	P05	EM	VI	CI	0.18000000000000002	"Con"	"Centrada"	0.022782140494090913
1414	P05.EM.VI.CI.0,19.Con.Centrada	P05	EM	VI	CI	0.19000000000000003	"Con"	"Centrada"	0.022782140494090913
1415	P05.EM.VI.CI.0,2.Con.Centrada	P05	EM	VI	CI	0.20000000000000004	"Con"	"Centrada"	0.022782140494090913
1416	P05.EP.VI.CE.0,01.Con.Centrada	P05	EP	VI	CE	0.01	"Con"	"Centrada"	0.20248632909824948
1417	P05.EP.VI.CE.0,02.Con.Centrada	P05	EP	VI	CE	0.02	"Con"	"Centrada"	0.20013112502749864
1418	P05.EP.VI.CE.0,03.Con.Centrada	P05	EP	VI	CE	0.03	"Con"	"Centrada"	0.19777592095674779
1419	P05.EP.VI.CE.0,04.Con.Centrada	P05	EP	VI	CE	0.04	"Con"	"Centrada"	0.19542071688599694
1420	P05.EP.VI.CE.0,05.Con.Centrada	P05	EP	VI	CE	0.05	"Con"	"Centrada"	0.1930655128152461
1421	P05.EP.VI.CE.0,06.Con.Centrada	P05	EP	VI	CE	0.060000000000000005	"Con"	"Centrada"	0.19615372698289324
1422	P05.EP.VI.CE.0,07.Con.Centrada	P05	EP	VI	CE	0.07	"Con"	"Centrada"	0.1992419411505404
1423	P05.EP.VI.CE.0,08.Con.Centrada	P05	EP	VI	CE	0.08	"Con"	"Centrada"	0.20233015531818754
1424	P05.EP.VI.CE.0,09.Con.Centrada	P05	EP	VI	CE	0.09	"Con"	"Centrada"	0.2054183694858347
1425	P05.EP.VI.CE.0,1.Con.Centrada	P05	EP	VI	CE	0.09999999999999999	"Con"	"Centrada"	0.20850658365348185
1426	P05.EP.VI.CE.0,11.Con.Centrada	P05	EP	VI	CE	0.10999999999999999	"Con"	"Centrada"	0.211594797821129
1427	P05.EP.VI.CE.0,12.Con.Centrada	P05	EP	VI	CE	0.11999999999999998	"Con"	"Centrada"	0.21468301198877615
1428	P05.EP.VI.CE.0,13.Con.Centrada	P05	EP	VI	CE	0.12999999999999998	"Con"	"Centrada"	0.2177712261564233
1429	P05.EP.VI.CE.0,14.Con.Centrada	P05	EP	VI	CE	0.13999999999999999	"Con"	"Centrada"	0.22085944032407046
1430	P05.EP.VI.CE.0,15.Con.Centrada	P05	EP	VI	CE	0.15	"Con"	"Centrada"	0.2239476544917176
1431	P05.EP.VI.CE.0,16.Con.Centrada	P05	EP	VI	CE	0.16	"Con"	"Centrada"	0.22703586865936476
1432	P05.EP.VI.CE.0,17.Con.Centrada	P05	EP	VI	CE	0.17	"Con"	"Centrada"	0.2301240828270119
1433	P05.EP.VI.CE.0,18.Con.Centrada	P05	EP	VI	CE	0.18000000000000002	"Con"	"Centrada"	0.23321229699465906
1434	P05.EP.VI.CE.0,19.Con.Centrada	P05	EP	VI	CE	0.19000000000000003	"Con"	"Centrada"	0.23630051116230621
1435	P05.EP.VI.CE.0,2.Con.Centrada	P05	EP	VI	CE	0.20000000000000004	"Con"	"Centrada"	0.23938872532995337
1436	P05.EI.VI.CE.0,01.Con.Centrada	P05	EI	VI	CE	0.01	"Con"	"Centrada"	0.15136082674250773
1437	P05.EI.VI.CE.0,02.Con.Centrada	P05	EI	VI	CE	0.02	"Con"	"Centrada"	0.15595584868040635
1438	P05.EI.VI.CE.0,03.Con.Centrada	P05	EI	VI	CE	0.03	"Con"	"Centrada"	0.16055087061830497
1439	P05.EI.VI.CE.0,04.Con.Centrada	P05	EI	VI	CE	0.04	"Con"	"Centrada"	0.1651458925562036
1440	P05.EI.VI.CE.0,05.Con.Centrada	P05	EI	VI	CE	0.05	"Con"	"Centrada"	0.16974091449410222
1441	P05.EI.VI.CE.0,06.Con.Centrada	P05	EI	VI	CE	0.060000000000000005	"Con"	"Centrada"	0.17272306355300637
1442	P05.EI.VI.CE.0,07.Con.Centrada	P05	EI	VI	CE	0.07	"Con"	"Centrada"	0.17570521261191052
1443	P05.EI.VI.CE.0,08.Con.Centrada	P05	EI	VI	CE	0.08	"Con"	"Centrada"	0.17868736167081467
1444	P05.EI.VI.CE.0,09.Con.Centrada	P05	EI	VI	CE	0.09	"Con"	"Centrada"	0.18166951072971882
1445	P05.EI.VI.CE.0,1.Con.Centrada	P05	EI	VI	CE	0.09999999999999999	"Con"	"Centrada"	0.18465165978862297
1446	P05.EI.VI.CE.0,11.Con.Centrada	P05	EI	VI	CE	0.10999999999999999	"Con"	"Centrada"	0.18763380884752712
1447	P05.EI.VI.CE.0,12.Con.Centrada	P05	EI	VI	CE	0.11999999999999998	"Con"	"Centrada"	0.19061595790643127
1448	P05.EI.VI.CE.0,13.Con.Centrada	P05	EI	VI	CE	0.12999999999999998	"Con"	"Centrada"	0.19359810696533541
1449	P05.EI.VI.CE.0,14.Con.Centrada	P05	EI	VI	CE	0.13999999999999999	"Con"	"Centrada"	0.19658025602423956
1450	P05.EI.VI.CE.0,15.Con.Centrada	P05	EI	VI	CE	0.15	"Con"	"Centrada"	0.1995624050831437
1451	P05.EI.VI.CE.0,16.Con.Centrada	P05	EI	VI	CE	0.16	"Con"	"Centrada"	0.20254455414204786
1452	P05.EI.VI.CE.0,17.Con.Centrada	P05	EI	VI	CE	0.17	"Con"	"Centrada"	0.205526703200952
1453	P05.EI.VI.CE.0,18.Con.Centrada	P05	EI	VI	CE	0.18000000000000002	"Con"	"Centrada"	0.20850885225985616
1454	P05.EI.VI.CE.0,19.Con.Centrada	P05	EI	VI	CE	0.19000000000000003	"Con"	"Centrada"	0.2114910013187603
1455	P05.EI.VI.CE.0,2.Con.Centrada	P05	EI	VI	CE	0.20000000000000004	"Con"	"Centrada"	0.21447315037766446
1456	P05.EM.VI.CE.0,01.Con.Centrada	P05	EM	VI	CE	0.01	"Con"	"Centrada"	0.08452850168394654
1457	P05.EM.VI.CE.0,02.Con.Centrada	P05	EM	VI	CE	0.02	"Con"	"Centrada"	0.09138592029082471
1458	P05.EM.VI.CE.0,03.Con.Centrada	P05	EM	VI	CE	0.03	"Con"	"Centrada"	0.09824333889770287
1459	P05.EM.VI.CE.0,04.Con.Centrada	P05	EM	VI	CE	0.04	"Con"	"Centrada"	0.10510075750458103
1460	P05.EM.VI.CE.0,05.Con.Centrada	P05	EM	VI	CE	0.05	"Con"	"Centrada"	0.1119581761114592
1461	P05.EM.VI.CE.0,06.Con.Centrada	P05	EM	VI	CE	0.060000000000000005	"Con"	"Centrada"	0.11639266549887947
1462	P05.EM.VI.CE.0,07.Con.Centrada	P05	EM	VI	CE	0.07	"Con"	"Centrada"	0.12082715488629976
1463	P05.EM.VI.CE.0,08.Con.Centrada	P05	EM	VI	CE	0.08	"Con"	"Centrada"	0.12526164427372005
1464	P05.EM.VI.CE.0,09.Con.Centrada	P05	EM	VI	CE	0.09	"Con"	"Centrada"	0.12969613366114033
1465	P05.EM.VI.CE.0,1.Con.Centrada	P05	EM	VI	CE	0.09999999999999999	"Con"	"Centrada"	0.1341306230485606
1466	P05.EM.VI.CE.0,11.Con.Centrada	P05	EM	VI	CE	0.10999999999999999	"Con"	"Centrada"	0.13856511243598088
1467	P05.EM.VI.CE.0,12.Con.Centrada	P05	EM	VI	CE	0.11999999999999998	"Con"	"Centrada"	0.14299960182340116
1468	P05.EM.VI.CE.0,13.Con.Centrada	P05	EM	VI	CE	0.12999999999999998	"Con"	"Centrada"	0.14743409121082143
1469	P05.EM.VI.CE.0,14.Con.Centrada	P05	EM	VI	CE	0.13999999999999999	"Con"	"Centrada"	0.1518685805982417
1470	P05.EM.VI.CE.0,15.Con.Centrada	P05	EM	VI	CE	0.15	"Con"	"Centrada"	0.156303069985662
1471	P05.EM.VI.CE.0,16.Con.Centrada	P05	EM	VI	CE	0.16	"Con"	"Centrada"	0.16073755937308232
1472	P05.EM.VI.CE.0,17.Con.Centrada	P05	EM	VI	CE	0.17	"Con"	"Centrada"	0.16517204876050257
1473	P05.EM.VI.CE.0,18.Con.Centrada	P05	EM	VI	CE	0.18000000000000002	"Con"	"Centrada"	0.16960653814792287
1474	P05.EM.VI.CE.0,19.Con.Centrada	P05	EM	VI	CE	0.19000000000000003	"Con"	"Centrada"	0.17404102753534317
1475	P05.EM.VI.CE.0,2.Con.Centrada	P05	EM	VI	CE	0.20000000000000004	"Con"	"Centrada"	0.17847551692276342
1476	P05.EL.VI.IE.0,01.Con.Centrada	P05	EL	VI	CE	0.01	"Con"	"Centrada"	0.16866486912863632
1477	P05.EL.VI.CE.0,02.Con.Centrada	P05	EL	VI	CE	0.02	"Con"	"Centrada"	0.16651169091342244
1478	P05.EL.VI.CE.0,03.Con.Centrada	P05	EL	VI	CE	0.03	"Con"	"Centrada"	0.16435851269820856
1479	P05.EL.VI.CE.0,04.Con.Centrada	P05	EL	VI	CE	0.04	"Con"	"Centrada"	0.16220533448299468
1480	P05.EL.VI.IE.0,05.Con.Centrada	P05	EL	VI	CE	0.05	"Con"	"Centrada"	0.1600521562677808
1481	P05.EL.VI.CE.0,06.Con.Centrada	P05	EL	VI	CE	0.060000000000000005	"Con"	"Centrada"	0.16175933525332145
1482	P05.EL.VI.CE.0,07.Con.Centrada	P05	EL	VI	CE	0.07	"Con"	"Centrada"	0.1634665142388621
1483	P05.EL.VI.CE.0,08.Con.Centrada	P05	EL	VI	CE	0.08	"Con"	"Centrada"	0.16517369322440273
1484	P05.EL.VI.CE.0,09.Con.Centrada	P05	EL	VI	CE	0.09	"Con"	"Centrada"	0.16688087220994338
1485	P05.EL.VI.IE.0,1.Con.Centrada	P05	EL	VI	CE	0.09999999999999999	"Con"	"Centrada"	0.16858805119548403
1486	P05.EL.VI.CE.0,11.Con.Centrada	P05	EL	VI	CE	0.10999999999999999	"Con"	"Centrada"	0.1702952301810247
1487	P05.EL.VI.CE.0,12.Con.Centrada	P05	EL	VI	CE	0.11999999999999998	"Con"	"Centrada"	0.17200240916656534
1488	P05.EL.VI.CE.0,13.Con.Centrada	P05	EL	VI	CE	0.12999999999999998	"Con"	"Centrada"	0.17370958815210596
1489	P05.EL.VI.CE.0,14.Con.Centrada	P05	EL	VI	CE	0.13999999999999999	"Con"	"Centrada"	0.17541676713764662
1490	P05.EL.VI.CE.0,15.Con.Centrada	P05	EL	VI	CE	0.15	"Con"	"Centrada"	0.17712394612318727
1491	P05.EL.VI.CE.0,16.Con.Centrada	P05	EL	VI	CE	0.16	"Con"	"Centrada"	0.17883112510872792
1492	P05.EL.VI.CE.0,17.Con.Centrada	P05	EL	VI	CE	0.17	"Con"	"Centrada"	0.18053830409426858
1493	P05.EL.VI.CE.0,18.Con.Centrada	P05	EL	VI	CE	0.18000000000000002	"Con"	"Centrada"	0.1822454830798092
1494	P05.EL.VI.CE.0,19.Con.Centrada	P05	EL	VI	CE	0.19000000000000003	"Con"	"Centrada"	0.18395266206534988
1495	P05.EL.VI.CE.0,2.Con.Centrada	P05	EL	VI	CE	0.20000000000000004	"Con"	"Centrada"	0.1856598410508905
1496	P05.EP.VI.SA.0.Sin.Exterior	P05	EP	VI	SA	0	"Sin"	"Exterior"	0.3608219816127569
1497	P05.EI.VI.SA.0.Sin.Exterior	P05	EI	VI	SA	0	"Sin"	"Exterior"	0.23030789438966615
1498	P05.EM.VI.SA.0.Sin.Exterior	P05	EM	VI	SA	0	"Sin"	"Exterior"	0.08885241550777323
1499	P05.EL.VI.SA.0.Sin.Exterior	P05	EL	VI	SA	0	"Sin"	"Exterior"	0.11123328711155
1500	P05.EP.VI.CI.0,01.Sin.Exterior	P05	EP	VI	CI	0.01	"Sin"	"Exterior"	0.5264984561367783
1501	P05.EP.VI.CI.0,02.Sin.Exterior	P05	EP	VI	CI	0.02	"Sin"	"Exterior"	0.5758794886505152
1502	P05.EP.VI.CI.0,03.Sin.Exterior	P05	EP	VI	CI	0.03	"Sin"	"Exterior"	0.6252605211642521
1503	P05.EP.VI.CI.0,04.Sin.Exterior	P05	EP	VI	CI	0.04	"Sin"	"Exterior"	0.6934725036812064
1504	P05.EP.VI.CI.0,05.Sin.Exterior	P05	EP	VI	CI	0.05	"Sin"	"Exterior"	0.7616844861981606
1505	P05.EP.VI.CI.0,06.Sin.Exterior	P05	EP	VI	CI	0.060000000000000005	"Sin"	"Exterior"	0.8298964687151149
1506	P05.EP.VI.CI.0,07.Sin.Exterior	P05	EP	VI	CI	0.07	"Sin"	"Exterior"	0.8981084512320692
1507	P05.EP.VI.CI.0,08.Sin.Exterior	P05	EP	VI	CI	0.08	"Sin"	"Exterior"	0.8981084512320692
1508	P05.EP.VI.CI.0,09.Sin.Exterior	P05	EP	VI	CI	0.09	"Sin"	"Exterior"	0.8981084512320692
1509	P05.EP.VI.CI.0,1.Sin.Exterior	P05	EP	VI	CI	0.09999999999999999	"Sin"	"Exterior"	0.8981084512320692
1510	P05.EP.VI.CI.0,11.Sin.Exterior	P05	EP	VI	CI	0.10999999999999999	"Sin"	"Exterior"	0.8981084512320692
1511	P05.EP.VI.CI.0,12.Sin.Exterior	P05	EP	VI	CI	0.11999999999999998	"Sin"	"Exterior"	0.8981084512320692
1512	P05.EP.VI.CI.0,13.Sin.Exterior	P05	EP	VI	CI	0.12999999999999998	"Sin"	"Exterior"	0.8981084512320692
1513	P05.EP.VI.CI.0,14.Sin.Exterior	P05	EP	VI	CI	0.13999999999999999	"Sin"	"Exterior"	0.8981084512320692
1514	P05.EP.VI.CI.0,15.Sin.Exterior	P05	EP	VI	CI	0.15	"Sin"	"Exterior"	0.8981084512320692
1515	P05.EP.VI.CI.0,16.Sin.Exterior	P05	EP	VI	CI	0.16	"Sin"	"Exterior"	0.8981084512320692
1516	P05.EP.VI.CI.0,17.Sin.Exterior	P05	EP	VI	CI	0.17	"Sin"	"Exterior"	0.8981084512320692
1517	P05.EP.VI.CI.0,18.Sin.Exterior	P05	EP	VI	CI	0.18000000000000002	"Sin"	"Exterior"	0.8981084512320692
1518	P05.EP.VI.CI.0,19.Sin.Exterior	P05	EP	VI	CI	0.19000000000000003	"Sin"	"Exterior"	0.8981084512320692
1519	P05.EP.VI.CI.0,2.Sin.Exterior	P05	EP	VI	CI	0.20000000000000004	"Sin"	"Exterior"	0.8981084512320692
1520	P05.EI.VI.CI.0,01.Sin.Exterior	P05	EI	VI	CI	0.01	"Sin"	"Exterior"	0.3231042037810372
1521	P05.EI.VI.CI.0,02.Sin.Exterior	P05	EI	VI	CI	0.02	"Sin"	"Exterior"	0.3596219662135345
1522	P05.EI.VI.CI.0,03.Sin.Exterior	P05	EI	VI	CI	0.03	"Sin"	"Exterior"	0.39613972864603175
1523	P05.EI.VI.CI.0,04.Sin.Exterior	P05	EI	VI	CI	0.04	"Sin"	"Exterior"	0.46267382981634864
1524	P05.EI.VI.CI.0,05.Sin.Exterior	P05	EI	VI	CI	0.05	"Sin"	"Exterior"	0.5292079309866655
1525	P05.EI.VI.CI.0,06.Sin.Exterior	P05	EI	VI	CI	0.060000000000000005	"Sin"	"Exterior"	0.5957420321569824
1526	P05.EI.VI.CI.0,07.Sin.Exterior	P05	EI	VI	CI	0.07	"Sin"	"Exterior"	0.6622761333272993
1527	P05.EI.VI.CI.0,08.Sin.Exterior	P05	EI	VI	CI	0.08	"Sin"	"Exterior"	0.6622761333272993
1528	P05.EI.VI.CI.0,09.Sin.Exterior	P05	EI	VI	CI	0.09	"Sin"	"Exterior"	0.6622761333272993
1529	P05.EI.VI.CI.0,1.Sin.Exterior	P05	EI	VI	CI	0.09999999999999999	"Sin"	"Exterior"	0.6622761333272993
1530	P05.EI.VI.CI.0,11.Sin.Exterior	P05	EI	VI	CI	0.10999999999999999	"Sin"	"Exterior"	0.6622761333272993
1531	P05.EI.VI.CI.0,12.Sin.Exterior	P05	EI	VI	CI	0.11999999999999998	"Sin"	"Exterior"	0.6622761333272993
1532	P05.EI.VI.CI.0,13.Sin.Exterior	P05	EI	VI	CI	0.12999999999999998	"Sin"	"Exterior"	0.6622761333272993
1533	P05.EI.VI.CI.0,14.Sin.Exterior	P05	EI	VI	CI	0.13999999999999999	"Sin"	"Exterior"	0.6622761333272993
1534	P05.EI.VI.CI.0,15.Sin.Exterior	P05	EI	VI	CI	0.15	"Sin"	"Exterior"	0.6622761333272993
1535	P05.EI.VI.CI.0,16.Sin.Exterior	P05	EI	VI	CI	0.16	"Sin"	"Exterior"	0.6622761333272993
1536	P05.EI.VI.CI.0,17.Sin.Exterior	P05	EI	VI	CI	0.17	"Sin"	"Exterior"	0.6622761333272993
1537	P05.EI.VI.CI.0,18.Sin.Exterior	P05	EI	VI	CI	0.18000000000000002	"Sin"	"Exterior"	0.6622761333272993
1538	P05.EI.VI.CI.0,19.Sin.Exterior	P05	EI	VI	CI	0.19000000000000003	"Sin"	"Exterior"	0.6622761333272993
1539	P05.EI.VI.CI.0,2.Sin.Exterior	P05	EI	VI	CI	0.20000000000000004	"Sin"	"Exterior"	0.6622761333272993
1540	P05.EM.VI.CI.0,01.Sin.Exterior	P05	EM	VI	CI	0.01	"Sin"	"Exterior"	0.10372399982020086
1541	P05.EM.VI.CI.0,02.Sin.Exterior	P05	EM	VI	CI	0.02	"Sin"	"Exterior"	0.11361253806243554
1542	P05.EM.VI.CI.0,03.Sin.Exterior	P05	EM	VI	CI	0.03	"Sin"	"Exterior"	0.12350107630467022
1543	P05.EM.VI.CI.0,04.Sin.Exterior	P05	EM	VI	CI	0.04	"Sin"	"Exterior"	0.150445674676833
1544	P05.EM.VI.CI.0,05.Sin.Exterior	P05	EM	VI	CI	0.05	"Sin"	"Exterior"	0.1773902730489958
1545	P05.EM.VI.CI.0,06.Sin.Exterior	P05	EM	VI	CI	0.060000000000000005	"Sin"	"Exterior"	0.20433487142115858
1546	P05.EM.VI.CI.0,07.Sin.Exterior	P05	EM	VI	CI	0.07	"Sin"	"Exterior"	0.23127946979332137
1547	P05.EM.VI.CI.0,08.Sin.Exterior	P05	EM	VI	CI	0.08	"Sin"	"Exterior"	0.23127946979332137
1548	P05.EM.VI.CI.0,09.Sin.Exterior	P05	EM	VI	CI	0.09	"Sin"	"Exterior"	0.23127946979332137
1549	P05.EM.VI.CI.0,1.Sin.Exterior	P05	EM	VI	CI	0.09999999999999999	"Sin"	"Exterior"	0.23127946979332137
1550	P05.EM.VI.CI.0,11.Sin.Exterior	P05	EM	VI	CI	0.10999999999999999	"Sin"	"Exterior"	0.23127946979332137
1551	P05.EM.VI.CI.0,12.Sin.Exterior	P05	EM	VI	CI	0.11999999999999998	"Sin"	"Exterior"	0.23127946979332137
1552	P05.EM.VI.CI.0,13.Sin.Exterior	P05	EM	VI	CI	0.12999999999999998	"Sin"	"Exterior"	0.23127946979332137
1553	P05.EM.VI.CI.0,14.Sin.Exterior	P05	EM	VI	CI	0.13999999999999999	"Sin"	"Exterior"	0.23127946979332137
1554	P05.EM.VI.CI.0,15.Sin.Exterior	P05	EM	VI	CI	0.15	"Sin"	"Exterior"	0.23127946979332137
1555	P05.EM.VI.CI.0,16.Sin.Exterior	P05	EM	VI	CI	0.16	"Sin"	"Exterior"	0.23127946979332137
1556	P05.EM.VI.CI.0,17.Sin.Exterior	P05	EM	VI	CI	0.17	"Sin"	"Exterior"	0.23127946979332137
1557	P05.EM.VI.CI.0,18.Sin.Exterior	P05	EM	VI	CI	0.18000000000000002	"Sin"	"Exterior"	0.23127946979332137
1558	P05.EM.VI.CI.0,19.Sin.Exterior	P05	EM	VI	CI	0.19000000000000003	"Sin"	"Exterior"	0.23127946979332137
1559	P05.EM.VI.CI.0,2.Sin.Exterior	P05	EM	VI	CI	0.20000000000000004	"Sin"	"Exterior"	0.23127946979332137
1560	P05.EP.VI.CE.0,01.Sin.Exterior	P05	EP	VI	CE	0.01	"Sin"	"Exterior"	0.20322970613677782
1561	P05.EP.VI.CE.0,02.Sin.Exterior	P05	EP	VI	CE	0.02	"Sin"	"Exterior"	0.20045864769022015
1562	P05.EP.VI.CE.0,03.Sin.Exterior	P05	EP	VI	CE	0.03	"Sin"	"Exterior"	0.19768758924366248
1563	P05.EP.VI.CE.0,04.Sin.Exterior	P05	EP	VI	CE	0.04	"Sin"	"Exterior"	0.1949165307971048
1564	P05.EP.VI.CE.0,05.Sin.Exterior	P05	EP	VI	CE	0.05	"Sin"	"Exterior"	0.19214547235054713
1565	P05.EP.VI.CE.0,06.Sin.Exterior	P05	EP	VI	CE	0.060000000000000005	"Sin"	"Exterior"	0.197353378616679
1566	P05.EP.VI.CE.0,07.Sin.Exterior	P05	EP	VI	CE	0.07	"Sin"	"Exterior"	0.2025612848828109
1567	P05.EP.VI.CE.0,08.Sin.Exterior	P05	EP	VI	CE	0.08	"Sin"	"Exterior"	0.20776919114894277
1568	P05.EP.VI.CE.0,09.Sin.Exterior	P05	EP	VI	CE	0.09	"Sin"	"Exterior"	0.21297709741507465
1569	P05.EP.VI.CE.0,1.Sin.Exterior	P05	EP	VI	CE	0.09999999999999999	"Sin"	"Exterior"	0.21818500368120652
1570	P05.EP.VI.CE.0,11.Sin.Exterior	P05	EP	VI	CE	0.10999999999999999	"Sin"	"Exterior"	0.2233929099473384
1571	P05.EP.VI.CE.0,12.Sin.Exterior	P05	EP	VI	CE	0.11999999999999998	"Sin"	"Exterior"	0.22860081621347028
1572	P05.EP.VI.CE.0,13.Sin.Exterior	P05	EP	VI	CE	0.12999999999999998	"Sin"	"Exterior"	0.23380872247960216
1573	P05.EP.VI.CE.0,14.Sin.Exterior	P05	EP	VI	CE	0.13999999999999999	"Sin"	"Exterior"	0.23901662874573404
1574	P05.EP.VI.CE.0,15.Sin.Exterior	P05	EP	VI	CE	0.15	"Sin"	"Exterior"	0.24422453501186592
1575	P05.EP.VI.CE.0,16.Sin.Exterior	P05	EP	VI	CE	0.16	"Sin"	"Exterior"	0.2494324412779978
1576	P05.EP.VI.CE.0,17.Sin.Exterior	P05	EP	VI	CE	0.17	"Sin"	"Exterior"	0.2546403475441297
1577	P05.EP.VI.CE.0,18.Sin.Exterior	P05	EP	VI	CE	0.18000000000000002	"Sin"	"Exterior"	0.25984825381026155
1578	P05.EP.VI.CE.0,19.Sin.Exterior	P05	EP	VI	CE	0.19000000000000003	"Sin"	"Exterior"	0.26505616007639343
1579	P05.EP.VI.CE.0,2.Sin.Exterior	P05	EP	VI	CE	0.20000000000000004	"Sin"	"Exterior"	0.2702640663425253
1580	P05.EI.VI.CE.0,01.Sin.Exterior	P05	EI	VI	CE	0.01	"Sin"	"Exterior"	0.14754170378103737
1581	P05.EI.VI.CE.0,02.Sin.Exterior	P05	EI	VI	CE	0.02	"Sin"	"Exterior"	0.14690069549925344
1582	P05.EI.VI.CE.0,03.Sin.Exterior	P05	EI	VI	CE	0.03	"Sin"	"Exterior"	0.14625968721746951
1583	P05.EI.VI.CE.0,04.Sin.Exterior	P05	EI	VI	CE	0.04	"Sin"	"Exterior"	0.14561867893568559
1584	P05.EI.VI.CE.0,05.Sin.Exterior	P05	EI	VI	CE	0.05	"Sin"	"Exterior"	0.14497767065390166
1585	P05.EI.VI.CE.0,06.Sin.Exterior	P05	EI	VI	CE	0.060000000000000005	"Sin"	"Exterior"	0.14750440248639105
1586	P05.EI.VI.CE.0,07.Sin.Exterior	P05	EI	VI	CE	0.07	"Sin"	"Exterior"	0.15003113431888043
1587	P05.EI.VI.CE.0,08.Sin.Exterior	P05	EI	VI	CE	0.08	"Sin"	"Exterior"	0.15255786615136985
1588	P05.EI.VI.CE.0,09.Sin.Exterior	P05	EI	VI	CE	0.09	"Sin"	"Exterior"	0.15508459798385923
1589	P05.EI.VI.CE.0,1.Sin.Exterior	P05	EI	VI	CE	0.09999999999999999	"Sin"	"Exterior"	0.15761132981634862
1590	P05.EI.VI.CE.0,11.Sin.Exterior	P05	EI	VI	CE	0.10999999999999999	"Sin"	"Exterior"	0.160138061648838
1591	P05.EI.VI.CE.0,12.Sin.Exterior	P05	EI	VI	CE	0.11999999999999998	"Sin"	"Exterior"	0.1626647934813274
1592	P05.EI.VI.CE.0,13.Sin.Exterior	P05	EI	VI	CE	0.12999999999999998	"Sin"	"Exterior"	0.1651915253138168
1593	P05.EI.VI.CE.0,14.Sin.Exterior	P05	EI	VI	CE	0.13999999999999999	"Sin"	"Exterior"	0.1677182571463062
1594	P05.EI.VI.CE.0,15.Sin.Exterior	P05	EI	VI	CE	0.15	"Sin"	"Exterior"	0.17024498897879559
1595	P05.EI.VI.CE.0,16.Sin.Exterior	P05	EI	VI	CE	0.16	"Sin"	"Exterior"	0.17277172081128497
1596	P05.EI.VI.CE.0,17.Sin.Exterior	P05	EI	VI	CE	0.17	"Sin"	"Exterior"	0.17529845264377436
1597	P05.EI.VI.CE.0,18.Sin.Exterior	P05	EI	VI	CE	0.18000000000000002	"Sin"	"Exterior"	0.17782518447626378
1598	P05.EI.VI.CE.0,19.Sin.Exterior	P05	EI	VI	CE	0.19000000000000003	"Sin"	"Exterior"	0.18035191630875316
1599	P05.EI.VI.CE.0,2.Sin.Exterior	P05	EI	VI	CE	0.20000000000000004	"Sin"	"Exterior"	0.18287864814124255
1600	P05.EM.VI.CE.0,01.Sin.Exterior	P05	EM	VI	CE	0.01	"Sin"	"Exterior"	0.07602399982020103
1601	P05.EM.VI.CE.0,02.Sin.Exterior	P05	EM	VI	CE	0.02	"Sin"	"Exterior"	0.0747838668659847
1602	P05.EM.VI.CE.0,03.Sin.Exterior	P05	EM	VI	CE	0.03	"Sin"	"Exterior"	0.07354373391176838
1603	P05.EM.VI.CE.0,04.Sin.Exterior	P05	EM	VI	CE	0.04	"Sin"	"Exterior"	0.07230360095755206
1604	P05.EM.VI.CE.0,05.Sin.Exterior	P05	EM	VI	CE	0.05	"Sin"	"Exterior"	0.07106346800333574
1605	P05.EM.VI.CE.0,06.Sin.Exterior	P05	EM	VI	CE	0.060000000000000005	"Sin"	"Exterior"	0.0744799093380352
1606	P05.EM.VI.CE.0,07.Sin.Exterior	P05	EM	VI	CE	0.07	"Sin"	"Exterior"	0.07789635067273463
1607	P05.EM.VI.CE.0,08.Sin.Exterior	P05	EM	VI	CE	0.08	"Sin"	"Exterior"	0.08131279200743409
1608	P05.EM.VI.CE.0,09.Sin.Exterior	P05	EM	VI	CE	0.09	"Sin"	"Exterior"	0.08472923334213353
1609	P05.EM.VI.CE.0,1.Sin.Exterior	P05	EM	VI	CE	0.09999999999999999	"Sin"	"Exterior"	0.08814567467683299
1610	P05.EM.VI.CE.0,11.Sin.Exterior	P05	EM	VI	CE	0.10999999999999999	"Sin"	"Exterior"	0.09156211601153244
1611	P05.EM.VI.CE.0,12.Sin.Exterior	P05	EM	VI	CE	0.11999999999999998	"Sin"	"Exterior"	0.09497855734623187
1612	P05.EM.VI.CE.0,13.Sin.Exterior	P05	EM	VI	CE	0.12999999999999998	"Sin"	"Exterior"	0.09839499868093132
1613	P05.EM.VI.CE.0,14.Sin.Exterior	P05	EM	VI	CE	0.13999999999999999	"Sin"	"Exterior"	0.10181144001563078
1614	P05.EM.VI.CE.0,15.Sin.Exterior	P05	EM	VI	CE	0.15	"Sin"	"Exterior"	0.10522788135033023
1615	P05.EM.VI.CE.0,16.Sin.Exterior	P05	EM	VI	CE	0.16	"Sin"	"Exterior"	0.10864432268502969
1616	P05.EM.VI.CE.0,17.Sin.Exterior	P05	EM	VI	CE	0.17	"Sin"	"Exterior"	0.11206076401972914
1617	P05.EM.VI.CE.0,18.Sin.Exterior	P05	EM	VI	CE	0.18000000000000002	"Sin"	"Exterior"	0.1154772053544286
1618	P05.EM.VI.CE.0,19.Sin.Exterior	P05	EM	VI	CE	0.19000000000000003	"Sin"	"Exterior"	0.11889364668912804
1619	P05.EM.VI.CE.0,2.Sin.Exterior	P05	EM	VI	CE	0.20000000000000004	"Sin"	"Exterior"	0.12231008802382749
1620	P05.EP.VI.CI.0,01.Con.Exterior	P05	EP	VI	CI	0.01	"Con"	"Exterior"	0.2735181931126691
1621	P05.EP.VI.CI.0,02.Con.Exterior	P05	EP	VI	CI	0.02	"Con"	"Exterior"	0.23938880765465576
1622	P05.EP.VI.CI.0,03.Con.Exterior	P05	EP	VI	CI	0.03	"Con"	"Exterior"	0.2052594221966424
1623	P05.EP.VI.CI.0,04.Con.Exterior	P05	EP	VI	CI	0.04	"Con"	"Exterior"	0.2273640541828459
1624	P05.EP.VI.CI.0,05.Con.Exterior	P05	EP	VI	CI	0.05	"Con"	"Exterior"	0.24946868616904938
1625	P05.EP.VI.CI.0,06.Con.Exterior	P05	EP	VI	CI	0.060000000000000005	"Con"	"Exterior"	0.2715733181552529
1626	P05.EP.VI.CI.0,07.Con.Exterior	P05	EP	VI	CI	0.07	"Con"	"Exterior"	0.29367795014145637
1627	P05.EP.VI.CI.0,08.Con.Exterior	P05	EP	VI	CI	0.08	"Con"	"Exterior"	0.29367795014145637
1628	P05.EP.VI.CI.0,09.Con.Exterior	P05	EP	VI	CI	0.09	"Con"	"Exterior"	0.29367795014145637
1629	P05.EP.VI.CI.0,1.Con.Exterior	P05	EP	VI	CI	0.09999999999999999	"Con"	"Exterior"	0.29367795014145637
1630	P05.EP.VI.CI.0,11.Con.Exterior	P05	EP	VI	CI	0.10999999999999999	"Con"	"Exterior"	0.29367795014145637
1631	P05.EP.VI.CI.0,12.Con.Exterior	P05	EP	VI	CI	0.11999999999999998	"Con"	"Exterior"	0.29367795014145637
1632	P05.EP.VI.CI.0,13.Con.Exterior	P05	EP	VI	CI	0.12999999999999998	"Con"	"Exterior"	0.29367795014145637
1633	P05.EP.VI.CI.0,14.Con.Exterior	P05	EP	VI	CI	0.13999999999999999	"Con"	"Exterior"	0.29367795014145637
1634	P05.EP.VI.CI.0,15.Con.Exterior	P05	EP	VI	CI	0.15	"Con"	"Exterior"	0.29367795014145637
1635	P05.EP.VI.CI.0,16.Con.Exterior	P05	EP	VI	CI	0.16	"Con"	"Exterior"	0.29367795014145637
1636	P05.EP.VI.CI.0,17.Con.Exterior	P05	EP	VI	CI	0.17	"Con"	"Exterior"	0.29367795014145637
1637	P05.EP.VI.CI.0,18.Con.Exterior	P05	EP	VI	CI	0.18000000000000002	"Con"	"Exterior"	0.29367795014145637
1638	P05.EP.VI.CI.0,19.Con.Exterior	P05	EP	VI	CI	0.19000000000000003	"Con"	"Exterior"	0.29367795014145637
1639	P05.EP.VI.CI.0,2.Con.Exterior	P05	EP	VI	CI	0.20000000000000004	"Con"	"Exterior"	0.29367795014145637
1640	P05.EI.VI.CI.0,01.Con.Exterior	P05	EI	VI	CI	0.01	"Con"	"Exterior"	0.19704269075692782
1641	P05.EI.VI.CI.0,02.Con.Exterior	P05	EI	VI	CI	0.02	"Con"	"Exterior"	0.18513441021767485
1642	P05.EI.VI.CI.0,03.Con.Exterior	P05	EI	VI	CI	0.03	"Con"	"Exterior"	0.17322612967842188
1643	P05.EI.VI.CI.0,04.Con.Exterior	P05	EI	VI	CI	0.04	"Con"	"Exterior"	0.20000288031798696
1644	P05.EI.VI.CI.0,05.Con.Exterior	P05	EI	VI	CI	0.05	"Con"	"Exterior"	0.22677963095755205
1645	P05.EI.VI.CI.0,06.Con.Exterior	P05	EI	VI	CI	0.060000000000000005	"Con"	"Exterior"	0.25355638159711713
1646	P05.EI.VI.CI.0,07.Con.Exterior	P05	EI	VI	CI	0.07	"Con"	"Exterior"	0.2803331322366822
1647	P05.EI.VI.CI.0,08.Con.Exterior	P05	EI	VI	CI	0.08	"Con"	"Exterior"	0.2803331322366822
1648	P05.EI.VI.CI.0,09.Con.Exterior	P05	EI	VI	CI	0.09	"Con"	"Exterior"	0.2803331322366822
1649	P05.EI.VI.CI.0,1.Con.Exterior	P05	EI	VI	CI	0.09999999999999999	"Con"	"Exterior"	0.2803331322366822
1650	P05.EI.VI.CI.0,11.Con.Exterior	P05	EI	VI	CI	0.10999999999999999	"Con"	"Exterior"	0.2803331322366822
1651	P05.EI.VI.CI.0,12.Con.Exterior	P05	EI	VI	CI	0.11999999999999998	"Con"	"Exterior"	0.2803331322366822
1652	P05.EI.VI.CI.0,13.Con.Exterior	P05	EI	VI	CI	0.12999999999999998	"Con"	"Exterior"	0.2803331322366822
1653	P05.EI.VI.CI.0,14.Con.Exterior	P05	EI	VI	CI	0.13999999999999999	"Con"	"Exterior"	0.2803331322366822
1654	P05.EI.VI.CI.0,15.Con.Exterior	P05	EI	VI	CI	0.15	"Con"	"Exterior"	0.2803331322366822
1655	P05.EI.VI.CI.0,16.Con.Exterior	P05	EI	VI	CI	0.16	"Con"	"Exterior"	0.2803331322366822
1656	P05.EI.VI.CI.0,17.Con.Exterior	P05	EI	VI	CI	0.17	"Con"	"Exterior"	0.2803331322366822
1657	P05.EI.VI.CI.0,18.Con.Exterior	P05	EI	VI	CI	0.18000000000000002	"Con"	"Exterior"	0.2803331322366822
1658	P05.EI.VI.CI.0,19.Con.Exterior	P05	EI	VI	CI	0.19000000000000003	"Con"	"Exterior"	0.2803331322366822
1659	P05.EI.VI.CI.0,2.Con.Exterior	P05	EI	VI	CI	0.20000000000000004	"Con"	"Exterior"	0.2803331322366822
1660	P05.EM.VI.CI.0,01.Con.Exterior	P05	EM	VI	CI	0.01	"Con"	"Exterior"	0.09653228788431267
1661	P05.EM.VI.CI.0,02.Con.Exterior	P05	EM	VI	CI	0.02	"Con"	"Exterior"	0.10103539323519195
1662	P05.EM.VI.CI.0,03.Con.Exterior	P05	EM	VI	CI	0.03	"Con"	"Exterior"	0.10553849858607123
1663	P05.EM.VI.CI.0,04.Con.Exterior	P05	EM	VI	CI	0.04	"Con"	"Exterior"	0.11994534134317014
1664	P05.EM.VI.CI.0,05.Con.Exterior	P05	EM	VI	CI	0.05	"Con"	"Exterior"	0.13435218410026906
1665	P05.EM.VI.CI.0,06.Con.Exterior	P05	EM	VI	CI	0.060000000000000005	"Con"	"Exterior"	0.14875902685736797
1666	P05.EM.VI.CI.0,07.Con.Exterior	P05	EM	VI	CI	0.07	"Con"	"Exterior"	0.16316586961446689
1667	P05.EM.VI.CI.0,08.Con.Exterior	P05	EM	VI	CI	0.08	"Con"	"Exterior"	0.16316586961446689
1668	P05.EM.VI.CI.0,09.Con.Exterior	P05	EM	VI	CI	0.09	"Con"	"Exterior"	0.16316586961446689
1669	P05.EM.VI.CI.0,1.Con.Exterior	P05	EM	VI	CI	0.09999999999999999	"Con"	"Exterior"	0.16316586961446689
1670	P05.EM.VI.CI.0,11.Con.Exterior	P05	EM	VI	CI	0.10999999999999999	"Con"	"Exterior"	0.16316586961446689
1671	P05.EM.VI.CI.0,12.Con.Exterior	P05	EM	VI	CI	0.11999999999999998	"Con"	"Exterior"	0.16316586961446689
1672	P05.EM.VI.CI.0,13.Con.Exterior	P05	EM	VI	CI	0.12999999999999998	"Con"	"Exterior"	0.16316586961446689
1673	P05.EM.VI.CI.0,14.Con.Exterior	P05	EM	VI	CI	0.13999999999999999	"Con"	"Exterior"	0.16316586961446689
1674	P05.EM.VI.CI.0,15.Con.Exterior	P05	EM	VI	CI	0.15	"Con"	"Exterior"	0.16316586961446689
1675	P05.EM.VI.CI.0,16.Con.Exterior	P05	EM	VI	CI	0.16	"Con"	"Exterior"	0.16316586961446689
1676	P05.EM.VI.CI.0,17.Con.Exterior	P05	EM	VI	CI	0.17	"Con"	"Exterior"	0.16316586961446689
1677	P05.EM.VI.CI.0,18.Con.Exterior	P05	EM	VI	CI	0.18000000000000002	"Con"	"Exterior"	0.16316586961446689
1678	P05.EM.VI.CI.0,19.Con.Exterior	P05	EM	VI	CI	0.19000000000000003	"Con"	"Exterior"	0.16316586961446689
1679	P05.EM.VI.CI.0,2.Con.Exterior	P05	EM	VI	CI	0.20000000000000004	"Con"	"Exterior"	0.16316586961446689
1680	P05.EL.VI.IE.0,01.Con.Exterior	P05	EL	VI	CI	0.01	"Con"	"Exterior"	0.2024936553290022
1681	P05.EL.VI.CI.0,02.Con.Exterior	P05	EL	VI	CI	0.02	"Con"	"Exterior"	0.20303287068289078
1682	P05.EL.VI.IE.0,03.Con.Exterior	P05	EL	VI	CI	0.03	"Con"	"Exterior"	0.20357208603677934
1683	P05.EL.VI.CI.0,04.Con.Exterior	P05	EL	VI	CI	0.04	"Con"	"Exterior"	0.18812151949009293
1684	P05.EL.VI.CI.0,05.Con.Exterior	P05	EL	VI	CI	0.05	"Con"	"Exterior"	0.1726709529434065
1685	P05.EL.VI.CI.0,06.Con.Exterior	P05	EL	VI	CI	0.060000000000000005	"Con"	"Exterior"	0.1572203863967201
1686	P05.EL.VI.CI.0,07.Con.Exterior	P05	EL	VI	CI	0.07	"Con"	"Exterior"	0.14176981985003367
1687	P05.EL.VI.CI.0,08.Con.Exterior	P05	EL	VI	CI	0.08	"Con"	"Exterior"	0.14176981985003367
1688	P05.EL.VI.CI.0,09.Con.Exterior	P05	EL	VI	CI	0.09	"Con"	"Exterior"	0.14176981985003367
1689	P05.EL.VI.IE.0,1.Con.Exterior	P05	EL	VI	CI	0.09999999999999999	"Con"	"Exterior"	0.14176981985003367
1690	P05.EL.VI.CI.0,11.Con.Exterior	P05	EL	VI	CI	0.10999999999999999	"Con"	"Exterior"	0.14176981985003367
1691	P05.EL.VI.CI.0,12.Con.Exterior	P05	EL	VI	CI	0.11999999999999998	"Con"	"Exterior"	0.14176981985003367
1692	P05.EL.VI.CI.0,13.Con.Exterior	P05	EL	VI	CI	0.12999999999999998	"Con"	"Exterior"	0.14176981985003367
1693	P05.EL.VI.CI.0,14.Con.Exterior	P05	EL	VI	CI	0.13999999999999999	"Con"	"Exterior"	0.14176981985003367
1694	P05.EL.VI.CI.0,15.Con.Exterior	P05	EL	VI	CI	0.15	"Con"	"Exterior"	0.14176981985003367
1695	P05.EL.VI.CI.0,16.Con.Exterior	P05	EL	VI	CI	0.16	"Con"	"Exterior"	0.14176981985003367
1696	P05.EL.VI.CI.0,17.Con.Exterior	P05	EL	VI	CI	0.17	"Con"	"Exterior"	0.14176981985003367
1697	P05.EL.VI.CI.0,18.Con.Exterior	P05	EL	VI	CI	0.18000000000000002	"Con"	"Exterior"	0.14176981985003367
1698	P05.EL.VI.CI.0,19.Con.Exterior	P05	EL	VI	CI	0.19000000000000003	"Con"	"Exterior"	0.14176981985003367
1699	P05.EL.VI.CI.0,2.Con.Exterior	P05	EL	VI	CI	0.20000000000000004	"Con"	"Exterior"	0.14176981985003367
1700	P05.EP.VI.CI.0,01.Con.Interior	P05	EP	VI	CI	0.01	"Con"	"Interior"	0.11963595613677835
1701	P05.EP.VI.CI.0,02.Con.Interior	P05	EP	VI	CI	0.02	"Con"	"Interior"	0.11755761365051542
1702	P05.EP.VI.CI.0,03.Con.Interior	P05	EP	VI	CI	0.03	"Con"	"Interior"	0.1154792711642525
1703	P05.EP.VI.CI.0,04.Con.Interior	P05	EP	VI	CI	0.04	"Con"	"Interior"	0.13461625368120655
1704	P05.EP.VI.CI.0,05.Con.Interior	P05	EP	VI	CI	0.05	"Con"	"Interior"	0.15375323619816061
1705	P05.EP.VI.CI.0,06.Con.Interior	P05	EP	VI	CI	0.060000000000000005	"Con"	"Interior"	0.17289021871511467
1706	P05.EP.VI.CI.0,07.Con.Interior	P05	EP	VI	CI	0.07	"Con"	"Interior"	0.19202720123206873
1707	P05.EP.VI.CI.0,08.Con.Interior	P05	EP	VI	CI	0.08	"Con"	"Interior"	0.19202720123206873
1708	P05.EP.VI.CI.0,09.Con.Interior	P05	EP	VI	CI	0.09	"Con"	"Interior"	0.19202720123206873
1709	P05.EP.VI.CI.0,1.Con.Interior	P05	EP	VI	CI	0.09999999999999999	"Con"	"Interior"	0.19202720123206873
1710	P05.EP.VI.CI.0,11.Con.Interior	P05	EP	VI	CI	0.10999999999999999	"Con"	"Interior"	0.19202720123206873
1711	P05.EP.VI.CI.0,12.Con.Interior	P05	EP	VI	CI	0.11999999999999998	"Con"	"Interior"	0.19202720123206873
1712	P05.EP.VI.CI.0,13.Con.Interior	P05	EP	VI	CI	0.12999999999999998	"Con"	"Interior"	0.19202720123206873
1713	P05.EP.VI.CI.0,14.Con.Interior	P05	EP	VI	CI	0.13999999999999999	"Con"	"Interior"	0.19202720123206873
1714	P05.EP.VI.CI.0,15.Con.Interior	P05	EP	VI	CI	0.15	"Con"	"Interior"	0.19202720123206873
1715	P05.EP.VI.CI.0,16.Con.Interior	P05	EP	VI	CI	0.16	"Con"	"Interior"	0.19202720123206873
1716	P05.EP.VI.CI.0,17.Con.Interior	P05	EP	VI	CI	0.17	"Con"	"Interior"	0.19202720123206873
1717	P05.EP.VI.CI.0,18.Con.Interior	P05	EP	VI	CI	0.18000000000000002	"Con"	"Interior"	0.19202720123206873
1718	P05.EP.VI.CI.0,19.Con.Interior	P05	EP	VI	CI	0.19000000000000003	"Con"	"Interior"	0.19202720123206873
1719	P05.EP.VI.CI.0,2.Con.Interior	P05	EP	VI	CI	0.20000000000000004	"Con"	"Interior"	0.19202720123206873
1720	P05.EI.VI.CI.0,01.Con.Interior	P05	EI	VI	CI	0.01	"Con"	"Interior"	0.10976045378103727
1721	P05.EI.VI.CI.0,02.Con.Interior	P05	EI	VI	CI	0.02	"Con"	"Interior"	0.10321884121353442
1722	P05.EI.VI.CI.0,03.Con.Interior	P05	EI	VI	CI	0.03	"Con"	"Interior"	0.09667722864603157
1723	P05.EI.VI.CI.0,04.Con.Interior	P05	EI	VI	CI	0.04	"Con"	"Interior"	0.11059882981634894
1724	P05.EI.VI.CI.0,05.Con.Interior	P05	EI	VI	CI	0.05	"Con"	"Interior"	0.12452043098666632
1725	P05.EI.VI.CI.0,06.Con.Interior	P05	EI	VI	CI	0.060000000000000005	"Con"	"Interior"	0.1384420321569837
1726	P05.EI.VI.CI.0,07.Con.Interior	P05	EI	VI	CI	0.07	"Con"	"Interior"	0.15236363332730107
1727	P05.EI.VI.CI.0,08.Con.Interior	P05	EI	VI	CI	0.08	"Con"	"Interior"	0.15236363332730107
1728	P05.EI.VI.CI.0,09.Con.Interior	P05	EI	VI	CI	0.09	"Con"	"Interior"	0.15236363332730107
1729	P05.EI.VI.CI.0,1.Con.Interior	P05	EI	VI	CI	0.09999999999999999	"Con"	"Interior"	0.15236363332730107
1730	P05.EI.VI.CI.0,11.Con.Interior	P05	EI	VI	CI	0.10999999999999999	"Con"	"Interior"	0.15236363332730107
1731	P05.EI.VI.CI.0,12.Con.Interior	P05	EI	VI	CI	0.11999999999999998	"Con"	"Interior"	0.15236363332730107
1732	P05.EI.VI.CI.0,13.Con.Interior	P05	EI	VI	CI	0.12999999999999998	"Con"	"Interior"	0.15236363332730107
1733	P05.EI.VI.CI.0,14.Con.Interior	P05	EI	VI	CI	0.13999999999999999	"Con"	"Interior"	0.15236363332730107
1734	P05.EI.VI.CI.0,15.Con.Interior	P05	EI	VI	CI	0.15	"Con"	"Interior"	0.15236363332730107
1735	P05.EI.VI.CI.0,16.Con.Interior	P05	EI	VI	CI	0.16	"Con"	"Interior"	0.15236363332730107
1736	P05.EI.VI.CI.0,17.Con.Interior	P05	EI	VI	CI	0.17	"Con"	"Interior"	0.15236363332730107
1737	P05.EI.VI.CI.0,18.Con.Interior	P05	EI	VI	CI	0.18000000000000002	"Con"	"Interior"	0.15236363332730107
1738	P05.EI.VI.CI.0,19.Con.Interior	P05	EI	VI	CI	0.19000000000000003	"Con"	"Interior"	0.15236363332730107
1739	P05.EI.VI.CI.0,2.Con.Interior	P05	EI	VI	CI	0.20000000000000004	"Con"	"Interior"	0.15236363332730107
1740	P05.EM.VI.CI.0,01.Con.Interior	P05	EM	VI	CI	0.01	"Con"	"Interior"	0.07224899982020094
1741	P05.EM.VI.CI.0,02.Con.Interior	P05	EM	VI	CI	0.02	"Con"	"Interior"	0.06765316306243552
1742	P05.EM.VI.CI.0,03.Con.Interior	P05	EM	VI	CI	0.03	"Con"	"Interior"	0.06305732630467009
1743	P05.EM.VI.CI.0,04.Con.Interior	P05	EM	VI	CI	0.04	"Con"	"Interior"	0.07553942467683283
1744	P05.EM.VI.CI.0,05.Con.Interior	P05	EM	VI	CI	0.05	"Con"	"Interior"	0.08802152304899558
1745	P05.EM.VI.CI.0,06.Con.Interior	P05	EM	VI	CI	0.060000000000000005	"Con"	"Interior"	0.10050362142115832
1746	P05.EM.VI.CI.0,07.Con.Interior	P05	EM	VI	CI	0.07	"Con"	"Interior"	0.11298571979332106
1747	P05.EM.VI.CI.0,08.Con.Interior	P05	EM	VI	CI	0.08	"Con"	"Interior"	0.11298571979332106
1748	P05.EM.VI.CI.0,09.Con.Interior	P05	EM	VI	CI	0.09	"Con"	"Interior"	0.11298571979332106
1749	P05.EM.VI.CI.0,1.Con.Interior	P05	EM	VI	CI	0.09999999999999999	"Con"	"Interior"	0.11298571979332106
1750	P05.EM.VI.CI.0,11.Con.Interior	P05	EM	VI	CI	0.10999999999999999	"Con"	"Interior"	0.11298571979332106
1751	P05.EM.VI.CI.0,12.Con.Interior	P05	EM	VI	CI	0.11999999999999998	"Con"	"Interior"	0.11298571979332106
1752	P05.EM.VI.CI.0,13.Con.Interior	P05	EM	VI	CI	0.12999999999999998	"Con"	"Interior"	0.11298571979332106
1753	P05.EM.VI.CI.0,14.Con.Interior	P05	EM	VI	CI	0.13999999999999999	"Con"	"Interior"	0.11298571979332106
1754	P05.EM.VI.CI.0,15.Con.Interior	P05	EM	VI	CI	0.15	"Con"	"Interior"	0.11298571979332106
1755	P05.EM.VI.CI.0,16.Con.Interior	P05	EM	VI	CI	0.16	"Con"	"Interior"	0.11298571979332106
1756	P05.EM.VI.CI.0,17.Con.Interior	P05	EM	VI	CI	0.17	"Con"	"Interior"	0.11298571979332106
1757	P05.EM.VI.CI.0,18.Con.Interior	P05	EM	VI	CI	0.18000000000000002	"Con"	"Interior"	0.11298571979332106
1758	P05.EM.VI.CI.0,19.Con.Interior	P05	EM	VI	CI	0.19000000000000003	"Con"	"Interior"	0.11298571979332106
1759	P05.EM.VI.CI.0,2.Con.Interior	P05	EM	VI	CI	0.20000000000000004	"Con"	"Interior"	0.11298571979332106
1760	P06.EP.VI.SA.0	P06	EP	VI	SA	0	0	0	1.3357441229835514
1761	P06.EM.VI.SA.0	P06	EM	VI	SA	0	0	0	0.21876912298355133
1762	P06.EP.VI.CE.0,01	P06	EP	VI	CE	0.01	0	0	0.9929089414220567
1763	P06.EM.VI.CE.0,01	P06	EM	VI	CE	0.01	0	0	0.23806519142205662
1764	P06.EP.VI.CE.0,03	P06	EP	VI	CE	0.03	0	0	0.11903259571102831
1765	P06.EM.VI.CE.0,03	P06	EM	VI	CE	0.03	0	0	0.11903259571102831
\.


--
-- TOC entry 3834 (class 0 OID 16818)
-- Dependencies: 288
-- Data for Name: thermals_bridges_walls; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.thermals_bridges_walls (po1_length, po1_id_element, po2_length, po2_id_element, po3_length, po3_id_element, po4_length, po4_e_aislacion, po4_id_element, id, wall_id, enclosure_id) FROM stdin;
\.


--
-- TOC entry 3764 (class 0 OID 16400)
-- Dependencies: 218
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (name, lastname, email, number_phone, birthdate, country, ubigeo, proffesion, direccion, id, password, active, is_deleted, created_at, updated_at, role_id, last_activity) FROM stdin;
Usuario	Prueba	test@test.com	999999999	2025-01-22	Chile	9809	\N	\N	2	$2b$12$fS8F.FoUU469woAhCCbR9.xCqz0AkXjxE0dZkzX0gmKSjO2.CYdIG	t	f	2025-09-05 09:42:50.370929	2025-09-05 09:42:50.37093	2	\N
Admin	System	admin@admin.com	999999999	2025-01-22	Chile	9809	\N	\N	1	$2b$12$VeETnKjAFHB8aWHFheEFQO8irTfcY6hEZjujleQrwG5eLpGAmyHdi	t	f	2025-09-05 09:42:50.370919	2025-09-05 09:42:50.370926	1	2025-09-19 02:32:31.425574
\.


--
-- TOC entry 3836 (class 0 OID 16830)
-- Dependencies: 290
-- Data for Name: wallpo; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.wallpo (id, enclosure_id, wall_id, tipo_muro, nombre, orientacion, longitud_pt, categoria_1, categoria_2, posicion_aislamiento_1, posicion_aislamiento_2, e_aislamient0_1, e_aislamiento_2, codigo_pt, pt, pt_lineal, espacio_contiguo) FROM stdin;
\.


--
-- TOC entry 3822 (class 0 OID 16734)
-- Dependencies: 276
-- Data for Name: walls; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.walls (wall_id, characteristics, angulo_azimut, area, id, enclosure_id, orientation, u) FROM stdin;
\.


--
-- TOC entry 3766 (class 0 OID 16409)
-- Dependencies: 220
-- Data for Name: weather_metadata; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.weather_metadata (id, name, location, version, created_at, content_hash, country, city, district, extension, file_size, zone, complementary) FROM stdin;
1	chl_la_cisterna_santiago_05_09_2025	public/uploads/chl_la_cisterna_santiago_05_09_2025.processed.parquet	1	2025-09-05 10:39:08.980821	2e4c11921b719d523c325e297ad8e769	chl	la_cisterna	santiago	.xlsx	957980	D	public/uploads/chl_la_cisterna_santiago_05_09_2025_monthly.processed.parquet
2	chl_alto_hospicio_iquique_11_09_2025	public/uploads/chl_alto_hospicio_iquique_11_09_2025.processed.parquet	1	2025-09-11 20:19:50.111	c1d690a606ca08809924f418be4b6e74	chl	alto_hospicio	iquique	.xlsx	955641	A	public/uploads/chl_alto_hospicio_iquique_11_09_2025_monthly.processed.parquet
3	chl_camarones_arica_11_09_2025	public/uploads/chl_camarones_arica_11_09_2025.processed.parquet	1	2025-09-11 21:57:10.18175	97d8b07243defb42211f8402131ff068	chl	camarones	arica	.xlsx	722468		public/uploads/chl_camarones_arica_11_09_2025_monthly.processed.parquet
4	chl_copiapó_copiapó_11_09_2025	public/uploads/chl_copiapó_copiapó_11_09_2025.processed.parquet	1	2025-09-11 22:02:12.105873	11e9a2f6f7cf6738987e7e96e30e9abd	chl	copiapó	copiapó	.xlsx	720538	A	public/uploads/chl_copiapó_copiapó_11_09_2025_monthly.processed.parquet
6	chl_iquique_iquique_11_09_2025	public/uploads/chl_iquique_iquique_11_09_2025.processed.parquet	1	2025-09-11 22:03:38.340896	b5a9c3d1be8833e644c21735171094c8	chl	iquique	iquique	.xlsx	723398	A	public/uploads/chl_iquique_iquique_11_09_2025_monthly.processed.parquet
7	chl_tocopilla_tocopilla_11_09_2025	public/uploads/chl_tocopilla_tocopilla_11_09_2025.processed.parquet	1	2025-09-11 22:05:07.774273	9e582801b1e378e70a65cd74c7f00913	chl	tocopilla	tocopilla	.xlsx	721662	A	public/uploads/chl_tocopilla_tocopilla_11_09_2025_monthly.processed.parquet
8	chl_alto_del_carmen_huasco_11_09_2025	public/uploads/chl_alto_del_carmen_huasco_11_09_2025.processed.parquet	1	2025-09-11 22:05:38.971794	0af5905c9f3803767efcdc4d6761d5ea	chl	alto_del_carmen	huasco	.xlsx	721408	A	public/uploads/chl_alto_del_carmen_huasco_11_09_2025_monthly.processed.parquet
9	chl_calama_el_loa_11_09_2025	public/uploads/chl_calama_el_loa_11_09_2025.processed.parquet	1	2025-09-11 22:06:27.306854	898da32572897ead102cddc3749a40e6	chl	calama	el_loa	.xlsx	734177	A	public/uploads/chl_calama_el_loa_11_09_2025_monthly.processed.parquet
11	chl_copiapó_copiapó_11_09_2025	public/uploads/chl_copiapó_copiapó_11_09_2025.processed.parquet	1	2025-09-11 22:07:59.052983	4cf9912cb76c954138b0d2b398807ce1	chl	copiapó	copiapó	.xlsx	733106	B	public/uploads/chl_copiapó_copiapó_11_09_2025_monthly.processed.parquet
12	chl_diego_de_almagro_chañaral_11_09_2025	public/uploads/chl_diego_de_almagro_chañaral_11_09_2025.processed.parquet	1	2025-09-11 22:10:30.472315	1e95dd3a18d097f1c710752b510df1eb	chl	diego_de_almagro	chañaral	.xlsx	727740	B	public/uploads/chl_diego_de_almagro_chañaral_11_09_2025_monthly.processed.parquet
14	chl_illapel_choapa_11_09_2025	public/uploads/chl_illapel_choapa_11_09_2025.processed.parquet	1	2025-09-11 22:10:58.648514	5cf690ea76947caebe2d305c31bf4b6d	chl	illapel	choapa	.xlsx	723078	B	public/uploads/chl_illapel_choapa_11_09_2025_monthly.processed.parquet
15	chl_la_higuera_elqui_11_09_2025	public/uploads/chl_la_higuera_elqui_11_09_2025.processed.parquet	1	2025-09-11 22:11:12.727434	1228af075cf384018948d56e0291c5be	chl	la_higuera	elqui	.xlsx	719691	B	public/uploads/chl_la_higuera_elqui_11_09_2025_monthly.processed.parquet
16	chl_maría_elena_tocopilla_11_09_2025	public/uploads/chl_maría_elena_tocopilla_11_09_2025.processed.parquet	1	2025-09-11 22:11:36.071283	bad407066f73ff85813eb5ad4af7e027	chl	maría_elena	tocopilla	.xlsx	728355	B	public/uploads/chl_maría_elena_tocopilla_11_09_2025_monthly.processed.parquet
17	chl_alto_del_carmen_huasco_11_09_2025	public/uploads/chl_alto_del_carmen_huasco_11_09_2025.processed.parquet	1	2025-09-11 22:15:24.298348	0af5905c9f3803767efcdc4d6761d5ea	chl	alto_del_carmen	huasco	.xlsx	721408	B	public/uploads/chl_alto_del_carmen_huasco_11_09_2025_monthly.processed.parquet
18	chl_calama_el_loa_11_09_2025	public/uploads/chl_calama_el_loa_11_09_2025.processed.parquet	1	2025-09-11 22:17:03.179783	898da32572897ead102cddc3749a40e6	chl	calama	el_loa	.xlsx	734177	B	public/uploads/chl_calama_el_loa_11_09_2025_monthly.processed.parquet
19	chl_camarones_arica_11_09_2025	public/uploads/chl_camarones_arica_11_09_2025.processed.parquet	1	2025-09-11 22:17:47.39627	0192df9709aaeffdadbbf99f60fbdbf6	chl	camarones	arica	.xlsx	702611	B	public/uploads/chl_camarones_arica_11_09_2025_monthly.processed.parquet
10	chl_camarones_arica_11_09_2025	public/uploads/chl_camarones_arica_11_09_2025.processed.parquet	2	2025-09-11 22:21:44.107128	97d8b07243defb42211f8402131ff068	chl	camarones	arica	.xlsx	722468	A	public/uploads/chl_camarones_arica_11_09_2025_monthly.processed.parquet
20	per_chachapoyas_chachapoyas_12_09_2025	public/uploads/per_chachapoyas_chachapoyas_12_09_2025.processed.parquet	1	2025-09-12 22:30:36.298428	6f8a2541a8907adb3cf67db337be44af	per	chachapoyas	chachapoyas	.xlsx	372399	CEJM	public/uploads/per_chachapoyas_chachapoyas_12_09_2025_monthly.processed.parquet
21	per_huancayo_huancayo_12_09_2025	public/uploads/per_huancayo_huancayo_12_09_2025.processed.parquet	1	2025-09-12 22:36:26.832528	599fba6e9a8aaec5c7d3ca7d7c696623	per	huancayo	huancayo	.xlsx	380588	MEA	public/uploads/per_huancayo_huancayo_12_09_2025_monthly.processed.parquet
22	per_trujillo_trujillo_12_09_2025	public/uploads/per_trujillo_trujillo_12_09_2025.processed.parquet	1	2025-09-12 22:39:09.427873	929e61981b554ec1e9694e325c73978d	per	trujillo	trujillo	.xlsx	375662	DEM	public/uploads/per_trujillo_trujillo_12_09_2025_monthly.processed.parquet
23	per_lambayeque_lambayeque_12_09_2025	public/uploads/per_lambayeque_lambayeque_12_09_2025.processed.parquet	1	2025-09-12 22:41:33.93433	ee02c026578b9bd2b451fba31b5e8751	per	lambayeque	lambayeque	.xlsx	377473	DES	public/uploads/per_lambayeque_lambayeque_12_09_2025_monthly.processed.parquet
24	per_lima_lima_12_09_2025	public/uploads/per_lima_lima_12_09_2025.processed.parquet	1	2025-09-12 22:42:50.987408	31dd6b3da2169c789e219a43e5921707	per	lima	lima	.xlsx	375600	DEC	public/uploads/per_lima_lima_12_09_2025_monthly.processed.parquet
5	chl_huara_tamarugal_11_09_2025	public/uploads/chl_huara_tamarugal_18_09_2025.processed.parquet	2	2025-09-18 03:37:13.952078	6f89790d56770bccd804eae38a29d40f	chl	huara	tamarugal	.xlsx	714088	A	public/uploads/chl_huara_tamarugal_18_09_2025_monthly.processed.parquet
26	ecu_quito_quito_12_09_2025	public/uploads/ecu_quito_quito_12_09_2025.processed.parquet	1	2025-09-12 23:20:12.292996	86a702b3bf7b840ca51030c3c41fe2a8	ecu	quito	quito	.xlsx	344954	COL	public/uploads/ecu_quito_quito_12_09_2025_monthly.processed.parquet
27	ecu_guayaquil_guayaquil_12_09_2025	public/uploads/ecu_guayaquil_guayaquil_12_09_2025.processed.parquet	1	2025-09-12 23:20:38.328521	45c9d6a619168abe26759f51dbacd71f	ecu	guayaquil	guayaquil	.xlsx	374382	HUM	public/uploads/ecu_guayaquil_guayaquil_12_09_2025_monthly.processed.parquet
13	chl_huara_tamarugal_11_09_2025	public/uploads/chl_huara_tamarugal_18_09_2025.processed.parquet	2	2025-09-18 03:38:42.960144	d1e14015a108d1a074ff2b2a1d7a3b13	chl	huara	tamarugal	.xlsx	724183	B	public/uploads/chl_huara_tamarugal_18_09_2025_monthly.processed.parquet
28	ecu_cuenca_cuenca_12_09_2025	public/uploads/ecu_cuenca_cuenca_12_09_2025.processed.parquet	1	2025-09-12 23:21:13.126238	dab1d9e18a9485643d7dce49e6618ef0	ecu	cuenca	cuenca	.xlsx	371758	COL	public/uploads/ecu_cuenca_cuenca_12_09_2025_monthly.processed.parquet
29	ecu_ambato_ambato_12_09_2025	public/uploads/ecu_ambato_ambato_12_09_2025.processed.parquet	1	2025-09-12 23:21:40.531962	25e287564600e620c8f2b2fe113e6d94	ecu	ambato	ambato	.xlsx	330721	COT	public/uploads/ecu_ambato_ambato_12_09_2025_monthly.processed.parquet
30	ecu_loja_loja_12_09_2025	public/uploads/ecu_loja_loja_12_09_2025.processed.parquet	1	2025-09-12 23:21:56.302613	b688fa1a8ec9a683f49f9d4c3d2891e1	ecu	loja	loja	.xlsx	330988	COL	public/uploads/ecu_loja_loja_12_09_2025_monthly.processed.parquet
31	ecu_salinas_ibarra_12_09_2025	public/uploads/ecu_salinas_ibarra_12_09_2025.processed.parquet	1	2025-09-12 23:22:19.672929	bfac3e75ff9591014bf9d05be59a49e2	ecu	salinas	ibarra	.xlsx	370340	HUC	public/uploads/ecu_salinas_ibarra_12_09_2025_monthly.processed.parquet
32	ecu_san_miguel_de_ibarra_ibarra_12_09_2025	public/uploads/ecu_san_miguel_de_ibarra_ibarra_12_09_2025.processed.parquet	1	2025-09-12 23:22:39.295443	fe4df098514d5ac65d0c402af1d85082	ecu	san_miguel_de_ibarra	ibarra	.xlsx	334108	COL	public/uploads/ecu_san_miguel_de_ibarra_ibarra_12_09_2025_monthly.processed.parquet
37	ecu_azogues_azogues_12_09_2025	public/uploads/ecu_azogues_azogues_12_09_2025.processed.parquet	1	2025-09-12 23:24:30.967112	eae127cc2dc799049e3b2e75f44502cb	ecu	azogues	azogues	.xlsx	331740	HUC	public/uploads/ecu_azogues_azogues_12_09_2025_monthly.processed.parquet
38	ecu_latacunga_latacunga_12_09_2025	public/uploads/ecu_latacunga_latacunga_12_09_2025.processed.parquet	1	2025-09-12 23:24:50.863794	e74517a69b7825a7d4c548b71e01117c	ecu	latacunga	latacunga	.xlsx	332348	COT	public/uploads/ecu_latacunga_latacunga_12_09_2025_monthly.processed.parquet
39	ecu_santa_rosa_santa_rosa_12_09_2025	public/uploads/ecu_santa_rosa_santa_rosa_12_09_2025.processed.parquet	1	2025-09-12 23:25:55.179239	69f84a34f03a4d765c2c34beb8b3db8d	ecu	santa_rosa	santa_rosa	.xlsx	377255	HUM	public/uploads/ecu_santa_rosa_santa_rosa_12_09_2025_monthly.processed.parquet
40	ecu_babahoyo_babahoyo_12_09_2025	public/uploads/ecu_babahoyo_babahoyo_12_09_2025.processed.parquet	1	2025-09-12 23:26:10.667671	9181df6a759f3895025fe3526a2b4c45	ecu	babahoyo	babahoyo	.xlsx	330188	HUM	public/uploads/ecu_babahoyo_babahoyo_12_09_2025_monthly.processed.parquet
41	ecu_cayambe_cayambe_12_09_2025	public/uploads/ecu_cayambe_cayambe_12_09_2025.processed.parquet	1	2025-09-12 23:26:26.242632	dd765a7a567373ac20b8d603d84af1a0	ecu	cayambe	cayambe	.xlsx	377591	COL	public/uploads/ecu_cayambe_cayambe_12_09_2025_monthly.processed.parquet
33	ecu_manta_manta_12_09_2025	public/uploads/ecu_manta_manta_12_09_2025.processed.parquet	1	2025-09-12 23:22:57.436628	586a55cdfaf70e90fc7c89970d2aa9ab	ecu	manta	manta	.xlsx	372206	HUM	public/uploads/ecu_manta_manta_12_09_2025_monthly.processed.parquet
34	ecu_machala_machala_12_09_2025	public/uploads/ecu_machala_machala_12_09_2025.processed.parquet	1	2025-09-12 23:23:21.109785	fa3e347c322a6051c36bd951194072e0	ecu	machala	machala	.xlsx	330169	HUM	public/uploads/ecu_machala_machala_12_09_2025_monthly.processed.parquet
35	ecu_portoviejo_portoviejo_12_09_2025	public/uploads/ecu_portoviejo_portoviejo_12_09_2025.processed.parquet	1	2025-09-12 23:23:39.943387	819a0bb272b63df7968fd921dfc56619	ecu	portoviejo	portoviejo	.xlsx	328010	HUM	public/uploads/ecu_portoviejo_portoviejo_12_09_2025_monthly.processed.parquet
36	ecu_riobamba_riobamba_12_09_2025	public/uploads/ecu_riobamba_riobamba_12_09_2025.processed.parquet	1	2025-09-12 23:23:56.045061	de01d68cdfdfdcbbfcb6d3cc4c1e1106	ecu	riobamba	riobamba	.xlsx	332335	COT	public/uploads/ecu_riobamba_riobamba_12_09_2025_monthly.processed.parquet
42	ecu_zamora_zamora_12_09_2025	public/uploads/ecu_zamora_zamora_12_09_2025.processed.parquet	1	2025-09-12 23:27:26.753689	be28cc7e055f218c8c101ec300a598ac	ecu	zamora	zamora	.xlsx	329742	HUC	public/uploads/ecu_zamora_zamora_12_09_2025_monthly.processed.parquet
43	ecu_la_troncal_la_troncal_12_09_2025	public/uploads/ecu_la_troncal_la_troncal_12_09_2025.processed.parquet	1	2025-09-12 23:27:44.8281	66a163d288b490a74f17e954e1ea40e5	ecu	la_troncal	la_troncal	.xlsx	376796	HUC	public/uploads/ecu_la_troncal_la_troncal_12_09_2025_monthly.processed.parquet
44	ecu_caluma_caluma_12_09_2025	public/uploads/ecu_caluma_caluma_12_09_2025.processed.parquet	1	2025-09-12 23:28:27.732486	8188115bdac55123eba1f10025cfd831	ecu	caluma	caluma	.xlsx	376847	HUC	public/uploads/ecu_caluma_caluma_12_09_2025_monthly.processed.parquet
45	ecu_el_carmen_el_carmen_12_09_2025	public/uploads/ecu_el_carmen_el_carmen_12_09_2025.processed.parquet	1	2025-09-12 23:28:44.397655	298df2ee1c4fe6483254391760c9f4f4	ecu	el_carmen	el_carmen	.xlsx	374973	HUM	public/uploads/ecu_el_carmen_el_carmen_12_09_2025_monthly.processed.parquet
46	ecu_chone_chone_12_09_2025	public/uploads/ecu_chone_chone_12_09_2025.processed.parquet	1	2025-09-12 23:28:56.150897	f09f570e2598fc5b9890c9e68d504b6c	ecu	chone	chone	.xlsx	375072	HUM	public/uploads/ecu_chone_chone_12_09_2025_monthly.processed.parquet
47	ecu_quevedo_quevedo_12_09_2025	public/uploads/ecu_quevedo_quevedo_12_09_2025.processed.parquet	1	2025-09-12 23:29:10.027713	d838be6bdd6f0355690b89b64ea50ea5	ecu	quevedo	quevedo	.xlsx	375501	HUM	public/uploads/ecu_quevedo_quevedo_12_09_2025_monthly.processed.parquet
48	ecu_catamayo_catamayo_12_09_2025	public/uploads/ecu_catamayo_catamayo_12_09_2025.processed.parquet	1	2025-09-12 23:30:08.729087	f1921989f8b8e633261517f524c77ea4	ecu	catamayo	catamayo	.xlsx	378743	HUC	public/uploads/ecu_catamayo_catamayo_12_09_2025_monthly.processed.parquet
49	ecu_gualaceo_gualaceo_12_09_2025	public/uploads/ecu_gualaceo_gualaceo_12_09_2025.processed.parquet	1	2025-09-12 23:30:28.141518	fe4deb76659190bdb9155e9202451de5	ecu	gualaceo	gualaceo	.xlsx	377649	COL	public/uploads/ecu_gualaceo_gualaceo_12_09_2025_monthly.processed.parquet
50	ecu_guaranda_guaranda_12_09_2025	public/uploads/ecu_guaranda_guaranda_12_09_2025.processed.parquet	1	2025-09-12 23:30:51.122013	ad88f88d39e66223822690526c867336	ecu	guaranda	guaranda	.xlsx	332039	COT	public/uploads/ecu_guaranda_guaranda_12_09_2025_monthly.processed.parquet
51	ecu_tena_tena_12_09_2025	public/uploads/ecu_tena_tena_12_09_2025.processed.parquet	1	2025-09-12 23:31:09.729356	6c03d949b569227e74a1c37d357892a2	ecu	tena	tena	.xlsx	372911	HUC	public/uploads/ecu_tena_tena_12_09_2025_monthly.processed.parquet
52	ecu_el_coca_francisco_de_orellana_12_09_2025	public/uploads/ecu_el_coca_francisco_de_orellana_12_09_2025.processed.parquet	1	2025-09-12 23:31:31.39113	2dbf0dddd7622a6e7677a6abd95967d1	ecu	el_coca	francisco_de_orellana	.xlsx	360937	HUM	public/uploads/ecu_el_coca_francisco_de_orellana_12_09_2025_monthly.processed.parquet
53	ecu_santa_isabel_santa_isabel_12_09_2025	public/uploads/ecu_santa_isabel_santa_isabel_12_09_2025.processed.parquet	1	2025-09-12 23:31:58.17682	1abc7309d6a104b62b2d6117f6bf71b7	ecu	santa_isabel	santa_isabel	.xlsx	378539	HUC	public/uploads/ecu_santa_isabel_santa_isabel_12_09_2025_monthly.processed.parquet
54	ecu_azogues_azogues_12_09_2025	public/uploads/ecu_azogues_azogues_12_09_2025.processed.parquet	1	2025-09-12 23:32:18.50596	8a5edc54a102acacace618318b77229e	ecu	azogues	azogues	.xlsx	365435	FRI	public/uploads/ecu_azogues_azogues_12_09_2025_monthly.processed.parquet
55	ecu_balzar_balzar_12_09_2025	public/uploads/ecu_balzar_balzar_12_09_2025.processed.parquet	1	2025-09-12 23:32:50.302643	5d2535e963ab37bdb7ad4dfb40c1fcfa	ecu	balzar	balzar	.xlsx	375808	HUM	public/uploads/ecu_balzar_balzar_12_09_2025_monthly.processed.parquet
56	ecu_las_naves_las_naves_12_09_2025	public/uploads/ecu_las_naves_las_naves_12_09_2025.processed.parquet	1	2025-09-12 23:33:07.501376	feee25f1091cab21aeaa6896c79660a2	ecu	las_naves	las_naves	.xlsx	376065	HUM	public/uploads/ecu_las_naves_las_naves_12_09_2025_monthly.processed.parquet
57	ecu_pedernales_pedernales_12_09_2025	public/uploads/ecu_pedernales_pedernales_12_09_2025.processed.parquet	1	2025-09-12 23:33:26.779509	9eba683f0a0a5bfeff0a94b057400f4a	ecu	pedernales	pedernales	.xlsx	372423	HUM	public/uploads/ecu_pedernales_pedernales_12_09_2025_monthly.processed.parquet
58	ecu_pallatanga_pallatanga_12_09_2025	public/uploads/ecu_pallatanga_pallatanga_12_09_2025.processed.parquet	1	2025-09-12 23:33:40.170431	6fbd2af8a6607514659a184e3f826fe3	ecu	pallatanga	pallatanga	.xlsx	378168	COL	public/uploads/ecu_pallatanga_pallatanga_12_09_2025_monthly.processed.parquet
59	per_huaraz_huaraz_16_09_2025	public/uploads/per_huaraz_huaraz_16_09_2025.processed.parquet	1	2025-09-16 21:15:05.536935	52828a907b146af8083106e5520b7c55	per	huaraz	huaraz	.xlsx	271786	ALA	public/uploads/per_huaraz_huaraz_16_09_2025_monthly.processed.parquet
60	per_abancay_abancay_16_09_2025	public/uploads/per_abancay_abancay_16_09_2025.processed.parquet	1	2025-09-16 21:15:59.226652	3064d5fa2912fbe695622c6efb6ad8ca	per	abancay	abancay	.xlsx	310410	MEA	public/uploads/per_abancay_abancay_16_09_2025_monthly.processed.parquet
61	per_arequipa_arequipa_16_09_2025	public/uploads/per_arequipa_arequipa_16_09_2025.processed.parquet	1	2025-09-16 21:16:16.03924	bc4f98232c1be2ed8da81912cd07a8c1	per	arequipa	arequipa	.xlsx	310728	MEA	public/uploads/per_arequipa_arequipa_16_09_2025_monthly.processed.parquet
62	per_ayacucho_huamanga_16_09_2025	public/uploads/per_ayacucho_huamanga_16_09_2025.processed.parquet	1	2025-09-16 21:16:28.61177	3e4fe99d0124a042f863e1406dbf8248	per	ayacucho	huamanga	.xlsx	311760	MEA	public/uploads/per_ayacucho_huamanga_16_09_2025_monthly.processed.parquet
63	per_san_miguel_lima_16_09_2025	public/uploads/per_san_miguel_lima_16_09_2025.processed.parquet	1	2025-09-16 21:16:52.906736	75087620753ff2fdff4208dc7b808d94	per	san_miguel	lima	.xlsx	308652	DEC	public/uploads/per_san_miguel_lima_16_09_2025_monthly.processed.parquet
64	per_cusco_cusco_16_09_2025	public/uploads/per_cusco_cusco_16_09_2025.processed.parquet	1	2025-09-16 21:17:04.977437	8df41ba0f49aff401be31b4a84286e25	per	cusco	cusco	.xlsx	309018	MEA	public/uploads/per_cusco_cusco_16_09_2025_monthly.processed.parquet
65	per_huancavelica_huancavelica_16_09_2025	public/uploads/per_huancavelica_huancavelica_16_09_2025.processed.parquet	1	2025-09-16 21:19:03.627455	407d2b9b3a54070710bf63db3039e004	per	huancavelica	huancavelica	.xlsx	307363	ALA	public/uploads/per_huancavelica_huancavelica_16_09_2025_monthly.processed.parquet
66	per_huánuco_huánuco_16_09_2025	public/uploads/per_huánuco_huánuco_16_09_2025.processed.parquet	1	2025-09-16 21:19:39.155949	fce5c60a6de55701602e2df550bf6f3f	per	huánuco	huánuco	.xlsx	312026	ALA	public/uploads/per_huánuco_huánuco_16_09_2025_monthly.processed.parquet
67	per_ica_ica_16_09_2025	public/uploads/per_ica_ica_16_09_2025.processed.parquet	1	2025-09-16 21:19:53.582045	6772f040072b9ec810636414c7786c29	per	ica	ica	.xlsx	309588	DES	public/uploads/per_ica_ica_16_09_2025_monthly.processed.parquet
25	per_iquitos_maynas_12_09_2025	public/uploads/per_iquitos_maynas_16_09_2025.processed.parquet	3	2025-09-16 21:20:07.897315	262eee6e1633c05fcc0a4baf5a43c892	per	iquitos	maynas	.xlsx	356122	TRH	public/uploads/per_iquitos_maynas_16_09_2025_monthly.processed.parquet
68	per_tambopata_tambopata_16_09_2025	public/uploads/per_tambopata_tambopata_16_09_2025.processed.parquet	1	2025-09-16 21:20:33.695272	c989df72cb9959c301f64173485b7e78	per	tambopata	tambopata	.xlsx	357431	TRH	public/uploads/per_tambopata_tambopata_16_09_2025_monthly.processed.parquet
69	per_moquegua_mariscal_nieto_16_09_2025	public/uploads/per_moquegua_mariscal_nieto_16_09_2025.processed.parquet	1	2025-09-16 21:20:50.988917	55b76cff7bcc519d074a331cc3e5cb2d	per	moquegua	mariscal_nieto	.xlsx	377689	INB	public/uploads/per_moquegua_mariscal_nieto_16_09_2025_monthly.processed.parquet
70	per_chaupimarca_pasco_16_09_2025	public/uploads/per_chaupimarca_pasco_16_09_2025.processed.parquet	1	2025-09-16 21:21:06.351702	f5a4996ea4c0de33e9211014f15f7868	per	chaupimarca	pasco	.xlsx	365828	ALA	public/uploads/per_chaupimarca_pasco_16_09_2025_monthly.processed.parquet
71	per_piura_piura_16_09_2025	public/uploads/per_piura_piura_16_09_2025.processed.parquet	1	2025-09-16 21:21:21.066424	f5a4996ea4c0de33e9211014f15f7868	per	piura	piura	.xlsx	365828	SUH	public/uploads/per_piura_piura_16_09_2025_monthly.processed.parquet
72	per_sullana_sullana_16_09_2025	public/uploads/per_sullana_sullana_16_09_2025.processed.parquet	1	2025-09-16 21:21:42.356369	6c0c4191e790726d98700d8492a3bc3e	per	sullana	sullana	.xlsx	379808	SUH	public/uploads/per_sullana_sullana_16_09_2025_monthly.processed.parquet
73	per_puno_puno_16_09_2025	public/uploads/per_puno_puno_16_09_2025.processed.parquet	1	2025-09-16 21:21:57.270245	1726daf387fa4696ed09bdbc665c74f2	per	puno	puno	.xlsx	380131	NEV	public/uploads/per_puno_puno_16_09_2025_monthly.processed.parquet
74	per_moyobamba_moyobamba_16_09_2025	public/uploads/per_moyobamba_moyobamba_16_09_2025.processed.parquet	1	2025-09-16 21:22:18.322772	9b9fda4b0d2d0e1a5654b44d907bc397	per	moyobamba	moyobamba	.xlsx	363628	TRH	public/uploads/per_moyobamba_moyobamba_16_09_2025_monthly.processed.parquet
75	per_moyobamba_moyobamba_16_09_2025	public/uploads/per_moyobamba_moyobamba_16_09_2025.processed.parquet	1	2025-09-16 21:22:30.246677	e2bb6047cc37cbb6518c6966cc6dfdd1	per	moyobamba	moyobamba	.xlsx	375541	MEA	public/uploads/per_moyobamba_moyobamba_16_09_2025_monthly.processed.parquet
76	per_yarinacocha_coronel_portillo_16_09_2025	public/uploads/per_yarinacocha_coronel_portillo_16_09_2025.processed.parquet	1	2025-09-16 21:23:03.327297	ae53a0647aba799bc21f7d06c11de031	per	yarinacocha	coronel_portillo	.xlsx	362444	TRH	public/uploads/per_yarinacocha_coronel_portillo_16_09_2025_monthly.processed.parquet
77	ecu_esmeraldas_esmeraldas_18_09_2025	public/uploads/ecu_esmeraldas_esmeraldas_18_09_2025.processed.parquet	1	2025-09-18 03:28:24.448933	74b25e3ddfcb59e082b25131377c5739	ecu	esmeraldas	esmeraldas	.xlsx	330696	HUM	public/uploads/ecu_esmeraldas_esmeraldas_18_09_2025_monthly.processed.parquet
78	ecu_gualaquiza_gualaquiza_18_09_2025	public/uploads/ecu_gualaquiza_gualaquiza_18_09_2025.processed.parquet	1	2025-09-18 03:29:48.723546	8b090b6317451ed4eddbd9567db5631d	ecu	gualaquiza	gualaquiza	.xlsx	380590	HUC	public/uploads/ecu_gualaquiza_gualaquiza_18_09_2025_monthly.processed.parquet
79	ecu_zaruma_zaruma_18_09_2025	public/uploads/ecu_zaruma_zaruma_18_09_2025.processed.parquet	1	2025-09-18 03:30:34.643478	941c9c08c8442998fc2d7bdeffb04e4a	ecu	zaruma	zaruma	.xlsx	377768	HUM	public/uploads/ecu_zaruma_zaruma_18_09_2025_monthly.processed.parquet
80	ecu_mira_mira_18_09_2025	public/uploads/ecu_mira_mira_18_09_2025.processed.parquet	1	2025-09-18 03:31:17.689282	885c1bafee75aaba2126e223d1ca3ffa	ecu	mira	mira	.xlsx	370112	COT	public/uploads/ecu_mira_mira_18_09_2025_monthly.processed.parquet
81	chl_antofagasta_antofagasta_18_09_2025	public/uploads/chl_antofagasta_antofagasta_18_09_2025.processed.parquet	1	2025-09-18 03:36:15.667204	aa1cb4d57eaacb44d4371a7fbf7d686f	chl	antofagasta	antofagasta	.xlsx	724977	A	public/uploads/chl_antofagasta_antofagasta_18_09_2025_monthly.processed.parquet
82	chl_arica_arica_18_09_2025	public/uploads/chl_arica_arica_18_09_2025.processed.parquet	1	2025-09-18 03:36:33.603167	7f96cbdcb65f8e4e72f5d70ce7a730ae	chl	arica	arica	.xlsx	725971	A	public/uploads/chl_arica_arica_18_09_2025_monthly.processed.parquet
83	chl_caldera_copiapó_18_09_2025	public/uploads/chl_caldera_copiapó_18_09_2025.processed.parquet	1	2025-09-18 03:36:42.758891	c05aa8a79fd498842221aa3337f9625d	chl	caldera	copiapó	.xlsx	722514	A	public/uploads/chl_caldera_copiapó_18_09_2025_monthly.processed.parquet
84	chl_chañaral_chañaral_18_09_2025	public/uploads/chl_chañaral_chañaral_18_09_2025.processed.parquet	1	2025-09-18 03:36:51.346064	f65ff09e461967b06e12eab25fa6591e	chl	chañaral	chañaral	.xlsx	723189	A	public/uploads/chl_chañaral_chañaral_18_09_2025_monthly.processed.parquet
85	chl_freirina_huasco_18_09_2025	public/uploads/chl_freirina_huasco_18_09_2025.processed.parquet	1	2025-09-18 03:37:05.335209	9e28796f7e774a310c246a2aefd7f8a4	chl	freirina	huasco	.xlsx	726393	A	public/uploads/chl_freirina_huasco_18_09_2025_monthly.processed.parquet
86	chl_mejillones_antofagasta_18_09_2025	public/uploads/chl_mejillones_antofagasta_18_09_2025.processed.parquet	1	2025-09-18 03:37:43.943102	d8835c74bd7a74b86bc5c15ec127d5bc	chl	mejillones	antofagasta	.xlsx	727808	A	public/uploads/chl_mejillones_antofagasta_18_09_2025_monthly.processed.parquet
87	chl_taltal_antofagasta_18_09_2025	public/uploads/chl_taltal_antofagasta_18_09_2025.processed.parquet	1	2025-09-18 03:37:52.100299	b2e30762ec3a07098528afb240abf845	chl	taltal	antofagasta	.xlsx	718719	A	public/uploads/chl_taltal_antofagasta_18_09_2025_monthly.processed.parquet
88	chl_andacollo_elqui_18_09_2025	public/uploads/chl_andacollo_elqui_18_09_2025.processed.parquet	2	2025-09-18 03:38:14.47106	20824e682f744eaf2fffd0959a2a3343	chl	andacollo	elqui	.xlsx	722654	B	public/uploads/chl_andacollo_elqui_18_09_2025_monthly.processed.parquet
89	chl_arica_arica_18_09_2025	public/uploads/chl_arica_arica_18_09_2025.processed.parquet	1	2025-09-18 03:38:25.411813	8c7d280ea781d0949370f40db6746ba5	chl	arica	arica	.xlsx	724343	B	public/uploads/chl_arica_arica_18_09_2025_monthly.processed.parquet
90	chl_camiña_tamarugal_18_09_2025	public/uploads/chl_camiña_tamarugal_18_09_2025.processed.parquet	1	2025-09-18 03:38:34.442243	e7f77df7fef705336028c108740fc409	chl	camiña	tamarugal	.xlsx	718188	B	public/uploads/chl_camiña_tamarugal_18_09_2025_monthly.processed.parquet
91	chl_la_serena_elqui_18_09_2025	public/uploads/chl_la_serena_elqui_18_09_2025.processed.parquet	1	2025-09-18 03:38:52.885786	a42bd7a4a369777e8f8a574fe1514846	chl	la_serena	elqui	.xlsx	717781	B	public/uploads/chl_la_serena_elqui_18_09_2025_monthly.processed.parquet
92	chl_monte_patria_limarí_18_09_2025	public/uploads/chl_monte_patria_limarí_18_09_2025.processed.parquet	1	2025-09-18 03:39:06.448476	eddb1595f01e655026cd84750edfca5c	chl	monte_patria	limarí	.xlsx	721499	B	public/uploads/chl_monte_patria_limarí_18_09_2025_monthly.processed.parquet
93	chl_taltal_antofagasta_18_09_2025	public/uploads/chl_taltal_antofagasta_18_09_2025.processed.parquet	1	2025-09-18 03:39:16.700953	0eb6095ed81b2d714cdacef4c8296906	chl	taltal	antofagasta	.xlsx	730572	B	public/uploads/chl_taltal_antofagasta_18_09_2025_monthly.processed.parquet
94	col_leticia_amazonas_19_09_2025	public/uploads/col_leticia_amazonas_19_09_2025.processed.parquet	1	2025-09-19 02:43:01.932465	ed7c25721d7e5670a35d20f9050159c7	col	leticia	amazonas	.xlsx	358094	CAH	public/uploads/col_leticia_amazonas_19_09_2025_monthly.processed.parquet
95	col_medellín_antioquia_19_09_2025	public/uploads/col_medellín_antioquia_19_09_2025.processed.parquet	1	2025-09-19 02:43:51.401499	9b5b9656517705a40ef8dad18b78c198	col	medellín	antioquia	.xlsx	365894	CAH	public/uploads/col_medellín_antioquia_19_09_2025_monthly.processed.parquet
96	col_arauca_arauca_19_09_2025	public/uploads/col_arauca_arauca_19_09_2025.processed.parquet	1	2025-09-19 02:44:08.316095	43739014be7d9ff1880039b0f52f659f	col	arauca	arauca	.xlsx	372832	CAH	public/uploads/col_arauca_arauca_19_09_2025_monthly.processed.parquet
97	col_barranquilla_atlántico_19_09_2025	public/uploads/col_barranquilla_atlántico_19_09_2025.processed.parquet	2	2025-09-19 02:45:01.268005	0f142c94dd98e23f7f47ead97f9b70bb	col	barranquilla	atlántico	.xlsx	374296	CAH	public/uploads/col_barranquilla_atlántico_19_09_2025_monthly.processed.parquet
98	col_arjona_bolívar_19_09_2025	public/uploads/col_arjona_bolívar_19_09_2025.processed.parquet	1	2025-09-19 02:45:25.265224	c19c588c41389de740e2b12973c10a41	col	arjona	bolívar	.xlsx	361471	CAH	public/uploads/col_arjona_bolívar_19_09_2025_monthly.processed.parquet
99	col_manizales_caldas_19_09_2025	public/uploads/col_manizales_caldas_19_09_2025.processed.parquet	1	2025-09-19 02:45:59.679074	b35a907c58eaca696e49216b7722a6c8	col	manizales	caldas	.xlsx	355123	TEM	public/uploads/col_manizales_caldas_19_09_2025_monthly.processed.parquet
100	col_florencia_caquetá_19_09_2025	public/uploads/col_florencia_caquetá_19_09_2025.processed.parquet	1	2025-09-19 02:46:20.374655	2b4ecf8a344f5d1e7137b15883aeb794	col	florencia	caquetá	.xlsx	363774	CAH	public/uploads/col_florencia_caquetá_19_09_2025_monthly.processed.parquet
101	col_yopal_casanare_19_09_2025	public/uploads/col_yopal_casanare_19_09_2025.processed.parquet	1	2025-09-19 02:46:34.110721	e866156feba15d51bb5e6641e31a4846	col	yopal	casanare	.xlsx	373640	CAH	public/uploads/col_yopal_casanare_19_09_2025_monthly.processed.parquet
102	col_popayán_cauca_19_09_2025	public/uploads/col_popayán_cauca_19_09_2025.processed.parquet	1	2025-09-19 02:46:47.069544	046fb0134760a94561b8552d357bc5c4	col	popayán	cauca	.xlsx	375362	TEM	public/uploads/col_popayán_cauca_19_09_2025_monthly.processed.parquet
103	col_valledupar_cesar_19_09_2025	public/uploads/col_valledupar_cesar_19_09_2025.processed.parquet	1	2025-09-19 02:47:15.57376	40a9408ac51de8c4b1f5dc9d29ff363f	col	valledupar	cesar	.xlsx	370273	CAH	public/uploads/col_valledupar_cesar_19_09_2025_monthly.processed.parquet
104	col_quibdó_chocó_19_09_2025	public/uploads/col_quibdó_chocó_19_09_2025.processed.parquet	1	2025-09-19 02:47:31.399298	b3c228fa8d786f3a24282aa47a96e256	col	quibdó	chocó	.xlsx	358093	CAH	public/uploads/col_quibdó_chocó_19_09_2025_monthly.processed.parquet
105	col_montería_córdoba_19_09_2025	public/uploads/col_montería_córdoba_19_09_2025.processed.parquet	1	2025-09-19 02:47:51.310031	d8f1cc5f7000aba83b47cc395be41c1e	col	montería	córdoba	.xlsx	363990	CAH	public/uploads/col_montería_córdoba_19_09_2025_monthly.processed.parquet
106	col_bogotá,_d.c._bogotá,_d.c._19_09_2025	public/uploads/col_bogotá,_d.c._bogotá,_d.c._19_09_2025.processed.parquet	1	2025-09-19 02:48:25.610218	45aa3c141536db455abc4c3ca6664d11	col	bogotá,_d.c.	bogotá,_d.c.	.xlsx	362887	FRI	public/uploads/col_bogotá,_d.c._bogotá,_d.c._19_09_2025_monthly.processed.parquet
107	col_inírida_guainía_19_09_2025	public/uploads/col_inírida_guainía_19_09_2025.processed.parquet	1	2025-09-19 02:49:14.902707	f229b0ac7f01c188038a108137f37310	col	inírida	guainía	.xlsx	323300	CAH	public/uploads/col_inírida_guainía_19_09_2025_monthly.processed.parquet
108	col_san_josé_del_guaviare_guaviare_19_09_2025	public/uploads/col_san_josé_del_guaviare_guaviare_19_09_2025.processed.parquet	1	2025-09-19 02:49:35.660203	78634894cea3330c593a08436749cd7e	col	san_josé_del_guaviare	guaviare	.xlsx	321974	CAH	public/uploads/col_san_josé_del_guaviare_guaviare_19_09_2025_monthly.processed.parquet
109	col_neiva_huila_19_09_2025	public/uploads/col_neiva_huila_19_09_2025.processed.parquet	1	2025-09-19 02:49:50.494576	9c4b9a0427dc14d9c277537dac0a0070	col	neiva	huila	.xlsx	374993	TEM	public/uploads/col_neiva_huila_19_09_2025_monthly.processed.parquet
110	col_riohacha_la_guajira_19_09_2025	public/uploads/col_riohacha_la_guajira_19_09_2025.processed.parquet	1	2025-09-19 02:50:07.506746	433c1341d0cde2f91d5ed279c53b01e5	col	riohacha	la_guajira	.xlsx	372910	CAS	public/uploads/col_riohacha_la_guajira_19_09_2025_monthly.processed.parquet
111	col_santa_marta_magdalena_19_09_2025	public/uploads/col_santa_marta_magdalena_19_09_2025.processed.parquet	1	2025-09-19 02:50:22.659841	9d3dfd6b11d21dce2781fa1c2d4964cd	col	santa_marta	magdalena	.xlsx	372162	CAH	public/uploads/col_santa_marta_magdalena_19_09_2025_monthly.processed.parquet
112	col_villavicencio_meta_19_09_2025	public/uploads/col_villavicencio_meta_19_09_2025.processed.parquet	1	2025-09-19 02:50:42.06537	2a556d653ca96205f6e0764a046f683f	col	villavicencio	meta	.xlsx	373142	CAH	public/uploads/col_villavicencio_meta_19_09_2025_monthly.processed.parquet
113	col_pasto_nariño_19_09_2025	public/uploads/col_pasto_nariño_19_09_2025.processed.parquet	1	2025-09-19 02:50:56.299191	2e920c866fb3729310a5cf3362a19edd	col	pasto	nariño	.xlsx	361409	CAH	public/uploads/col_pasto_nariño_19_09_2025_monthly.processed.parquet
114	col_cúcuta_norte_de_santander_19_09_2025	public/uploads/col_cúcuta_norte_de_santander_19_09_2025.processed.parquet	1	2025-09-19 02:51:11.353061	9ce6ac6008d7b36cd3e6bc694651b574	col	cúcuta	norte_de_santander	.xlsx	376502	TEM	public/uploads/col_cúcuta_norte_de_santander_19_09_2025_monthly.processed.parquet
115	col_mocoa_putumayo_19_09_2025	public/uploads/col_mocoa_putumayo_19_09_2025.processed.parquet	1	2025-09-19 02:51:27.603195	37b3b95ea5d756d0605abac4fa012f5b	col	mocoa	putumayo	.xlsx	371734	CAH	public/uploads/col_mocoa_putumayo_19_09_2025_monthly.processed.parquet
116	col_armenia_quindío_19_09_2025	public/uploads/col_armenia_quindío_19_09_2025.processed.parquet	1	2025-09-19 02:51:48.78592	04e57e57f3325493b769a1550774ba0f	col	armenia	quindío	.xlsx	371072	TEM	public/uploads/col_armenia_quindío_19_09_2025_monthly.processed.parquet
117	col_pereira_risaralda_19_09_2025	public/uploads/col_pereira_risaralda_19_09_2025.processed.parquet	1	2025-09-19 02:52:01.61512	3fcd09139038937d4a59aec9c2f1ce39	col	pereira	risaralda	.xlsx	366330	TEM	public/uploads/col_pereira_risaralda_19_09_2025_monthly.processed.parquet
118	col_san_andrés_san_andrés_y_providencia_19_09_2025	public/uploads/col_san_andrés_san_andrés_y_providencia_19_09_2025.processed.parquet	1	2025-09-19 02:53:05.050558	9fb8f7028a339ede876085efc350fe63	col	san_andrés	san_andrés_y_providencia	.xlsx	364880	CAH	public/uploads/col_san_andrés_san_andrés_y_providencia_19_09_2025_monthly.processed.parquet
119	col_bucaramanga_santander_19_09_2025	public/uploads/col_bucaramanga_santander_19_09_2025.processed.parquet	1	2025-09-19 02:53:19.28683	7205d91db315b3097c27ed2fb7194d94	col	bucaramanga	santander	.xlsx	374294	CAH	public/uploads/col_bucaramanga_santander_19_09_2025_monthly.processed.parquet
120	col_sincelejo_sucre_19_09_2025	public/uploads/col_sincelejo_sucre_19_09_2025.processed.parquet	1	2025-09-19 02:53:41.901213	976376f0dd8110d01cbcb6e1cc1584ab	col	sincelejo	sucre	.xlsx	362473	CAH	public/uploads/col_sincelejo_sucre_19_09_2025_monthly.processed.parquet
121	col_ibagué_tolima_19_09_2025	public/uploads/col_ibagué_tolima_19_09_2025.processed.parquet	1	2025-09-19 02:53:59.419423	ea64463e8139ede75b93abde7ce32d1d	col	ibagué	tolima	.xlsx	374016	FRI	public/uploads/col_ibagué_tolima_19_09_2025_monthly.processed.parquet
122	col_cali_valle_del_cauca_19_09_2025	public/uploads/col_cali_valle_del_cauca_19_09_2025.processed.parquet	1	2025-09-19 02:54:15.110581	386a815f4ce576a3b0f4b42adb85b44c	col	cali	valle_del_cauca	.xlsx	374353	TEM	public/uploads/col_cali_valle_del_cauca_19_09_2025_monthly.processed.parquet
123	col_mitú_vaupés_19_09_2025	public/uploads/col_mitú_vaupés_19_09_2025.processed.parquet	1	2025-09-19 02:54:27.616696	7b09af3e063a255088ad2d23424815df	col	mitú	vaupés	.xlsx	354429	CAH	public/uploads/col_mitú_vaupés_19_09_2025_monthly.processed.parquet
124	col_puerto_carreño_vichada_19_09_2025	public/uploads/col_puerto_carreño_vichada_19_09_2025.processed.parquet	1	2025-09-19 02:54:38.505429	f704a17a2ae8f981132750eaa6c357db	col	puerto_carreño	vichada	.xlsx	372431	CAH	public/uploads/col_puerto_carreño_vichada_19_09_2025_monthly.processed.parquet
\.


--
-- TOC entry 3838 (class 0 OID 16845)
-- Dependencies: 292
-- Data for Name: windowpo; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.windowpo (id, enclosure_id, window_id, tipo, hosted_in, orientacion, altura, ancho, categoria_muro, categoria_ventana, posicion_aislamiento, e_aislamient0_1, e_aislamiento_2, retorno, posicion_vidrio, codigo_pt, pt, pt_lineal, espacio_contiguo) FROM stdin;
\.


--
-- TOC entry 3830 (class 0 OID 16790)
-- Dependencies: 284
-- Data for Name: windows; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.windows (window_id, characteristics, angulo_azimut, housed_in, "position", with_no_return, high, broad, id, enclosure_id, orientation, clousure_type, frame) FROM stdin;
\.


--
-- TOC entry 3889 (class 0 OID 0)
-- Dependencies: 215
-- Name: agua_caliente_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.agua_caliente_id_seq', 1, false);


--
-- TOC entry 3890 (class 0 OID 0)
-- Dependencies: 261
-- Name: building_conditions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.building_conditions_id_seq', 120, true);


--
-- TOC entry 3891 (class 0 OID 0)
-- Dependencies: 235
-- Name: calculate_piso_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.calculate_piso_id_seq', 1, false);


--
-- TOC entry 3892 (class 0 OID 0)
-- Dependencies: 267
-- Name: calculation_results_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.calculation_results_id_seq', 1, false);


--
-- TOC entry 3893 (class 0 OID 0)
-- Dependencies: 221
-- Name: calculations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.calculations_id_seq', 6, true);


--
-- TOC entry 3894 (class 0 OID 0)
-- Dependencies: 237
-- Name: casobase_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.casobase_id_seq', 1, false);


--
-- TOC entry 3895 (class 0 OID 0)
-- Dependencies: 263
-- Name: comunas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.comunas_id_seq', 246, true);


--
-- TOC entry 3896 (class 0 OID 0)
-- Dependencies: 257
-- Name: constants_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.constants_id_seq', 41, true);


--
-- TOC entry 3897 (class 0 OID 0)
-- Dependencies: 241
-- Name: customizations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.customizations_id_seq', 1, false);


--
-- TOC entry 3898 (class 0 OID 0)
-- Dependencies: 239
-- Name: dailyschedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.dailyschedule_id_seq', 120, true);


--
-- TOC entry 3899 (class 0 OID 0)
-- Dependencies: 273
-- Name: details_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.details_id_seq', 6, true);


--
-- TOC entry 3900 (class 0 OID 0)
-- Dependencies: 223
-- Name: details_part_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.details_part_id_seq', 3, true);


--
-- TOC entry 3901 (class 0 OID 0)
-- Dependencies: 295
-- Name: divisions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.divisions_id_seq', 1, false);


--
-- TOC entry 3902 (class 0 OID 0)
-- Dependencies: 277
-- Name: doors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.doors_id_seq', 1, false);


--
-- TOC entry 3903 (class 0 OID 0)
-- Dependencies: 259
-- Name: elements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.elements_id_seq', 16, true);


--
-- TOC entry 3904 (class 0 OID 0)
-- Dependencies: 271
-- Name: enclosures_generals_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.enclosures_generals_id_seq', 1, false);


--
-- TOC entry 3905 (class 0 OID 0)
-- Dependencies: 227
-- Name: enclosures_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.enclosures_id_seq', 30, true);


--
-- TOC entry 3906 (class 0 OID 0)
-- Dependencies: 247
-- Name: energy_data_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.energy_data_id_seq', 54, true);


--
-- TOC entry 3907 (class 0 OID 0)
-- Dependencies: 229
-- Name: favs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.favs_id_seq', 1, false);


--
-- TOC entry 3908 (class 0 OID 0)
-- Dependencies: 293
-- Name: floorpo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.floorpo_id_seq', 1, false);


--
-- TOC entry 3909 (class 0 OID 0)
-- Dependencies: 279
-- Name: floors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.floors_id_seq', 1, false);


--
-- TOC entry 3910 (class 0 OID 0)
-- Dependencies: 269
-- Name: formulas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.formulas_id_seq', 6, true);


--
-- TOC entry 3911 (class 0 OID 0)
-- Dependencies: 265
-- Name: heating_config_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.heating_config_id_seq', 1, false);


--
-- TOC entry 3912 (class 0 OID 0)
-- Dependencies: 249
-- Name: indicadores_finales_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.indicadores_finales_id_seq', 1, false);


--
-- TOC entry 3913 (class 0 OID 0)
-- Dependencies: 245
-- Name: levels_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.levels_id_seq', 15, true);


--
-- TOC entry 3914 (class 0 OID 0)
-- Dependencies: 285
-- Name: orientations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.orientations_id_seq', 1, false);


--
-- TOC entry 3915 (class 0 OID 0)
-- Dependencies: 253
-- Name: personal_access_token_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.personal_access_token_id_seq', 50, true);


--
-- TOC entry 3916 (class 0 OID 0)
-- Dependencies: 255
-- Name: projects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.projects_id_seq', 1, false);


--
-- TOC entry 3917 (class 0 OID 0)
-- Dependencies: 233
-- Name: pt_table_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.pt_table_id_seq', 1, false);


--
-- TOC entry 3918 (class 0 OID 0)
-- Dependencies: 243
-- Name: regiones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.regiones_id_seq', 1, false);


--
-- TOC entry 3919 (class 0 OID 0)
-- Dependencies: 251
-- Name: resultados_por_recinto_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.resultados_por_recinto_id_seq', 1, false);


--
-- TOC entry 3920 (class 0 OID 0)
-- Dependencies: 281
-- Name: roofs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.roofs_id_seq', 1, false);


--
-- TOC entry 3921 (class 0 OID 0)
-- Dependencies: 225
-- Name: tabla_py_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tabla_py_id_seq', 1, false);


--
-- TOC entry 3922 (class 0 OID 0)
-- Dependencies: 231
-- Name: thermal_bridges_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.thermal_bridges_id_seq', 1765, true);


--
-- TOC entry 3923 (class 0 OID 0)
-- Dependencies: 287
-- Name: thermals_bridges_walls_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.thermals_bridges_walls_id_seq', 1, false);


--
-- TOC entry 3924 (class 0 OID 0)
-- Dependencies: 217
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- TOC entry 3925 (class 0 OID 0)
-- Dependencies: 289
-- Name: wallpo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.wallpo_id_seq', 1, false);


--
-- TOC entry 3926 (class 0 OID 0)
-- Dependencies: 275
-- Name: walls_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.walls_id_seq', 1, false);


--
-- TOC entry 3927 (class 0 OID 0)
-- Dependencies: 219
-- Name: weather_metadata_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.weather_metadata_id_seq', 124, true);


--
-- TOC entry 3928 (class 0 OID 0)
-- Dependencies: 291
-- Name: windowpo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.windowpo_id_seq', 1, false);


--
-- TOC entry 3929 (class 0 OID 0)
-- Dependencies: 283
-- Name: windows_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.windows_id_seq', 1, false);


--
-- TOC entry 3509 (class 2606 OID 16398)
-- Name: agua_caliente agua_caliente_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agua_caliente
    ADD CONSTRAINT agua_caliente_pkey PRIMARY KEY (id);


--
-- TOC entry 3507 (class 2606 OID 16389)
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- TOC entry 3557 (class 2606 OID 16635)
-- Name: building_conditions building_conditions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.building_conditions
    ADD CONSTRAINT building_conditions_pkey PRIMARY KEY (id);


--
-- TOC entry 3530 (class 2606 OID 16497)
-- Name: calculate_piso calculate_piso_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.calculate_piso
    ADD CONSTRAINT calculate_piso_pkey PRIMARY KEY (id);


--
-- TOC entry 3565 (class 2606 OID 16680)
-- Name: calculation_results calculation_results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.calculation_results
    ADD CONSTRAINT calculation_results_pkey PRIMARY KEY (id);


--
-- TOC entry 3515 (class 2606 OID 16425)
-- Name: calculations calculations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.calculations
    ADD CONSTRAINT calculations_pkey PRIMARY KEY (id);


--
-- TOC entry 3532 (class 2606 OID 16506)
-- Name: casobase casobase_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.casobase
    ADD CONSTRAINT casobase_pkey PRIMARY KEY (id);


--
-- TOC entry 3559 (class 2606 OID 16649)
-- Name: comunas comunas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comunas
    ADD CONSTRAINT comunas_pkey PRIMARY KEY (id);


--
-- TOC entry 3552 (class 2606 OID 16606)
-- Name: constants constants_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.constants
    ADD CONSTRAINT constants_pkey PRIMARY KEY (id);


--
-- TOC entry 3536 (class 2606 OID 16524)
-- Name: customizations customizations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customizations
    ADD CONSTRAINT customizations_pkey PRIMARY KEY (id);


--
-- TOC entry 3534 (class 2606 OID 16515)
-- Name: dailyschedule dailyschedule_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dailyschedule
    ADD CONSTRAINT dailyschedule_pkey PRIMARY KEY (id);


--
-- TOC entry 3517 (class 2606 OID 16438)
-- Name: details_part details_part_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.details_part
    ADD CONSTRAINT details_part_pkey PRIMARY KEY (id);


--
-- TOC entry 3571 (class 2606 OID 16727)
-- Name: details details_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.details
    ADD CONSTRAINT details_pkey PRIMARY KEY (id);


--
-- TOC entry 3594 (class 2606 OID 16880)
-- Name: divisions divisions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.divisions
    ADD CONSTRAINT divisions_pkey PRIMARY KEY (id);


--
-- TOC entry 3575 (class 2606 OID 16755)
-- Name: doors doors_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.doors
    ADD CONSTRAINT doors_pkey PRIMARY KEY (id);


--
-- TOC entry 3555 (class 2606 OID 16621)
-- Name: elements elements_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.elements
    ADD CONSTRAINT elements_pkey PRIMARY KEY (id);


--
-- TOC entry 3569 (class 2606 OID 16708)
-- Name: enclosures_generals enclosures_generals_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.enclosures_generals
    ADD CONSTRAINT enclosures_generals_pkey PRIMARY KEY (id);


--
-- TOC entry 3521 (class 2606 OID 16456)
-- Name: enclosures enclosures_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.enclosures
    ADD CONSTRAINT enclosures_pkey PRIMARY KEY (id);


--
-- TOC entry 3542 (class 2606 OID 16551)
-- Name: energy_data energy_data_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.energy_data
    ADD CONSTRAINT energy_data_pkey PRIMARY KEY (id);


--
-- TOC entry 3524 (class 2606 OID 16470)
-- Name: favs favs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.favs
    ADD CONSTRAINT favs_pkey PRIMARY KEY (id);


--
-- TOC entry 3592 (class 2606 OID 16866)
-- Name: floorpo floorpo_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.floorpo
    ADD CONSTRAINT floorpo_pkey PRIMARY KEY (id);


--
-- TOC entry 3577 (class 2606 OID 16769)
-- Name: floors floors_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.floors
    ADD CONSTRAINT floors_pkey PRIMARY KEY (id);


--
-- TOC entry 3567 (class 2606 OID 16694)
-- Name: formulas formulas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.formulas
    ADD CONSTRAINT formulas_pkey PRIMARY KEY (id);


--
-- TOC entry 3561 (class 2606 OID 16663)
-- Name: heating_config heating_config_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.heating_config
    ADD CONSTRAINT heating_config_pkey PRIMARY KEY (id);


--
-- TOC entry 3563 (class 2606 OID 16665)
-- Name: heating_config heating_config_project_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.heating_config
    ADD CONSTRAINT heating_config_project_id_key UNIQUE (project_id);


--
-- TOC entry 3544 (class 2606 OID 16560)
-- Name: indicadores_finales indicadores_finales_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.indicadores_finales
    ADD CONSTRAINT indicadores_finales_pkey PRIMARY KEY (id);


--
-- TOC entry 3540 (class 2606 OID 16542)
-- Name: levels levels_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.levels
    ADD CONSTRAINT levels_pkey PRIMARY KEY (id);


--
-- TOC entry 3583 (class 2606 OID 16811)
-- Name: orientations orientations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orientations
    ADD CONSTRAINT orientations_pkey PRIMARY KEY (id);


--
-- TOC entry 3548 (class 2606 OID 16578)
-- Name: personal_access_token personal_access_token_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personal_access_token
    ADD CONSTRAINT personal_access_token_pkey PRIMARY KEY (id);


--
-- TOC entry 3550 (class 2606 OID 16592)
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- TOC entry 3528 (class 2606 OID 16490)
-- Name: pt_table pt_table_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pt_table
    ADD CONSTRAINT pt_table_pkey PRIMARY KEY (id);


--
-- TOC entry 3538 (class 2606 OID 16533)
-- Name: regiones regiones_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.regiones
    ADD CONSTRAINT regiones_pkey PRIMARY KEY (id);


--
-- TOC entry 3546 (class 2606 OID 16569)
-- Name: resultados_por_recinto resultados_por_recinto_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.resultados_por_recinto
    ADD CONSTRAINT resultados_por_recinto_pkey PRIMARY KEY (id);


--
-- TOC entry 3579 (class 2606 OID 16783)
-- Name: roofs roofs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roofs
    ADD CONSTRAINT roofs_pkey PRIMARY KEY (id);


--
-- TOC entry 3519 (class 2606 OID 16447)
-- Name: tabla_py tabla_py_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tabla_py
    ADD CONSTRAINT tabla_py_pkey PRIMARY KEY (id);


--
-- TOC entry 3526 (class 2606 OID 16483)
-- Name: thermal_bridges thermal_bridges_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.thermal_bridges
    ADD CONSTRAINT thermal_bridges_pkey PRIMARY KEY (id);


--
-- TOC entry 3585 (class 2606 OID 16823)
-- Name: thermals_bridges_walls thermals_bridges_walls_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.thermals_bridges_walls
    ADD CONSTRAINT thermals_bridges_walls_pkey PRIMARY KEY (id);


--
-- TOC entry 3511 (class 2606 OID 16407)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 3588 (class 2606 OID 16837)
-- Name: wallpo wallpo_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wallpo
    ADD CONSTRAINT wallpo_pkey PRIMARY KEY (id);


--
-- TOC entry 3573 (class 2606 OID 16741)
-- Name: walls walls_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.walls
    ADD CONSTRAINT walls_pkey PRIMARY KEY (id);


--
-- TOC entry 3513 (class 2606 OID 16416)
-- Name: weather_metadata weather_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.weather_metadata
    ADD CONSTRAINT weather_metadata_pkey PRIMARY KEY (id);


--
-- TOC entry 3590 (class 2606 OID 16852)
-- Name: windowpo windowpo_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.windowpo
    ADD CONSTRAINT windowpo_pkey PRIMARY KEY (id);


--
-- TOC entry 3581 (class 2606 OID 16797)
-- Name: windows windows_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.windows
    ADD CONSTRAINT windows_pkey PRIMARY KEY (id);


--
-- TOC entry 3553 (class 1259 OID 16612)
-- Name: ix_constants_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_constants_name ON public.constants USING btree (name);


--
-- TOC entry 3522 (class 1259 OID 16457)
-- Name: ix_enclosures_code; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_enclosures_code ON public.enclosures USING btree (code);


--
-- TOC entry 3586 (class 1259 OID 16843)
-- Name: ix_wallpo_tipo_muro; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_wallpo_tipo_muro ON public.wallpo USING btree (tipo_muro);


--
-- TOC entry 3599 (class 2606 OID 16636)
-- Name: building_conditions building_conditions_enclosure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.building_conditions
    ADD CONSTRAINT building_conditions_enclosure_id_fkey FOREIGN KEY (enclosure_id) REFERENCES public.enclosures(id);


--
-- TOC entry 3602 (class 2606 OID 16681)
-- Name: calculation_results calculation_results_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.calculation_results
    ADD CONSTRAINT calculation_results_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- TOC entry 3600 (class 2606 OID 16650)
-- Name: comunas comunas_region_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comunas
    ADD CONSTRAINT comunas_region_id_fkey FOREIGN KEY (region_id) REFERENCES public.regiones(id);


--
-- TOC entry 3597 (class 2606 OID 16607)
-- Name: constants constants_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.constants
    ADD CONSTRAINT constants_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 3606 (class 2606 OID 16728)
-- Name: details details_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.details
    ADD CONSTRAINT details_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- TOC entry 3617 (class 2606 OID 16881)
-- Name: divisions divisions_orientation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.divisions
    ADD CONSTRAINT divisions_orientation_id_fkey FOREIGN KEY (orientation_id) REFERENCES public.orientations(id);


--
-- TOC entry 3608 (class 2606 OID 16756)
-- Name: doors doors_enclosure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.doors
    ADD CONSTRAINT doors_enclosure_id_fkey FOREIGN KEY (enclosure_id) REFERENCES public.enclosures_generals(id);


--
-- TOC entry 3598 (class 2606 OID 16622)
-- Name: elements elements_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.elements
    ADD CONSTRAINT elements_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 3604 (class 2606 OID 16709)
-- Name: enclosures_generals enclosures_generals_occupation_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.enclosures_generals
    ADD CONSTRAINT enclosures_generals_occupation_profile_id_fkey FOREIGN KEY (occupation_profile_id) REFERENCES public.enclosures(id);


--
-- TOC entry 3605 (class 2606 OID 16714)
-- Name: enclosures_generals enclosures_generals_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.enclosures_generals
    ADD CONSTRAINT enclosures_generals_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- TOC entry 3616 (class 2606 OID 16867)
-- Name: floorpo floorpo_enclosure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.floorpo
    ADD CONSTRAINT floorpo_enclosure_id_fkey FOREIGN KEY (enclosure_id) REFERENCES public.enclosures_generals(id);


--
-- TOC entry 3609 (class 2606 OID 16770)
-- Name: floors floors_enclosure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.floors
    ADD CONSTRAINT floors_enclosure_id_fkey FOREIGN KEY (enclosure_id) REFERENCES public.enclosures_generals(id);


--
-- TOC entry 3603 (class 2606 OID 16695)
-- Name: formulas formulas_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.formulas
    ADD CONSTRAINT formulas_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- TOC entry 3601 (class 2606 OID 16666)
-- Name: heating_config heating_config_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.heating_config
    ADD CONSTRAINT heating_config_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- TOC entry 3612 (class 2606 OID 16812)
-- Name: orientations orientations_enclosure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orientations
    ADD CONSTRAINT orientations_enclosure_id_fkey FOREIGN KEY (enclosure_id) REFERENCES public.enclosures_generals(id);


--
-- TOC entry 3595 (class 2606 OID 16579)
-- Name: personal_access_token personal_access_token_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personal_access_token
    ADD CONSTRAINT personal_access_token_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 3596 (class 2606 OID 16593)
-- Name: projects projects_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 3610 (class 2606 OID 16784)
-- Name: roofs roofs_enclosure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roofs
    ADD CONSTRAINT roofs_enclosure_id_fkey FOREIGN KEY (enclosure_id) REFERENCES public.enclosures_generals(id);


--
-- TOC entry 3613 (class 2606 OID 16824)
-- Name: thermals_bridges_walls thermals_bridges_walls_enclosure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.thermals_bridges_walls
    ADD CONSTRAINT thermals_bridges_walls_enclosure_id_fkey FOREIGN KEY (enclosure_id) REFERENCES public.enclosures_generals(id);


--
-- TOC entry 3614 (class 2606 OID 16838)
-- Name: wallpo wallpo_enclosure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wallpo
    ADD CONSTRAINT wallpo_enclosure_id_fkey FOREIGN KEY (enclosure_id) REFERENCES public.enclosures_generals(id);


--
-- TOC entry 3607 (class 2606 OID 16742)
-- Name: walls walls_enclosure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.walls
    ADD CONSTRAINT walls_enclosure_id_fkey FOREIGN KEY (enclosure_id) REFERENCES public.enclosures_generals(id);


--
-- TOC entry 3615 (class 2606 OID 16853)
-- Name: windowpo windowpo_enclosure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.windowpo
    ADD CONSTRAINT windowpo_enclosure_id_fkey FOREIGN KEY (enclosure_id) REFERENCES public.enclosures_generals(id);


--
-- TOC entry 3611 (class 2606 OID 16798)
-- Name: windows windows_enclosure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.windows
    ADD CONSTRAINT windows_enclosure_id_fkey FOREIGN KEY (enclosure_id) REFERENCES public.enclosures_generals(id);


-- Completed on 2025-09-20 10:34:42 UTC

--
-- PostgreSQL database dump complete
--

\unrestrict B7rdqltE89wpjRPcqGzpeshwVOSM91jFNKEAmND4UT495HKfWbADopkB8hXrx4f

