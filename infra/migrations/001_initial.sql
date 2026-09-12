-- PostgreSQL/PostGIS foundation for the production persistence adapter.
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE TABLE IF NOT EXISTS land_parcel (
  id uuid PRIMARY KEY,
  ulpin text UNIQUE,
  survey_number text,
  plot_number text,
  state text NOT NULL,
  district text,
  tehsil text,
  village text,
  area numeric,
  area_unit text,
  normalized_area_sqm numeric,
  geometry geometry(Geometry, 4326),
  geometry_source text,
  authoritative_source text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS document (
  id uuid PRIMARY KEY,
  parcel_id uuid REFERENCES land_parcel(id),
  document_type text NOT NULL,
  storage_key text NOT NULL UNIQUE,
  sha256 char(64) NOT NULL,
  file_size bigint NOT NULL,
  source text NOT NULL,
  uploaded_by uuid,
  uploaded_at timestamptz NOT NULL DEFAULT now(),
  version integer NOT NULL,
  parent_document_id uuid REFERENCES document(id),
  processing_status text NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_event (
  id bigserial PRIMARY KEY,
  actor_id uuid,
  action text NOT NULL,
  entity_type text NOT NULL,
  entity_id text NOT NULL,
  timestamp timestamptz NOT NULL DEFAULT now(),
  before_state jsonb,
  after_state jsonb,
  reason text,
  trace_id uuid NOT NULL
);
