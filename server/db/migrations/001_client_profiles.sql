-- Migration: 001_client_profiles.sql
-- Extends the client data model with rich financial profile data

-- Risk profile enum
CREATE TYPE risk_profile_enum AS ENUM ('CAUTIOUS', 'BALANCED', 'ADVENTUROUS', 'AGGRESSIVE');

-- Client profiles table for detailed financial data
CREATE TABLE IF NOT EXISTS client_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE UNIQUE,
    
    -- Risk and Investment Profile
    risk_profile risk_profile_enum DEFAULT 'BALANCED',
    time_horizon_years INT,
    investment_experience TEXT, -- 'NOVICE', 'INTERMEDIATE', 'EXPERIENCED'
    
    -- Goals and Targets
    retirement_target_age INT,
    retirement_income_goal DECIMAL(12, 2),
    state_pension_age INT,
    
    -- Current Financial Position
    monthly_expenditure DECIMAL(12, 2),
    annual_income DECIMAL(12, 2),
    cash_reserves DECIMAL(12, 2),
    emergency_fund_months INT DEFAULT 6,
    
    -- Allowances and Tax Planning
    isa_allowance_used DECIMAL(12, 2) DEFAULT 0,
    annual_allowance_used DECIMAL(12, 2) DEFAULT 0,
    tax_year TEXT, -- e.g., '2025-26'
    
    -- Family and Protection
    marital_status TEXT, -- 'SINGLE', 'MARRIED', 'DIVORCED', 'WIDOWED'
    dependents INT DEFAULT 0,
    has_children BOOLEAN DEFAULT FALSE,
    children_ages JSONB, -- Array of ages
    
    -- Business Ownership
    is_business_owner BOOLEAN DEFAULT FALSE,
    business_type TEXT,
    has_exit_plan BOOLEAN,
    
    -- Compliance Tracking
    last_review_date TIMESTAMPTZ,
    next_review_due TIMESTAMPTZ,
    review_frequency_months INT DEFAULT 12,
    
    -- Notes and Metadata
    preferences JSONB, -- Sustainability preferences, etc.
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster lookups
CREATE INDEX idx_client_profiles_client_id ON client_profiles(client_id);
CREATE INDEX idx_client_profiles_review_due ON client_profiles(next_review_due);
CREATE INDEX idx_client_profiles_risk ON client_profiles(risk_profile);

-- Trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_client_profile_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER client_profiles_updated
    BEFORE UPDATE ON client_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_client_profile_timestamp();
