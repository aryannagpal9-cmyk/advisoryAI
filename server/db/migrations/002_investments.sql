-- Migration: 002_investments.sql
-- Investment and portfolio tracking

-- Investment type enum
CREATE TYPE investment_type_enum AS ENUM (
    'ISA', 'STOCKS_AND_SHARES_ISA', 'CASH_ISA', 'LIFETIME_ISA',
    'PERSONAL_PENSION', 'WORKPLACE_PENSION', 'SIPP', 
    'GIA', 'BOND', 'VCT', 'EIS',
    'PROPERTY', 'CASH'
);

-- Investment wrapper/account table
CREATE TABLE IF NOT EXISTS investments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    
    -- Investment Details
    type investment_type_enum NOT NULL,
    provider TEXT NOT NULL, -- 'Aviva', 'AJ Bell', 'Scottish Widows', etc.
    account_reference TEXT,
    product_name TEXT,
    
    -- Valuation
    current_value DECIMAL(14, 2) NOT NULL DEFAULT 0,
    last_valuation_date TIMESTAMPTZ DEFAULT NOW(),
    
    -- Asset Allocation (percentages)
    equity_allocation DECIMAL(5, 2) DEFAULT 0, -- 0-100
    bond_allocation DECIMAL(5, 2) DEFAULT 0,
    cash_allocation DECIMAL(5, 2) DEFAULT 0,
    property_allocation DECIMAL(5, 2) DEFAULT 0,
    alternative_allocation DECIMAL(5, 2) DEFAULT 0,
    
    -- For Pensions
    crystallised BOOLEAN DEFAULT FALSE,
    drawdown_active BOOLEAN DEFAULT FALSE,
    annuity_purchased BOOLEAN DEFAULT FALSE,
    
    -- For Active Drawdown/Income
    withdrawal_rate DECIMAL(5, 2), -- Annual as percentage of fund
    annual_withdrawal DECIMAL(12, 2),
    sustainable_withdrawal_rate DECIMAL(5, 2) DEFAULT 4.0,
    
    -- Contributions
    annual_contribution DECIMAL(12, 2) DEFAULT 0,
    employer_contribution DECIMAL(12, 2) DEFAULT 0,
    
    -- Metadata
    fund_names JSONB, -- Array of underlying fund names
    risk_rating INT, -- 1-10 scale
    charges_percent DECIMAL(4, 2),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_investments_client ON investments(client_id);
CREATE INDEX idx_investments_type ON investments(type);
CREATE INDEX idx_investments_provider ON investments(provider);

-- Trigger for updated_at
CREATE TRIGGER investments_updated
    BEFORE UPDATE ON investments
    FOR EACH ROW
    EXECUTE FUNCTION update_client_profile_timestamp();
