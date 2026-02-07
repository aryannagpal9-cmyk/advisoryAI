-- Migration: 007_conversations.sql
-- Chat history for AI assistant context

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL, -- Groups messages in a session
    
    -- Message Content
    role TEXT NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    
    -- Context and Metadata
    intent TEXT, -- Classified intent
    entities JSONB, -- Extracted entities (client names, dates, etc.)
    agent_used TEXT, -- Which agent handled this
    
    -- Related Records
    related_client_id UUID REFERENCES clients(id),
    related_case_id UUID REFERENCES cases(id),
    
    -- Response Metadata
    tokens_used INT,
    response_time_ms INT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_conversations_created ON conversations(created_at DESC);
CREATE INDEX idx_conversations_client ON conversations(related_client_id);

-- View for getting recent conversation context
CREATE OR REPLACE VIEW recent_conversation_context AS
SELECT 
    session_id,
    json_agg(
        json_build_object(
            'role', role,
            'content', content,
            'created_at', created_at
        ) ORDER BY created_at
    ) as messages
FROM conversations
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY session_id;
