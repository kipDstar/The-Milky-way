-- ============================================
-- Digital Dairy Collection & Payment Transparency System
-- Database Schema
-- PostgreSQL 15+
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- ENUMS
-- ============================================

CREATE TYPE user_role AS ENUM ('officer', 'manager', 'admin');
CREATE TYPE quality_grade AS ENUM ('A', 'B', 'C', 'Rejected');
CREATE TYPE delivery_source AS ENUM ('mobile', 'web', 'batch');
CREATE TYPE sync_status AS ENUM ('synced', 'pending', 'conflict');
CREATE TYPE payment_status AS ENUM ('pending', 'sent', 'completed', 'failed');
CREATE TYPE sms_direction AS ENUM ('outbound', 'inbound');
CREATE TYPE sms_status AS ENUM ('queued', 'sent', 'delivered', 'failed', 'rejected');

-- ============================================
-- TABLES
-- ============================================

-- Companies/Dairy Processors
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    address TEXT,
    contact_phone VARCHAR(20),
    contact_email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Collection Stations
CREATE TABLE stations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    company_id UUID REFERENCES companies(id) ON DELETE RESTRICT,
    address TEXT,
    latitude DECIMAL(9, 6),  -- e.g., -1.286389 (Nairobi)
    longitude DECIMAL(9, 6), -- e.g., 36.817223
    contact_phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Farmers
CREATE TABLE farmers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farmer_code VARCHAR(32) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    national_id VARCHAR(50),  -- Optional, for KYC
    phone VARCHAR(20) NOT NULL,  -- E.164 format: +254712345678
    mpesa_phone VARCHAR(20),  -- May differ from primary phone
    station_id UUID REFERENCES stations(id) ON DELETE RESTRICT,
    village VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT farmer_code_format CHECK (farmer_code ~ '^[A-Z0-9\-_]{3,32}$'),
    CONSTRAINT phone_format CHECK (phone ~ '^\+[0-9]{10,15}$')
);

-- Officers/Users
CREATE TABLE officers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'officer',
    station_id UUID REFERENCES stations(id) ON DELETE RESTRICT,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret VARCHAR(255),  -- TOTP secret (encrypted)
    last_login_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Deliveries (core transaction table)
CREATE TABLE deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farmer_id UUID NOT NULL REFERENCES farmers(id) ON DELETE RESTRICT,
    station_id UUID NOT NULL REFERENCES stations(id) ON DELETE RESTRICT,
    officer_id UUID REFERENCES officers(id) ON DELETE SET NULL,
    delivery_date DATE NOT NULL,  -- Local date (YYYY-MM-DD)
    quantity_liters NUMERIC(8, 3) NOT NULL,  -- e.g., 6.800
    fat_content NUMERIC(5, 2),  -- Percentage, e.g., 3.75
    quality_grade quality_grade NOT NULL DEFAULT 'B',
    remarks TEXT,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source delivery_source DEFAULT 'mobile',
    sync_status sync_status DEFAULT 'synced',
    client_generated_id UUID,  -- For offline-first sync (client-side UUID)
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT quantity_positive CHECK (quantity_liters > 0),
    CONSTRAINT quantity_reasonable CHECK (quantity_liters <= 1000),  -- Max 1000L per delivery
    CONSTRAINT fat_content_range CHECK (fat_content IS NULL OR (fat_content >= 0 AND fat_content <= 20))
);

-- Monthly Summaries (aggregated for reporting and payment calculation)
CREATE TABLE monthly_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farmer_id UUID NOT NULL REFERENCES farmers(id) ON DELETE RESTRICT,
    month DATE NOT NULL,  -- First day of month: YYYY-MM-01
    total_liters NUMERIC(10, 3) NOT NULL DEFAULT 0,
    total_deliveries INTEGER NOT NULL DEFAULT 0,
    avg_fat_content NUMERIC(5, 2),
    grade_a_count INTEGER DEFAULT 0,
    grade_b_count INTEGER DEFAULT 0,
    grade_c_count INTEGER DEFAULT 0,
    rejected_count INTEGER DEFAULT 0,
    estimated_payment NUMERIC(12, 2),  -- KES
    currency VARCHAR(3) DEFAULT 'KES',
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_farmer_month UNIQUE (farmer_id, month)
);

-- Payments
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farmer_id UUID NOT NULL REFERENCES farmers(id) ON DELETE RESTRICT,
    monthly_summary_id UUID REFERENCES monthly_summaries(id) ON DELETE SET NULL,
    amount NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'KES',
    phone_number VARCHAR(20) NOT NULL,  -- M-Pesa phone number
    mpesa_conversation_id VARCHAR(255),  -- From M-Pesa API
    mpesa_originator_conversation_id VARCHAR(255),
    mpesa_transaction_id VARCHAR(255),  -- M-Pesa receipt number
    status payment_status DEFAULT 'pending',
    initiated_by UUID REFERENCES officers(id) ON DELETE SET NULL,
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    failure_reason TEXT,
    metadata JSONB,  -- Additional M-Pesa response data
    
    CONSTRAINT amount_positive CHECK (amount > 0)
);

-- SMS Logs (for audit and retry management)
CREATE TABLE sms_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farmer_id UUID REFERENCES farmers(id) ON DELETE SET NULL,
    delivery_id UUID REFERENCES deliveries(id) ON DELETE SET NULL,
    payment_id UUID REFERENCES payments(id) ON DELETE SET NULL,
    phone VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    direction sms_direction DEFAULT 'outbound',
    status sms_status DEFAULT 'queued',
    provider VARCHAR(50) NOT NULL,  -- 'africastalking', 'twilio', etc.
    provider_message_id VARCHAR(255),  -- Provider's message ID
    provider_status_code VARCHAR(50),
    provider_response JSONB,
    cost NUMERIC(8, 4),  -- Cost in KES
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit Logs (compliance and traceability)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(100) NOT NULL,  -- 'farmer', 'delivery', 'payment', etc.
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,  -- 'created', 'updated', 'deleted', 'approved', etc.
    actor_id UUID REFERENCES officers(id) ON DELETE SET NULL,
    actor_role user_role,
    changes JSONB,  -- JSON diff of before/after state
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Farmer Feedback
CREATE TABLE farmer_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farmer_id UUID NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,
    delivery_id UUID REFERENCES deliveries(id) ON DELETE SET NULL,
    category VARCHAR(50),  -- 'quality', 'payment', 'service', 'other'
    rating INTEGER,  -- 1-5 stars
    comment TEXT,
    source VARCHAR(50) DEFAULT 'sms',  -- 'sms', 'web', 'mobile', 'call'
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_by UUID REFERENCES officers(id) ON DELETE SET NULL,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT rating_range CHECK (rating IS NULL OR (rating >= 1 AND rating <= 5))
);

-- Refresh Tokens (for JWT refresh flow)
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    officer_id UUID NOT NULL REFERENCES officers(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL UNIQUE,  -- Hashed token for security
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP WITH TIME ZONE,
    ip_address INET,
    user_agent TEXT
);

-- OTP Codes (for two-factor authentication)
CREATE TABLE otp_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    officer_id UUID NOT NULL REFERENCES officers(id) ON DELETE CASCADE,
    code_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT otp_expires_soon CHECK (expires_at > CURRENT_TIMESTAMP)
);

-- ============================================
-- INDEXES (for query performance)
-- ============================================

-- Farmers
CREATE INDEX idx_farmers_station ON farmers(station_id);
CREATE INDEX idx_farmers_phone ON farmers(phone);
CREATE INDEX idx_farmers_active ON farmers(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_farmers_code_trgm ON farmers USING gin(farmer_code gin_trgm_ops);  -- For fuzzy search

-- Officers
CREATE INDEX idx_officers_station ON officers(station_id);
CREATE INDEX idx_officers_email ON officers(email);
CREATE INDEX idx_officers_role ON officers(role);

-- Deliveries (most queried table)
CREATE INDEX idx_deliveries_farmer ON deliveries(farmer_id);
CREATE INDEX idx_deliveries_station ON deliveries(station_id);
CREATE INDEX idx_deliveries_officer ON deliveries(officer_id);
CREATE INDEX idx_deliveries_date ON deliveries(delivery_date DESC);
CREATE INDEX idx_deliveries_farmer_date ON deliveries(farmer_id, delivery_date DESC);
CREATE INDEX idx_deliveries_station_date ON deliveries(station_id, delivery_date DESC);
CREATE INDEX idx_deliveries_recorded_at ON deliveries(recorded_at DESC);
CREATE INDEX idx_deliveries_sync_status ON deliveries(sync_status) WHERE sync_status != 'synced';
CREATE INDEX idx_deliveries_client_id ON deliveries(client_generated_id) WHERE client_generated_id IS NOT NULL;

-- Monthly Summaries
CREATE INDEX idx_monthly_summaries_farmer ON monthly_summaries(farmer_id);
CREATE INDEX idx_monthly_summaries_month ON monthly_summaries(month DESC);
CREATE INDEX idx_monthly_summaries_farmer_month ON monthly_summaries(farmer_id, month DESC);

-- Payments
CREATE INDEX idx_payments_farmer ON payments(farmer_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_requested_at ON payments(requested_at DESC);
CREATE INDEX idx_payments_mpesa_transaction ON payments(mpesa_transaction_id) WHERE mpesa_transaction_id IS NOT NULL;

-- SMS Logs
CREATE INDEX idx_sms_logs_farmer ON sms_logs(farmer_id);
CREATE INDEX idx_sms_logs_delivery ON sms_logs(delivery_id);
CREATE INDEX idx_sms_logs_status ON sms_logs(status);
CREATE INDEX idx_sms_logs_created_at ON sms_logs(created_at DESC);
CREATE INDEX idx_sms_logs_retry ON sms_logs(status, retry_count) WHERE status = 'failed';

-- Audit Logs
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_actor ON audit_logs(actor_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);

-- Feedback
CREATE INDEX idx_feedback_farmer ON farmer_feedback(farmer_id);
CREATE INDEX idx_feedback_unresolved ON farmer_feedback(is_resolved, created_at) WHERE is_resolved = FALSE;

-- Refresh Tokens
CREATE INDEX idx_refresh_tokens_officer ON refresh_tokens(officer_id);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at) WHERE is_revoked = FALSE;

-- OTP Codes
CREATE INDEX idx_otp_codes_officer ON otp_codes(officer_id);
CREATE INDEX idx_otp_codes_expires ON otp_codes(expires_at) WHERE is_used = FALSE;

-- ============================================
-- TRIGGERS (for updated_at automation)
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stations_updated_at BEFORE UPDATE ON stations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_farmers_updated_at BEFORE UPDATE ON farmers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_officers_updated_at BEFORE UPDATE ON officers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_deliveries_updated_at BEFORE UPDATE ON deliveries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_monthly_summaries_updated_at BEFORE UPDATE ON monthly_summaries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- VIEWS (for common queries)
-- ============================================

-- Daily station totals (commonly used in dashboard)
CREATE OR REPLACE VIEW daily_station_totals AS
SELECT 
    d.station_id,
    s.name AS station_name,
    d.delivery_date,
    COUNT(*) AS delivery_count,
    SUM(d.quantity_liters) AS total_liters,
    AVG(d.fat_content) AS avg_fat_content,
    COUNT(*) FILTER (WHERE d.quality_grade = 'A') AS grade_a_count,
    COUNT(*) FILTER (WHERE d.quality_grade = 'B') AS grade_b_count,
    COUNT(*) FILTER (WHERE d.quality_grade = 'C') AS grade_c_count,
    COUNT(*) FILTER (WHERE d.quality_grade = 'Rejected') AS rejected_count
FROM deliveries d
JOIN stations s ON d.station_id = s.id
GROUP BY d.station_id, s.name, d.delivery_date;

-- Farmer performance summary (last 90 days)
CREATE OR REPLACE VIEW farmer_performance_90d AS
SELECT 
    f.id AS farmer_id,
    f.farmer_code,
    f.name,
    COUNT(d.id) AS delivery_count,
    SUM(d.quantity_liters) AS total_liters,
    AVG(d.quantity_liters) AS avg_liters_per_delivery,
    AVG(d.fat_content) AS avg_fat_content,
    COUNT(*) FILTER (WHERE d.quality_grade = 'A') * 100.0 / COUNT(*) AS grade_a_percentage,
    MAX(d.delivery_date) AS last_delivery_date
FROM farmers f
LEFT JOIN deliveries d ON f.id = d.farmer_id 
    AND d.delivery_date >= CURRENT_DATE - INTERVAL '90 days'
WHERE f.is_active = TRUE
GROUP BY f.id, f.farmer_code, f.name;

-- ============================================
-- COMMENTS (documentation)
-- ============================================

COMMENT ON TABLE farmers IS 'Dairy farmers registered in the system';
COMMENT ON TABLE deliveries IS 'Daily milk deliveries with quality grading';
COMMENT ON TABLE payments IS 'M-Pesa payment transactions';
COMMENT ON TABLE sms_logs IS 'SMS communication audit trail';
COMMENT ON TABLE audit_logs IS 'Complete audit trail for compliance';

COMMENT ON COLUMN deliveries.client_generated_id IS 'UUID generated by mobile app for offline-first sync and duplicate detection';
COMMENT ON COLUMN deliveries.sync_status IS 'Sync state for offline-first mobile app';
COMMENT ON COLUMN payments.metadata IS 'Full M-Pesa API response for debugging and reconciliation';
COMMENT ON COLUMN sms_logs.retry_count IS 'Number of send attempts (for failed messages)';

-- ============================================
-- GRANTS (example, adjust for your roles)
-- ============================================

-- Create application user (used by backend service)
-- In production, create this user separately with strong password
-- CREATE USER ddcpts_app WITH PASSWORD 'secure_password_here';
-- GRANT CONNECT ON DATABASE ddcpts_prod TO ddcpts_app;
-- GRANT USAGE ON SCHEMA public TO ddcpts_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ddcpts_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ddcpts_app;

-- ============================================
-- SAMPLE DATA (for development only)
-- ============================================

-- NOTE: Use backend seed script for proper sample data generation
-- This is just a schema validation example

/*
INSERT INTO companies (name, code) VALUES ('Brookside Dairy Limited', 'BROOKSIDE');
INSERT INTO stations (name, code, company_id, address) 
VALUES ('Kipkaren Collection Centre', 'KIP001', 
    (SELECT id FROM companies WHERE code = 'BROOKSIDE'),
    'Kipkaren, Nandi County');
*/

-- ============================================
-- MAINTENANCE QUERIES (DBA reference)
-- ============================================

-- Table sizes
-- SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
-- FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Index usage
-- SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
-- FROM pg_stat_user_indexes ORDER BY idx_scan ASC;

-- Slow queries (requires pg_stat_statements extension)
-- SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 20;
