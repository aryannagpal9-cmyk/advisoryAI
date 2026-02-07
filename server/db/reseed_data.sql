-- Comprehensive Reseed Script for AdvisoryAI
-- Date Range: 7th Feb 2026 to 8th Feb 2026
-- Covers all tables: clients, providers, cases, requests, audit_logs, policy_rules, client_profiles, 
-- investments, protection_policies, meetings, action_items, insights, conversations, email_drafts.

-- 1. TRUNCATE ALL TABLES (Clean Slate)
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

-- 2. INSERT POLICY RULES
INSERT INTO policy_rules (name, condition_json, action_type) VALUES
    ('High Cash Alert', '{"field": "cash_reserves", "operator": ">", "value": 50000}', 'INSIGHT'),
    ('Missing Life Cover', '{"field": "has_dependents", "operator": "==", "value": true, "has_life_cover": false}', 'RECOMMENDATION'),
    ('Rebalance Required', '{"field": "equity_drift", "operator": ">", "value": 5}', 'ALERT');

-- 3. INSERT PROVIDERS (4 Providers)
INSERT INTO providers (id, name, email, portal_url, standard_response_days) VALUES
    ('22222222-2222-2222-2222-000000000001', 'Aviva Wealth', 'transfers@aviva-wealth.co.uk', 'https://adviser.aviva.co.uk', 5),
    ('22222222-2222-2222-2222-000000000002', 'L&G Pensions', 'service@landg-pensions.com', 'https://landg.com/adviser', 7),
    ('22222222-2222-2222-2222-000000000003', 'Scottish Widows', 'ifa.support@scottishwidows.co.uk', 'https://scottishwidows.co.uk/adviser', 10),
    ('22222222-2222-2222-2222-000000000004', 'St. James''s Place', 'partner@sjp.co.uk', 'https://sjp.co.uk/adviser', 8);

-- 4. INSERT CLIENTS (12 Clients)
INSERT INTO clients (id, name, email, phone) VALUES
    ('11111111-1111-1111-1111-000000000001', 'Alexander Knight', 'alex.knight@example.com', '+44 7700 900201'),
    ('11111111-1111-1111-1111-000000000002', 'Sophia Martinez', 'sophia.m@example.com', '+44 7700 900202'),
    ('11111111-1111-1111-1111-000000000003', 'Dr. Julian Thorne', 'j.thorne@hospital.uk', '+44 7700 900203'),
    ('11111111-1111-1111-1111-000000000004', 'Eleanor Rigby', 'eleanor@rigby-consulting.com', '+44 7700 900204'),
    ('11111111-1111-1111-1111-000000000005', 'Marcus Aurelius', 'marcus.f@rome.it', '+44 7700 900205'),
    ('11111111-1111-1111-1111-000000000006', 'Isabella Swan', 'bella.swan@forks.com', '+44 7700 900206'),
    ('11111111-1111-1111-1111-000000000007', 'Thomas Shelby', 'thomas@shelby.co', '+44 7700 900207'),
    ('11111111-1111-1111-1111-000000000008', 'Diana Prince', 'diana@themyscira.gov', '+44 7700 900208'),
    ('11111111-1111-1111-1111-000000000009', 'Harvey Specter', 'harvey@pearson-hardman.com', '+44 7700 900209'),
    ('11111111-1111-1111-1111-000000000010', 'Olivia Pope', 'olivia@pope-associates.com', '+44 7700 900210'),
    ('11111111-1111-1111-1111-000000000011', 'Bruce Wayne', 'bruce@wayne-ent.com', '+44 7700 900211'),
    ('11111111-1111-1111-1111-000000000012', 'Clara Oswald', 'clara.o@tardis.org', '+44 7700 900212');

-- 5. INSERT CLIENT PROFILES
INSERT INTO client_profiles (client_id, risk_profile, time_horizon_years, retirement_target_age, retirement_income_goal, annual_income, cash_reserves, tax_year, marital_status, dependents, has_children) VALUES
    ('11111111-1111-1111-1111-000000000001', 'BALANCED', 15, 60, 50000, 120000, 85000, '2025-26', 'MARRIED', 2, TRUE),
    ('11111111-1111-1111-1111-000000000002', 'ADVENTUROUS', 20, 55, 60000, 150000, 45000, '2025-26', 'SINGLE', 0, FALSE),
    ('11111111-1111-1111-1111-000000000004', 'BALANCED', 10, 65, 40000, 95000, 30000, '2025-26', 'MARRIED', 0, TRUE),
    ('11111111-1111-1111-1111-000000000007', 'CAUTIOUS', 5, 62, 35000, 85000, 120000, '2025-26', 'MARRIED', 0, TRUE),
    ('11111111-1111-1111-1111-000000000011', 'ADVENTUROUS', 25, 60, 100000, 500000, 1000000, '2025-26', 'SINGLE', 0, FALSE);

-- 6. INSERT INVESTMENTS
INSERT INTO investments (client_id, type, provider, current_value, equity_allocation, bond_allocation, cash_allocation, annual_contribution) VALUES
    ('11111111-1111-1111-1111-000000000001', 'SIPP', 'Aviva Wealth', 450000, 60, 30, 10, 20000),
    ('11111111-1111-1111-1111-000000000001', 'STOCKS_AND_SHARES_ISA', 'Aviva Wealth', 85000, 70, 20, 10, 20000),
    ('11111111-1111-1111-1111-000000000002', 'SIPP', 'Scottish Widows', 320000, 80, 15, 5, 40000),
    ('11111111-1111-1111-1111-000000000011', 'GIA', 'St. James''s Place', 5000000, 85, 10, 5, 0);

-- 7. INSERT PROTECTION POLICIES
INSERT INTO protection_policies (client_id, type, provider, sum_assured, monthly_premium, is_active) VALUES
    ('11111111-1111-1111-1111-000000000001', 'TERM_LIFE', 'L&G Pensions', 500000, 45, TRUE),
    ('11111111-1111-1111-1111-000000000004', 'KEYMAN', 'L&G Pensions', 1000000, 120, TRUE);

-- 8. INSERT CASES (5 Active Cases)
INSERT INTO cases (id, advisor_id, client_id, title, status, created_at) VALUES
    ('33333333-3333-3333-3333-000000000001', uuid_generate_v4(), '11111111-1111-1111-1111-000000000001', 'Retirement Strategy 2026', 'ACTIVE', '2026-02-07 09:00:00+00'),
    ('33333333-3333-3333-3333-000000000002', uuid_generate_v4(), '11111111-1111-1111-1111-000000000004', 'Corporate Protection Audit', 'ACTIVE', '2026-02-07 11:00:00+00'),
    ('33333333-3333-3333-3333-000000000003', uuid_generate_v4(), '11111111-1111-1111-1111-000000000002', 'Annual ISA Strategy', 'ACTIVE', '2026-02-07 14:00:00+00'),
    ('33333333-3333-3333-3333-000000000004', uuid_generate_v4(), '11111111-1111-1111-1111-000000000007', 'Estate & IHT Planning', 'ACTIVE', '2026-02-08 10:00:00+00'),
    ('33333333-3333-3333-3333-000000000005', uuid_generate_v4(), '11111111-1111-1111-1111-000000000011', 'Quarterly Portfolio Rebalance', 'ACTIVE', '2026-02-08 13:00:00+00');


-- 9. INSERT MEETINGS (7th & 8th Feb 2026)
INSERT INTO meetings (id, client_id, case_id, meeting_type, status, title, scheduled_at, duration_minutes, completed_at, notes, transcript) VALUES
    ('44444444-4444-4444-4444-000000000001', '11111111-1111-1111-1111-000000000001', '33333333-3333-3333-3333-000000000001', 'FACT_FIND', 'COMPLETED', 'Initial Retirement Fact Find', '2026-02-07 10:00:00+00', 60, '2026-02-07 11:00:00+00', 'Discussed retirement age of 60.', 'Advisor: Hello Alex, let''s talk about your retirement...'),
    ('44444444-4444-4444-4444-000000000002', '11111111-1111-1111-1111-000000000004', '33333333-3333-3333-3333-000000000002', 'AD_HOC', 'COMPLETED', 'Keyman Protection Discussion', '2026-02-07 14:00:00+00', 45, '2026-02-07 14:45:00+00', 'Confirmed medical requirements.', 'Advisor: Eleanor, we need the business accounts...'),
    ('44444444-4444-4444-4444-000000000003', '11111111-1111-1111-1111-000000000007', '33333333-3333-3333-3333-000000000004', 'INITIAL_CONSULTATION', 'SCHEDULED', 'IHT Strategy Workshop', '2026-02-08 10:00:00+00', 90, NULL, NULL, NULL),
    ('44444444-4444-4444-4444-000000000004', '11111111-1111-1111-1111-000000000011', '33333333-3333-3333-3333-000000000005', 'ANNUAL_REVIEW', 'SCHEDULED', 'Q1 Portfolio Review', '2026-02-08 15:00:00+00', 60, NULL, NULL, NULL);

-- 10. INSERT REQUESTS (Document Requirements)
INSERT INTO requests (id, case_id, title, description, owner_type, client_owner_id, provider_owner_id, status, priority, created_at) VALUES
    ('55555555-5555-5555-5555-000000000001', '33333333-3333-3333-3333-000000000001', 'State Pension Forecast', 'Latest forecast from HMRC.', 'CLIENT', '11111111-1111-1111-1111-000000000001', NULL, 'PENDING', 'HIGH', '2026-02-07 09:30:00+00'),
    ('55555555-5555-5555-5555-000000000002', '33333333-3333-3333-3333-000000000001', 'Aviva Policy Valuation', 'Breakdown of holdings.', 'PROVIDER', NULL, '22222222-2222-2222-2222-000000000001', 'WAITING', 'STANDARD', '2026-02-07 10:00:00+00'),
    ('55555555-5555-5555-5555-000000000003', '33333333-3333-3333-3333-000000000002', 'Business Accounts', 'Audited accounts for 2 years.', 'CLIENT', '11111111-1111-1111-1111-000000000004', NULL, 'PENDING', 'CRITICAL', '2026-02-07 11:30:00+00');

-- 11. INSERT ACTION ITEMS
INSERT INTO action_items (client_id, case_id, meeting_id, title, owner, status, priority, due_date) VALUES
    ('11111111-1111-1111-1111-000000000001', '33333333-3333-3333-3333-000000000001', '44444444-4444-4444-4444-000000000001', 'Send Pension Guide', 'ADVISOR', 'COMPLETED', 'HIGH', '2026-02-07 17:00:00+00'),
    ('11111111-1111-1111-1111-000000000001', '33333333-3333-3333-3333-000000000001', NULL, 'Follow up with Aviva', 'AGENT', 'PENDING', 'MEDIUM', '2026-02-10 09:00:00+00');

-- 12. INSERT INSIGHTS
INSERT INTO insights (client_id, category, title, description, recommendation, priority, source_agent) VALUES
    ('11111111-1111-1111-1111-000000000001', 'INVESTMENT', 'Excess Cash Reserves', 'Client has £85k in cash.', 'Invest surplus.', 'MEDIUM', 'investment_agent'),
    ('11111111-1111-1111-1111-000000000011', 'OPPORTUNITY', 'Tax Efficient Gifting', 'High net worth estate.', 'Explore trust options.', 'HIGH', 'tax_agent');

-- 13. INSERT CONVERSATIONS
INSERT INTO conversations (session_id, role, content, intent, related_client_id, related_case_id) VALUES
    ('66666666-6666-6666-6666-000000000001', 'user', 'What is the status of Alex Knight''s pension review?', 'SEARCH', '11111111-1111-1111-1111-000000000001', '33333333-3333-3333-3333-000000000001'),
    ('66666666-6666-6666-6666-000000000001', 'assistant', 'The review is active. We are waiting for an Aviva valuation.', NULL, '11111111-1111-1111-1111-000000000001', '33333333-3333-3333-3333-000000000001');

-- 14. INSERT EMAIL DRAFTS
INSERT INTO email_drafts (client_id, case_id, subject, body, status, to_email, context_type) VALUES
    ('11111111-1111-1111-1111-000000000001', '33333333-3333-3333-3333-000000000001', 'Our Retirement Meeting', 'Dear Alex, great meeting you today...', 'GENERATED', 'alex.knight@example.com', 'FOLLOW_UP'),
    ('11111111-1111-1111-1111-000000000004', '33333333-3333-3333-3333-000000000002', 'Urgent: Business Accounts', 'Hi Eleanor, we need those accounts...', 'GENERATED', 'eleanor@rigby-consulting.com', 'CHASE');

-- 15. INSERT AUDIT LOGS
INSERT INTO audit_logs (request_id, case_id, action, actor, reason) VALUES
    ('55555555-5555-5555-5555-000000000002', '33333333-3333-3333-3333-000000000001', 'EMAIL_SENT', 'AGENT', 'Automatic chase sent to Aviva'),
    (NULL, '33333333-3333-3333-3333-000000000004', 'CASE_CREATED', 'Aryan Nagpal', 'Manual creation');
