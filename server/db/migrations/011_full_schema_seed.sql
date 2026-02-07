-- Migration: 011_full_schema_seed.sql
-- Comprehensive seed data for ALL tables in the schema
-- Use this to fully populate the application with interconnected demo data.

-- 1. TRUNCATE ALL TABLES (Clean Slate) ---------------------------------------
TRUNCATE TABLE audit_logs CASCADE;
TRUNCATE TABLE action_items CASCADE;
TRUNCATE TABLE requests CASCADE;
TRUNCATE TABLE meetings CASCADE;
TRUNCATE TABLE email_drafts CASCADE;
TRUNCATE TABLE conversations CASCADE;
TRUNCATE TABLE insights CASCADE;
TRUNCATE TABLE protection_policies CASCADE;
TRUNCATE TABLE investments CASCADE;
TRUNCATE TABLE client_profiles CASCADE;
TRUNCATE TABLE cases CASCADE;
TRUNCATE TABLE providers CASCADE;
TRUNCATE TABLE clients CASCADE;
TRUNCATE TABLE policy_rules CASCADE;

-- 2. INSERT INDEPENDENT DATA ------------------------------------------------

-- PROVIDERS
INSERT INTO providers (id, name, email, portal_url, standard_response_days) VALUES
    ('22222222-2222-2222-2222-222222222201', 'Aviva', 'intermediary@aviva.co.uk', 'https://adviser.aviva.co.uk', 5),
    ('22222222-2222-2222-2222-222222222202', 'Legal & General', 'service@landg.com', 'https://landgAdapter.com', 7),
    ('22222222-2222-2222-2222-222222222203', 'Scottish Widows', 'ifa.support@scottishwidows.co.uk', 'https://scottishwidows.co.uk/adviser', 10),
    ('22222222-2222-2222-2222-222222222204', 'AJ Bell', 'transfers@ajbell.co.uk', 'https://ajbell.co.uk/adviser', 3),
    ('22222222-2222-2222-2222-222222222205', 'Vitality', 'adviser@vitality.co.uk', 'https://vitality.co.uk/adviser', 5);

-- POLICY RULES
INSERT INTO policy_rules (name, condition_json, action_type) VALUES
    ('High Equity Warning', '{"field": "equity_allocation", "operator": ">", "value": 80, "risk_profile": "CAUTIOUS"}', 'ALERT'),
    ('Pension Annual Allowance Check', '{"field": "annual_contribution", "operator": ">", "value": 60000}', 'FLAG'),
    ('Missing Protection Warning', '{"field": "has_mortgage", "operator": "==", "value": true, "protection_check": "none"}', 'RECOMMENDATION');

-- CLIENTS (Same as before)
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
    ('11111111-1111-1111-1111-111111111110', 'Christopher Davis', 'chris.davis@example.com', '+44 7700 900110');


-- 3. INSERT DEPENDENT DATA (Layer 1) ---------------------------------------

-- CLIENT PROFILES (Same as before)
INSERT INTO client_profiles (client_id, risk_profile, time_horizon_years, retirement_target_age, retirement_income_goal,
    monthly_expenditure, annual_income, cash_reserves, isa_allowance_used, annual_allowance_used, tax_year,
    marital_status, dependents, has_children, children_ages, is_business_owner, business_type,
    last_review_date, next_review_due, preferences) VALUES
('11111111-1111-1111-1111-111111111101', 'BALANCED', 15, 60, 50000, 3500, 120000, 85000, 12000, 35000, '2025-26', 'MARRIED', 2, TRUE, '[8, 12]', FALSE, NULL, '2024-12-01', '2025-12-01', '{"sustainable": true}'),
('11111111-1111-1111-1111-111111111102', 'ADVENTUROUS', 20, 55, 60000, 4000, 150000, 45000, 20000, 60000, '2025-26', 'SINGLE', 0, FALSE, NULL, TRUE, 'Tech Consultancy', '2025-01-15', '2026-01-15', '{"growth_focused": true}'),
('11111111-1111-1111-1111-111111111103', 'CAUTIOUS', 5, 62, 40000, 2800, 85000, 120000, 20000, 40000, '2025-26', 'MARRIED', 0, TRUE, '[28, 25]', FALSE, NULL, '2024-06-15', '2025-06-15', '{"income_focused": true}'),
('11111111-1111-1111-1111-111111111104', 'BALANCED', 25, 65, 35000, 2900, 0, 25000, 0, 0, '2025-26', 'MARRIED', 0, TRUE, '[35, 32]', FALSE, NULL, '2024-09-01', '2025-09-01', NULL),
('11111111-1111-1111-1111-111111111105', 'ADVENTUROUS', 30, 60, 55000, 2200, 95000, 65000, 5000, 15000, '2025-26', 'SINGLE', 0, FALSE, NULL, FALSE, NULL, '2024-11-01', '2025-11-01', '{"tech_sector": true}'),
('11111111-1111-1111-1111-111111111106', 'BALANCED', 15, 63, 80000, 6000, 250000, 150000, 20000, 60000, '2025-26', 'MARRIED', 3, TRUE, '[16, 14, 10]', TRUE, 'Property Development', '2024-08-01', '2025-08-01', NULL),
('11111111-1111-1111-1111-111111111107', 'CAUTIOUS', 10, 58, 30000, 2000, 55000, 35000, 8000, 20000, '2025-26', 'DIVORCED', 1, TRUE, '[19]', FALSE, NULL, '2023-12-01', '2024-12-01', NULL),
('11111111-1111-1111-1111-111111111108', 'BALANCED', 12, 60, 45000, 3200, 90000, 28000, 10000, 30000, '2025-26', 'MARRIED', 2, TRUE, '[17, 15]', FALSE, NULL, '2025-01-10', '2026-01-10', NULL),
('11111111-1111-1111-1111-111111111109', 'ADVENTUROUS', 18, 58, 70000, 4500, 180000, 90000, 20000, 60000, '2025-26', 'MARRIED', 1, TRUE, '[22]', TRUE, 'Marketing Agency', '2024-10-15', '2025-10-15', '{"ESG": true}'),
('11111111-1111-1111-1111-111111111110', 'BALANCED', 8, 55, 50000, 3000, 75000, 20000, 15000, 25000, '2025-26', 'SINGLE', 0, FALSE, NULL, FALSE, NULL, '2024-07-01', '2025-07-01', NULL);

-- CASES (New Table!)
INSERT INTO cases (id, advisor_id, client_id, title, status, created_at) VALUES
    ('33333333-3333-3333-3333-333333333301', uuid_generate_v4(), '11111111-1111-1111-1111-111111111101', 'Pension Consolidation - David Chen', 'ACTIVE', NOW() - INTERVAL '30 days'),
    ('33333333-3333-3333-3333-333333333302', uuid_generate_v4(), '11111111-1111-1111-1111-111111111106', 'IHT Planning - James Thompson', 'ACTIVE', NOW() - INTERVAL '10 days'),
    ('33333333-3333-3333-3333-333333333303', uuid_generate_v4(), '11111111-1111-1111-1111-111111111102', 'Business Protection Review', 'COMPLETED', NOW() - INTERVAL '60 days');

-- INVESTMENTS (Same as before)
INSERT INTO investments (client_id, type, provider, current_value, equity_allocation, bond_allocation, cash_allocation, withdrawal_rate, annual_contribution) VALUES
('11111111-1111-1111-1111-111111111101', 'SIPP', 'Aviva', 450000, 30, 50, 20, NULL, 20000),
('11111111-1111-1111-1111-111111111101', 'STOCKS_AND_SHARES_ISA', 'AJ Bell', 85000, 35, 40, 25, NULL, 20000),
('11111111-1111-1111-1111-111111111102', 'SIPP', 'Scottish Widows', 320000, 80, 15, 5, NULL, 40000),
('11111111-1111-1111-1111-111111111102', 'STOCKS_AND_SHARES_ISA', 'AJ Bell', 120000, 85, 10, 5, NULL, 20000), -- Changed provider to match seeded providers
('11111111-1111-1111-1111-111111111103', 'SIPP', 'Aviva', 680000, 40, 45, 15, NULL, 10000),
('11111111-1111-1111-1111-111111111104', 'SIPP', 'Legal & General', 550000, 50, 40, 10, 5.2, 0);

-- PROTECTION POLICIES (Same as before)
INSERT INTO protection_policies (client_id, type, provider, sum_assured, monthly_premium, is_active, income_multiple_covered, recommended_cover, cover_gap) VALUES
('11111111-1111-1111-1111-111111111101', 'TERM_LIFE', 'Legal & General', 500000, 45, TRUE, 4.2, 600000, 100000),
('11111111-1111-1111-1111-111111111101', 'CRITICAL_ILLNESS', 'Vitality', 200000, 65, TRUE, NULL, NULL, NULL),
('11111111-1111-1111-1111-111111111106', 'KEYMAN', 'Vitality', 500000, 95, TRUE, NULL, NULL, NULL);

-- 4. INSERT DEPENDENT DATA (Layer 2) ---------------------------------------

-- MEETINGS
INSERT INTO meetings (id, client_id, case_id, meeting_type, status, title, scheduled_at, completed_at, notes, recommendations_made) VALUES
    ('44444444-4444-4444-4444-444444444401', '11111111-1111-1111-1111-111111111101', '33333333-3333-3333-3333-333333333301', 'ANNUAL_REVIEW', 'COMPLETED', 'Pension Review', '2024-12-01 10:00:00+00', '2024-12-01 11:30:00+00', 'Discussed consolidating pensions.', '[{"type": "consolidation", "detail": "Move old pots to SIPP"}]'),
    ('44444444-4444-4444-4444-444444444402', '11111111-1111-1111-1111-111111111102', '33333333-3333-3333-3333-333333333303', 'AD_HOC', 'COMPLETED', 'Business Protection', '2025-01-15 14:00:00+00', '2025-01-15 15:00:00+00', 'Discussed Keyman insurance.', NULL);

-- REQUESTS (New Table!)
INSERT INTO requests (id, case_id, title, description, owner_type, provider_owner_id, status, created_at) VALUES
    ('55555555-5555-5555-5555-555555555501', '33333333-3333-3333-3333-333333333301', 'Letter of Authority - Aviva', 'Requesting policy details', 'PROVIDER', '22222222-2222-2222-2222-222222222201', 'FULFILLED', NOW() - INTERVAL '20 days'),
    ('55555555-5555-5555-5555-555555555502', '33333333-3333-3333-3333-333333333301', 'Transfer Forms - AJ Bell', 'Application for transfer', 'PROVIDER', '22222222-2222-2222-2222-222222222204', 'PENDING', NOW() - INTERVAL '5 days');

-- INSIGHTS
INSERT INTO insights (client_id, category, title, description, recommendation, priority, source_agent, metrics) VALUES
('11111111-1111-1111-1111-111111111101', 'INVESTMENT', 'Portfolio Underweight in Equities', 'Description...', 'Rebalance', 'MEDIUM', 'investment_agent', '{"gap": 28}'),
('11111111-1111-1111-1111-111111111104', 'RISK_ALERT', 'Withdrawal Rate Warning', 'Description...', 'Reduce withdrawal', 'HIGH', 'investment_agent', '{"rate": 5.2}');


-- 5. INSERT DEPENDENT DATA (Layer 3) ---------------------------------------

-- ACTION ITEMS (Linked to cases/meetings)
INSERT INTO action_items (client_id, case_id, meeting_id, title, owner, status, priority, due_date) VALUES
    ('11111111-1111-1111-1111-111111111101', '33333333-3333-3333-3333-333333333301', '44444444-4444-4444-4444-444444444401', 'Send LOA to Aviva', 'ADVISOR', 'COMPLETED', 'HIGH', NOW() - INTERVAL '15 days'),
    ('11111111-1111-1111-1111-111111111101', '33333333-3333-3333-3333-333333333301', NULL, 'Chase transfer packs', 'ADVISOR', 'PENDING', 'MEDIUM', NOW() + INTERVAL '2 days');

-- EMAIL DRAFTS
INSERT INTO email_drafts (client_id, case_id, meeting_id, subject, body, to_email, status, created_at) VALUES
    ('11111111-1111-1111-1111-111111111101', '33333333-3333-3333-3333-333333333301', '44444444-4444-4444-4444-444444444401', 'Follow up: Pension Consolidation', 'Dear David...', 'david.chen@example.com', 'GENERATED', NOW());

-- CONVERSATIONS
INSERT INTO conversations (session_id, role, content, intent, related_client_id, related_case_id) VALUES
    (uuid_generate_v4(), 'user', 'What is the status of David Chen''s transfer?', 'search', '11111111-1111-1111-1111-111111111101', '33333333-3333-3333-3333-333333333301'),
    (uuid_generate_v4(), 'assistant', 'The transfer is currently pending with AJ Bell.', NULL, '11111111-1111-1111-1111-111111111101', '33333333-3333-3333-3333-333333333301');

-- AUDIT LOGS (New Table!)
INSERT INTO audit_logs (request_id, case_id, action, actor, reason) VALUES
    ('55555555-5555-5555-5555-555555555501', '33333333-3333-3333-3333-333333333301', 'STATUS_CHANGE', 'SYSTEM', 'Provider portal updated'),
    (NULL, '33333333-3333-3333-3333-333333333301', 'CASE_CREATED', 'Aryan Nagpal', 'New client instruction');

