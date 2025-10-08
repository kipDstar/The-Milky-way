-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- stations
CREATE TABLE IF NOT EXISTS stations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name varchar(255) NOT NULL,
  company varchar(255),
  address text,
  latitude decimal(9,6),
  longitude decimal(9,6),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- farmers
CREATE TABLE IF NOT EXISTS farmers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  farmer_code varchar(32) UNIQUE NOT NULL,
  name varchar(255) NOT NULL,
  national_id varchar(50),
  phone varchar(20) NOT NULL,
  station_id uuid REFERENCES stations(id),
  is_active boolean DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT farmer_code_format CHECK (farmer_code ~ '^[A-Z0-9\-_]{3,32}$')
);

-- officers (users)
DO $$ BEGIN
  CREATE TYPE user_role AS ENUM ('officer','manager','admin');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
CREATE TABLE IF NOT EXISTS officers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name varchar(255) NOT NULL,
  email varchar(255) UNIQUE,
  phone varchar(20),
  station_id uuid REFERENCES stations(id),
  role user_role NOT NULL,
  password_hash text NOT NULL,
  two_factor_enabled boolean DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- deliveries
DO $$ BEGIN
  CREATE TYPE quality_grade AS ENUM ('A','B','C','Rejected');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
  CREATE TYPE source_type AS ENUM ('mobile','web','batch');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
  CREATE TYPE sync_status AS ENUM ('synced','pending','conflict');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
CREATE TABLE IF NOT EXISTS deliveries (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  farmer_id uuid NOT NULL REFERENCES farmers(id),
  station_id uuid NOT NULL REFERENCES stations(id),
  officer_id uuid REFERENCES officers(id),
  delivery_date date NOT NULL,
  quantity_liters numeric(8,3) NOT NULL CHECK (quantity_liters > 0 AND quantity_liters <= 200),
  fat_content numeric(5,2),
  quality_grade quality_grade NOT NULL,
  remarks text,
  recorded_at timestamptz NOT NULL DEFAULT now(),
  source source_type NOT NULL DEFAULT 'mobile',
  sync_status sync_status NOT NULL DEFAULT 'synced'
);

-- monthly_summaries
CREATE TABLE IF NOT EXISTS monthly_summaries (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  farmer_id uuid NOT NULL REFERENCES farmers(id),
  month char(7) NOT NULL, -- YYYY-MM
  total_liters numeric(12,3) NOT NULL DEFAULT 0,
  estimated_payment numeric(14,2) NOT NULL DEFAULT 0,
  currency char(3) NOT NULL DEFAULT 'KES',
  generated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (farmer_id, month)
);

-- payments
DO $$ BEGIN
  CREATE TYPE payment_status AS ENUM ('pending','sent','failed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
CREATE TABLE IF NOT EXISTS payments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  farmer_id uuid NOT NULL REFERENCES farmers(id),
  amount numeric(14,2) NOT NULL CHECK (amount >= 0),
  currency char(3) NOT NULL DEFAULT 'KES',
  mpesa_transaction_id varchar(128),
  status payment_status NOT NULL DEFAULT 'pending',
  requested_at timestamptz NOT NULL DEFAULT now(),
  completed_at timestamptz
);

-- sms_logs
DO $$ BEGIN
  CREATE TYPE sms_direction AS ENUM ('outbound','inbound');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
  CREATE TYPE sms_status AS ENUM ('queued','sent','delivered','failed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
CREATE TABLE IF NOT EXISTS sms_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  farmer_id uuid REFERENCES farmers(id),
  message text NOT NULL,
  direction sms_direction NOT NULL,
  status sms_status NOT NULL,
  provider varchar(64),
  provider_id varchar(128),
  sent_at timestamptz DEFAULT now()
);

-- audit_logs
CREATE TABLE IF NOT EXISTS audit_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  entity_type varchar(64) NOT NULL,
  entity_id uuid,
  action varchar(64) NOT NULL,
  actor_id uuid,
  actor_role user_role,
  changes jsonb,
  timestamp timestamptz NOT NULL DEFAULT now()
);

-- indexes
CREATE INDEX IF NOT EXISTS idx_deliveries_farmer_date ON deliveries (farmer_id, delivery_date);
CREATE INDEX IF NOT EXISTS idx_deliveries_station_date ON deliveries (station_id, delivery_date);
CREATE INDEX IF NOT EXISTS idx_monthly_summaries_month ON monthly_summaries (month);
