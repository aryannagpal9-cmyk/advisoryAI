# AdvisoryAI Server (Core Engine)

The AdvisoryAI backend is a robust FastAPI application that serves as the orchestration layer between the React frontend, the Supabase database, and the autonomous agentic core.

## 🛠 Core Responsibilities

1. **API Gateway**: REST and WebSocket endpoints for the dashboard.
2. **State Management**: Managing the lifecycle of Cases and Requests in PostgreSQL.
3. **Agentic Orchestration**: Interfacing with the Smart Agent via MCP.
4. **Time Simulation**: The "Advance Day" engine for processing automated chases.

## 📂 Architecture & Directory Structure

- `main.py`: Entry point, middleware (CORS, Error Handling), and router registration.
- **[`routes/`](file:///Users/aryannagpal/Documents/advisoryAI/server/routes)**:
    - `api.py`: Core CRUD for cases, requests, and dashboard stats.
    - `websockets.py`: Real-time state updates to the frontend.
- **[`agent_mcp/`](file:///Users/aryannagpal/Documents/advisoryAI/server/agent_mcp)**:
    - `server.py`: The FastMCP server hosting tools.
    - `tools/`: Atomic tool definitions (Email, Search, DB operations).
- **[`services/`](file:///Users/aryannagpal/Documents/advisoryAI/server/services)**:
    - `llm_service.py`: High-speed interface to Groq/Llama 3.3.
    - `logging_service.py`: Structured JSON logging for observability.
- **[`db/`](file:///Users/aryannagpal/Documents/advisoryAI/server/db)**:
    - `supabase.py`: Client initialization and raw query wrappers.
    - `schema.sql`: The source of truth for the database structure.

## 📡 API Specification

### Case Management
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/cases` | `GET` | List all active cases with recent request status. |
| `/api/cases` | `POST` | Create a new case and initialize child requests. |
| `/api/cases/{id}` | `GET` | Fetch granular details, including audit logs. |
| `/api/cases/priority`| `GET` | Fetch cases flagged as "High" or "Critical". |

### Automation & Simulation
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/simulate/advance-day` | `POST` | Advances the system time and triggers the agentic chase policy. |
| `/api/requests/{id}/chase` | `POST` | Manually trigger an immediate follow-up for a request. |
| `/api/requests/{id}/resolve`| `POST` | Mark a request as FULFILLED and notify the case owner. |

## 🤖 MCP Tool Layer

The server hosts a Model Context Protocol (MCP) server that exposes the following tools to the agent:

- **`fetch_overdue_requests`**: Returns a list of requests where `next_action_at < current_time`.
- **`dispatch_chase_email`**: Generates a context-aware follow-up email via SendGrid.
- **`update_request_state`**: Updates DB status and increments retry counters.
- **`log_audit_event`**: Records the rationale for an agent action.

## 🚀 Setup & Development

1. **Environment**:
   ```bash
   cp .env.example .env
   # Ensure SUPABASE_URL, SUPABASE_KEY, and GROQ_API_KEY are set.
   ```

2. **Installation**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Execution**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

4. **Documentation**:
   Interactive Swagger docs are available at `http://localhost:8000/docs`.
