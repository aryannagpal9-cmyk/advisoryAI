# AdvisoryAI: Technical Requirements Document (TRD)

## 1. System Architecture

AdvisoryAI follows an asynchronous, event-driven pattern where a stateless FastAPI frontend orchestrates a stateful background lifecycle via the Model Context Protocol (MCP).

### 1.1 High-Level Logical Diagram
```mermaid
graph LR
    subgraph "Frontend Layer"
        UI[React SPA] <--> API[FastAPI Gateway]
        API <--> WS[WebSocket Hub]
    end

    subgraph "Agentic Layer (MCP)"
        Agent[Smart Agent]
        MCPServer[FastMCP Tool Server]
        Agent <--> MCPServer
    end

    subgraph "Resource Layer"
        DB[(Supabase/Postgres)]
        Email[Postmark Service]
        LLM[Groq Llama 3.3]
    end

    API <--> Agent
    MCPServer <--> DB
    MCPServer <--> Email
    MCPServer <--> LLM
```

---

## 2. Data Model & Schema

The system uses a normalized PostgreSQL schema (managed via Supabase) to track the lifecycle of cases and requests.

### 2.1 Entity Relationship Diagram (ERD)
```mermaid
erDiagram
    CLIENT ||--o{ CASE : "involved in"
    PROVIDER ||--o{ REQUEST : "fulfills"
    CASE ||--o{ REQUEST : "contains"
    REQUEST ||--o{ AUDIT_LOG : "generates"
    
    CLIENT {
        uuid id PK
        string name
        string email
        string phone
    }

    CASE {
        uuid id PK
        uuid advisor_id
        uuid client_id FK
        string title
        string status
    }

    REQUEST {
        uuid id PK
        uuid case_id FK
        string title
        enum status
        enum owner_type
        uuid client_owner_id FK
        uuid provider_owner_id FK
        int retry_count
        timestamp next_action_at
    }

    AUDIT_LOG {
        uuid id PK
        uuid request_id FK
        string action
        string actor
        string reason
        jsonb metadata
    }
```

---

## 3. The "Automated Chase" Lifecycle

### 3.1 Lifecycle Sequence
```mermaid
sequenceDiagram
    participant S as Scheduler
    participant B as Backend
    participant A as Smart Agent
    participant M as MCP Server
    participant E as Postmark

    S->>B: Trigger Simulation / Interval
    B->>M: fetch_pending_requests(current_time)
    M-->>B: List[Requests]
    
    loop for each request
        B->>A: analyze_and_execute(request_context)
        A->>M: send_chase_email(request_id)
        M->>E: POST /email
        M->>M: update_status(status=WAITING, retry_count++)
        M->>M: log_audit(action=EMAIL_SENT)
    end
```

---

## 4. API & Integration Design

### 4.1 MCP Tools (FastMCP)
The MCP server exposes a standard interface for the agent to interact with the world:
- `get_overdue_requests`: Queries DB for items past their `next_action_at`.
- `send_followup`: Orchestrates email creation and status updates.
- `validate_document`: Basic heuristic check for uploaded files.

### 4.2 Security & Transports
- **Auth**: JWT-based authentication for the FastAPI gateway.
- **Transports**: Standard SSE (Server-Sent Events) or HTTP for MCP communication.
- **Uploads**: Requests generate a signed `upload_token` used as a magic link for clients.

---

## 5. Deployment & Observability

- **Containerization**: Multi-stage Docker builds for Python (Backend) and Node.js (Frontend).
- **Logging**: Level-based structured logging (filtering out PII).
- **Monitoring**: Health check endpoints at `/api/health`.
