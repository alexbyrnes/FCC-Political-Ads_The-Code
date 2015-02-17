--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: bbox; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE bbox (
    id character varying(100),
    llx integer,
    lly integer,
    urx double precision,
    ury double precision
);


--
-- Name: contract; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE contract (
    id character varying(100),
    product character varying(255),
    advertiser character varying(255),
    advertiser_address_name character varying(255),
    advertiser_address character varying(1000),
    station_address character varying(1000),
    contract_from date,
    contract_to date,
    estimate_no character varying(100),
    billing_cycle character varying(100),
    station character varying(100),
    special_handling character varying(255),
    demographic character varying(255),
    idb_no character varying(100),
    agency_ref character varying(255),
    contract_revision character varying(100),
    billing_calendar character varying(100),
    account_executive character varying(255),
    advertiser_code character varying(100),
    print_date date,
    original_date date,
    revision_date date,
    alt_order_no character varying(100),
    advertiser_ref character varying(255),
    cash_trade character varying(100),
    sales_office character varying(255),
    product_code character varying(1000),
    page integer,
    total_pages integer,
    advertiser_address_entity character varying(1000),
    advertiser_original character varying(255),
    product_original character varying(255)
);


--
-- Name: invoice; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE invoice (
    id character varying(100),
    product character varying(255),
    advertiser character varying(255),
    advertiser_address_name character varying(255),
    advertiser_address character varying(1000),
    account_executive character varying(255),
    advertiser_code character varying(100),
    alt_order_no character varying(100),
    billing_calendar character varying(100),
    billing_type character varying(100),
    estimate_no character varying(100),
    flight_from date,
    flight_to date,
    invoice_date date,
    invoice_month character varying(100),
    invoice_no character varying(100),
    invoice_from date,
    invoice_to date,
    order_no character varying(100),
    page integer,
    total_pages integer,
    product_code character varying(1000),
    sales_office character varying(255),
    sales_region character varying(100),
    send_payment_to character varying(1000),
    station_address character varying(1000),
    station character varying(100),
    deal_no character varying(100),
    special_handling character varying(1000),
    idb_no character varying(100),
    agency_ref character varying(255),
    advertiser_ref character varying(255),
    product_original character varying(255),
    advertiser_original character varying(255),
    advertiser_address_entity character varying(1000)
);


--
-- Name: ocr; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE ocr (
    id character varying(100),
    field character varying(100),
    page integer,
    text character varying(2000),
    docformat character varying(255)
);


--
-- Name: ocr_v1; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE ocr_v1 (
    id character varying(800),
    doctype character(1),
    docformat character varying(255),
    docformat_predicted character varying(255),
    page integer
);


--
-- Name: orders; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE orders (
    id character varying(100),
    product_desc character varying(1000),
    advertiser character varying(255),
    agency_name character varying(255),
    order_revision character varying(100),
    alt_order_no character varying(100),
    estimate character varying(100),
    flight_from date,
    flight_to date,
    original_date date,
    revision_date date,
    order_type character varying(100),
    buying_contact character varying(255),
    billing_contact character varying(1000),
    demographic character varying(100),
    product_codes character varying(255),
    priority character varying(100),
    revenue_codes character varying(255),
    primary_ae character varying(255),
    sales_office character varying(255),
    sales_region character varying(100),
    billing_type character varying(100),
    billing_calendar character varying(100),
    billing_cycle character varying(25),
    agency_commission character varying(100),
    new_business_through character varying(255),
    order_separation character varying(100),
    advertiser_external_id character varying(100),
    agency_external_id character varying(100),
    page integer,
    total_pages integer,
    product_desc_original character varying(255),
    advertiser_original character varying(255)
);


--
-- Name: pageoffset; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE pageoffset (
    id character varying(100),
    field character varying(100),
    page integer,
    target_text character varying(100),
    x1 double precision,
    y1 double precision,
    x2 double precision,
    y2 double precision
);


--
-- Name: pages; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE pages (
    id character varying(100),
    pages integer
);


--
-- Name: polfile; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE polfile (
    id character varying(800),
    stationid integer,
    station character varying(100),
    year character(4),
    office character varying(100),
    type character varying(100),
    updated timestamp without time zone,
    url character varying(1024),
    doctype character(1),
    docformat character varying(255),
    urx double precision,
    ury double precision
);


--
-- Name: station; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE station (
    station character varying(10),
    updated timestamp without time zone,
    state character(2)
);


--
-- PostgreSQL database dump complete
--

