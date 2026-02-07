-- Migration: 009_seed_data.sql
-- Seed comprehensive mock data for demonstrating all features

-- Insert sample clients
INSERT INTO clients (id, name, email, phone) VALUES
    ('11111111-1111-1111-1111-111111111101', 'David Chen', 'david.chen@example.com', '+44 7700 900101'),
    ('11111111-1111-1111-1111-111111111102', 'Sarah Williams', 'sarah.williams@example.com', '+44 7700 900102'),
    ('11111111-1111-1111-1111-111111111103', 'The Gurung Family', 'roshan.gurung@example.com', '+44 7700 900103'),
    ('11111111-1111-1111-1111-111111111104', 'Michael Smith', 'michael.smith@example.com', '+44 7700 900104'),
    ('11111111-1111-1111-1111-111111111105', 'Emma Jackson', 'emma.jackson@example.com', '+44 7700 900105'),
    ('11111111-1111-1111-1111-111111111106', 'James Thompson', 'james.thompson@example.com', '+44 7700 900106'),
    ('11111111-1111-1111-1111-111111111107', 'Lisa Anderson', 'lisa.anderson@example.com', '+44 7700 900107'),
    ('11111111-1111-1111-1111-111111111108', 'Robert Wilson', 'robert.wilson@example.com', '+44 7700 900108'),
    ('11111111-1111-1111-1111-111111111109', 'Jennifer Brown', 'jennifer.brown@example.com', '+44 7700 900109'),
    ('11111111-1111-1111-1111-111111111110', 'Christopher Davis', 'chris.davis@example.com', '+44 7700 900110')
ON CONFLICT DO NOTHING;

-- Insert client profiles with varied scenarios
INSERT INTO client_profiles (client_id, risk_profile, time_horizon_years, retirement_target_age, retirement_income_goal,
    monthly_expenditure, annual_income, cash_reserves, isa_allowance_used, annual_allowance_used, tax_year,
    marital_status, dependents, has_children, children_ages, is_business_owner, business_type,
    last_review_date, next_review_due, preferences) VALUES

-- David Chen: High earner, underweight equities, needs annual review
('11111111-1111-1111-1111-111111111101', 'BALANCED', 15, 60, 50000,
 3500, 120000, 85000, 12000, 35000, '2025-26',
 'MARRIED', 2, TRUE, '[8, 12]', FALSE, NULL,
 '2024-12-01', '2025-12-01', '{"sustainable": true, "exclude_tobacco": true}'),

-- Sarah Williams: Business owner, no exit plan, good for R&D credits
('11111111-1111-1111-1111-111111111102', 'ADVENTUROUS', 20, 55, 60000,
 4000, 150000, 45000, 20000, 60000, '2025-26',
 'SINGLE', 0, FALSE, NULL, TRUE, 'Tech Consultancy',
 '2025-01-15', '2026-01-15', '{"growth_focused": true}'),

-- Gurung Family: Approaching retirement, needs long-term care planning
('11111111-1111-1111-1111-111111111103', 'CAUTIOUS', 5, 62, 40000,
 2800, 85000, 120000, 20000, 40000, '2025-26',
 'MARRIED', 0, TRUE, '[28, 25]', FALSE, NULL,
 '2024-06-15', '2025-06-15', '{"income_focused": true, "low_volatility": true}'),

-- Michael Smith: Retired, high withdrawal rate (5.2%)
('11111111-1111-1111-1111-111111111104', 'BALANCED', 25, 65, 35000,
 2900, 0, 25000, 0, 0, '2025-26',
 'MARRIED', 0, TRUE, '[35, 32]', FALSE, NULL,
 '2024-09-01', '2025-09-01', NULL),

-- Emma Jackson: Young professional, excess cash, no protection
('11111111-1111-1111-1111-111111111105', 'ADVENTUROUS', 30, 60, 55000,
 2200, 95000, 65000, 5000, 15000, '2025-26',
 'SINGLE', 0, FALSE, NULL, FALSE, NULL,
 '2024-11-01', '2025-11-01', '{"tech_sector": true}'),

-- James Thompson: HNW, no estate planning
('11111111-1111-1111-1111-111111111106', 'BALANCED', 15, 63, 80000,
 6000, 250000, 150000, 20000, 60000, '2025-26',
 'MARRIED', 3, TRUE, '[16, 14, 10]', TRUE, 'Property Development',
 '2024-08-01', '2025-08-01', NULL),

-- Lisa Anderson: Overdue review (14 months)
('11111111-1111-1111-1111-111111111107', 'CAUTIOUS', 10, 58, 30000,
 2000, 55000, 35000, 8000, 20000, '2025-26',
 'DIVORCED', 1, TRUE, '[19]', FALSE, NULL,
 '2023-12-01', '2024-12-01', NULL),

-- Robert Wilson: Children approaching university, no education planning
('11111111-1111-1111-1111-111111111108', 'BALANCED', 12, 60, 45000,
 3200, 90000, 28000, 10000, 30000, '2025-26',
 'MARRIED', 2, TRUE, '[17, 15]', FALSE, NULL,
 '2025-01-10', '2026-01-10', NULL),

-- Jennifer Brown: Birthday this month, good client relationship
('11111111-1111-1111-1111-111111111109', 'ADVENTUROUS', 18, 58, 70000,
 4500, 180000, 90000, 20000, 60000, '2025-26',
 'MARRIED', 1, TRUE, '[22]', TRUE, 'Marketing Agency',
 '2024-10-15', '2025-10-15', '{"ESG": true}'),

-- Christopher Davis: Underperforming, trajectory won't meet goals
('11111111-1111-1111-1111-111111111110', 'BALANCED', 8, 55, 50000,
 3000, 75000, 20000, 15000, 25000, '2025-26',
 'SINGLE', 0, FALSE, NULL, FALSE, NULL,
 '2024-07-01', '2025-07-01', NULL)
ON CONFLICT DO NOTHING;

-- Insert investments with various scenarios
INSERT INTO investments (client_id, type, provider, current_value, equity_allocation, bond_allocation, 
    cash_allocation, withdrawal_rate, annual_contribution) VALUES

-- David Chen: Underweight equities (30% vs 60% target for BALANCED)
('11111111-1111-1111-1111-111111111101', 'SIPP', 'Aviva', 450000, 30, 50, 20, NULL, 20000),
('11111111-1111-1111-1111-111111111101', 'STOCKS_AND_SHARES_ISA', 'AJ Bell', 85000, 35, 40, 25, NULL, 20000),

-- Sarah Williams: Growth focused
('11111111-1111-1111-1111-111111111102', 'SIPP', 'Scottish Widows', 320000, 80, 15, 5, NULL, 40000),
('11111111-1111-1111-1111-111111111102', 'STOCKS_AND_SHARES_ISA', 'Hargreaves Lansdown', 120000, 85, 10, 5, NULL, 20000),

-- Gurung Family: Conservative, preparing for retirement
('11111111-1111-1111-1111-111111111103', 'SIPP', 'Aviva', 680000, 40, 45, 15, NULL, 10000),
('11111111-1111-1111-1111-111111111103', 'STOCKS_AND_SHARES_ISA', 'Vanguard', 95000, 35, 50, 15, NULL, 20000),

-- Michael Smith: Retired with 5.2% withdrawal (above 4% sustainable)
('11111111-1111-1111-1111-111111111104', 'SIPP', 'Standard Life', 550000, 50, 40, 10, 5.2, 0),
('11111111-1111-1111-1111-111111111104', 'STOCKS_AND_SHARES_ISA', 'Fidelity', 80000, 45, 45, 10, NULL, 0),

-- Emma Jackson: Excess cash (65k vs 13k needed for 6 months)
('11111111-1111-1111-1111-111111111105', 'WORKPLACE_PENSION', 'Nest', 45000, 70, 25, 5, NULL, 9500),
('11111111-1111-1111-1111-111111111105', 'STOCKS_AND_SHARES_ISA', 'Nutmeg', 25000, 75, 20, 5, NULL, 5000),

-- James Thompson: HNW portfolio
('11111111-1111-1111-1111-111111111106', 'SIPP', 'AJ Bell', 890000, 55, 35, 10, NULL, 60000),
('11111111-1111-1111-1111-111111111106', 'STOCKS_AND_SHARES_ISA', 'Interactive Investor', 250000, 60, 30, 10, NULL, 20000),
('11111111-1111-1111-1111-111111111106', 'GIA', 'Charles Stanley', 450000, 50, 35, 15, NULL, 50000),

-- Lisa Anderson: Modest portfolio, overdue review
('11111111-1111-1111-1111-111111111107', 'PERSONAL_PENSION', 'Legal & General', 180000, 40, 50, 10, NULL, 8000),
('11111111-1111-1111-1111-111111111107', 'CASH_ISA', 'Nationwide', 35000, 0, 0, 100, NULL, 8000),

-- Robert Wilson: Standard portfolio
('11111111-1111-1111-1111-111111111108', 'SIPP', 'Fidelity', 280000, 55, 35, 10, NULL, 15000),
('11111111-1111-1111-1111-111111111108', 'STOCKS_AND_SHARES_ISA', 'Vanguard', 65000, 60, 30, 10, NULL, 10000),

-- Jennifer Brown: High performer
('11111111-1111-1111-1111-111111111109', 'SIPP', 'Quilter', 520000, 70, 25, 5, NULL, 40000),
('11111111-1111-1111-1111-111111111109', 'STOCKS_AND_SHARES_ISA', 'Hargreaves Lansdown', 180000, 75, 20, 5, NULL, 20000),

-- Christopher Davis: Underperforming trajectory
('11111111-1111-1111-1111-111111111110', 'SIPP', 'Aviva', 120000, 50, 40, 10, NULL, 10000),
('11111111-1111-1111-1111-111111111110', 'STOCKS_AND_SHARES_ISA', 'AJ Bell', 35000, 55, 35, 10, NULL, 5000)
ON CONFLICT DO NOTHING;

-- Insert protection policies (some with gaps)
INSERT INTO protection_policies (client_id, type, provider, sum_assured, monthly_premium, is_active, 
    income_multiple_covered, recommended_cover, cover_gap) VALUES

-- David Chen: Has protection
('11111111-1111-1111-1111-111111111101', 'TERM_LIFE', 'Legal & General', 500000, 45, TRUE, 4.2, 600000, 100000),
('11111111-1111-1111-1111-111111111101', 'CRITICAL_ILLNESS', 'Vitality', 200000, 65, TRUE, NULL, NULL, NULL),

-- Sarah Williams: No protection (gap)
-- (no entries)

-- Gurung Family: Income protection
('11111111-1111-1111-1111-111111111103', 'INCOME_PROTECTION', 'Aviva', NULL, 85, TRUE, NULL, NULL, NULL),

-- Emma Jackson: No protection despite single with mortgage
-- (no entries)

-- James Thompson: Keyman for business
('11111111-1111-1111-1111-111111111106', 'TERM_LIFE', 'Royal London', 1000000, 120, TRUE, 4.0, 1250000, 250000),
('11111111-1111-1111-1111-111111111106', 'KEYMAN', 'Zurich', 500000, 95, TRUE, NULL, NULL, NULL)
ON CONFLICT DO NOTHING;

-- Insert meetings with various scenarios
INSERT INTO meetings (client_id, meeting_type, status, title, scheduled_at, completed_at, notes, 
    topics_discussed, risk_discussions, recommendations_made, client_concerns, follow_up_required) VALUES

-- David Chen: Recent meeting with follow-up needed
('11111111-1111-1111-1111-111111111101', 'ANNUAL_REVIEW', 'COMPLETED', 'Annual Review 2024', 
 '2024-12-01 10:00:00+00', '2024-12-01 11:30:00+00',
 'Discussed portfolio performance and rebalancing. David expressed concerns about market volatility affecting his retirement plans.',
 '["retirement_planning", "portfolio_review", "risk_assessment"]',
 'Reviewed risk profile - David comfortable with BALANCED approach but wants to reduce volatility as he approaches 50. Discussed moving from 60% to 50% equity over next 2 years.',
 '[{"type": "rebalance", "detail": "Reduce equity to 50% by Q2 2025"}, {"type": "review", "detail": "Check Scottish Widows transfer progress"}]',
 '["market_volatility", "pension_consolidation_timeline"]',
 TRUE),

-- Williams Family: Discussed sustainable investing
('11111111-1111-1111-1111-111111111102', 'AD_HOC', 'COMPLETED', 'Sustainable Investment Discussion',
 '2025-01-15 14:00:00+00', '2025-01-15 15:00:00+00',
 'Sarah wants to align her portfolio with ESG principles. Discussed various sustainable fund options.',
 '["sustainable_investing", "ESG", "fund_selection"]',
 NULL,
 '[{"type": "fund_switch", "detail": "Move to ESG-focused funds in ISA"}]',
 '["greenwashing_concerns"]',
 FALSE),

-- Upcoming meeting scheduled
('11111111-1111-1111-1111-111111111103', 'ANNUAL_REVIEW', 'SCHEDULED', 'Gurung Family Annual Review',
 '2025-02-15 11:00:00+00', NULL, NULL,
 '["retirement_planning", "long_term_care"]', NULL, NULL, NULL, FALSE)
ON CONFLICT DO NOTHING;

-- Insert action items
INSERT INTO action_items (client_id, title, description, owner, status, due_date, priority, category, promised_at, promise_context) VALUES

-- David Chen follow-ups
('11111111-1111-1111-1111-111111111101', 'Send rebalancing proposal', 
 'Prepare detailed rebalancing proposal to reduce equity from 60% to 50%',
 'ADVISOR', 'PENDING', '2025-02-10 17:00:00+00', 'HIGH', 'DOCUMENT',
 '2024-12-01 11:30:00+00', 'Promised to send within 2 weeks of meeting'),

('11111111-1111-1111-1111-111111111101', 'Chase Scottish Widows transfer',
 'Follow up on pension transfer progress from Scottish Widows to AJ Bell',
 'ADVISOR', 'IN_PROGRESS', '2025-02-05 17:00:00+00', 'MEDIUM', 'CALL',
 NULL, NULL),

-- Overdue item for Lisa Anderson
('11111111-1111-1111-1111-111111111107', 'Schedule overdue annual review',
 'Client review is 2 months overdue - need to schedule urgently for compliance',
 'ADVISOR', 'OVERDUE', '2025-01-15 17:00:00+00', 'URGENT', 'ADMIN',
 NULL, NULL),

-- Emma Jackson: Waiting on client
('11111111-1111-1111-1111-111111111105', 'Awaiting proof of address',
 'Client to provide utility bill for platform account opening',
 'CLIENT', 'PENDING', '2025-02-08 17:00:00+00', 'MEDIUM', 'DOCUMENT',
 NULL, NULL),

-- James Thompson: Estate planning
('11111111-1111-1111-1111-111111111106', 'Prepare estate planning summary',
 'HNW client with no estate planning - prepare IHT analysis and trust options',
 'ADVISOR', 'PENDING', '2025-02-20 17:00:00+00', 'HIGH', 'RESEARCH',
 NULL, NULL)
ON CONFLICT DO NOTHING;

-- Insert some insights
INSERT INTO insights (client_id, category, title, description, recommendation, priority, query_type, source_agent, metrics, affected_value) VALUES

('11111111-1111-1111-1111-111111111101', 'INVESTMENT', 
 'Portfolio Underweight in Equities',
 'David Chen''s portfolio is at 32% equities vs 60% target for his BALANCED risk profile and 15-year time horizon.',
 'Consider phased rebalancing to increase equity allocation while managing sequence risk.',
 'MEDIUM', 'equity_analysis', 'investment_agent',
 '{"current_equity": 32, "target_equity": 60, "gap": 28}', NULL),

('11111111-1111-1111-1111-111111111104', 'RISK_ALERT',
 'Withdrawal Rate Above Sustainable Level',
 'Michael Smith is withdrawing at 5.2% annually, above the 4% sustainable withdrawal rate guideline.',
 'Review income needs and consider reducing withdrawal or adjusting asset allocation.',
 'HIGH', 'withdrawal_analysis', 'investment_agent',
 '{"current_rate": 5.2, "sustainable_rate": 4.0, "fund_value": 550000}', 6600),

('11111111-1111-1111-1111-111111111107', 'COMPLIANCE',
 'Annual Review Overdue',
 'Lisa Anderson has not had an annual review in 14 months. Compliance requires reviews within 12 months.',
 'Contact client urgently to schedule review meeting.',
 'CRITICAL', 'review_check', 'compliance_agent',
 '{"months_since_review": 14, "required_frequency": 12}', NULL),

('11111111-1111-1111-1111-111111111105', 'OPPORTUNITY',
 'Excess Cash Above Emergency Buffer',
 'Emma Jackson has £65,000 cash reserves vs £13,200 needed (6 months expenditure). £51,800 could be invested.',
 'Discuss maximising ISA allowance and longer-term investment options.',
 'MEDIUM', 'cash_analysis', 'investment_agent',
 '{"cash_reserves": 65000, "required_buffer": 13200, "excess": 51800}', 51800),

('11111111-1111-1111-1111-111111111106', 'OPPORTUNITY',
 'Estate Planning Gap for HNW Client',
 'James Thompson has £1.59M in investments with no estate planning in place. Potential IHT liability significant.',
 'Schedule estate planning review to discuss trusts, gifts, and IHT mitigation strategies.',
 'HIGH', 'estate_planning', 'proactive_agent',
 '{"total_assets": 1590000, "nil_rate_band": 325000, "potential_iht": 506000}', 506000),

('11111111-1111-1111-1111-111111111102', 'OPPORTUNITY',
 'R&D Tax Credit Opportunity',
 'Sarah Williams runs a Tech Consultancy and may be eligible for R&D tax credits under recent scheme changes.',
 'Discuss R&D tax credit eligibility and refer to specialist accountant if needed.',
 'MEDIUM', 'business_opportunity', 'proactive_agent',
 '{"business_type": "Tech Consultancy", "revenue_estimate": null}', NULL),

('11111111-1111-1111-1111-111111111108', 'RELATIONSHIP',
 'Education Planning Needed',
 'Robert Wilson has children aged 17 and 15 approaching university but no education funding in place.',
 'Discuss Junior ISA, regular savings, or other education funding strategies.',
 'MEDIUM', 'life_event', 'proactive_agent',
 '{"children_ages": [17, 15], "years_to_uni": [1, 3]}', NULL)
ON CONFLICT DO NOTHING;
