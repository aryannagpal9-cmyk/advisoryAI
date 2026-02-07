-- Migration: 003_protection.sql
-- Protection policies (life insurance, income protection, etc.)

CREATE TYPE protection_type_enum AS ENUM (
    'TERM_LIFE', 'WHOLE_OF_LIFE', 'CRITICAL_ILLNESS',
    'INCOME_PROTECTION', 'FAMILY_INCOME_BENEFIT',
    'PRIVATE_MEDICAL', 'KEYMAN', 'RELEVANT_LIFE'
);

CREATE TABLE IF NOT EXISTS protection_policies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    
    -- Policy Details
    type protection_type_enum NOT NULL,
    provider TEXT NOT NULL,
    policy_number TEXT,
    
    -- Coverage
    sum_assured DECIMAL(14, 2),
    monthly_premium DECIMAL(10, 2),
    annual_premium DECIMAL(10, 2),
    
    -- Term
    start_date DATE,
    end_date DATE,
    term_years INT,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- For Income Protection
    benefit_amount DECIMAL(10, 2), -- Monthly
    deferred_period_weeks INT,
    
    -- Gaps Analysis
    income_multiple_covered DECIMAL(4, 2), -- e.g., 10x salary
    recommended_cover DECIMAL(14, 2),
    cover_gap DECIMAL(14, 2),
    
    -- Metadata
    in_trust BOOLEAN DEFAULT FALSE,
    joint_life BOOLEAN DEFAULT FALSE,
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_protection_client ON protection_policies(client_id);
CREATE INDEX idx_protection_type ON protection_policies(type);
CREATE INDEX idx_protection_active ON protection_policies(is_active);

-- Trigger for updated_at
CREATE TRIGGER protection_updated
    BEFORE UPDATE ON protection_policies
    FOR EACH ROW
    EXECUTE FUNCTION update_client_profile_timestamp();
