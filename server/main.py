import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load env vars
load_dotenv()

from routes.api import router as api_router
from routes.websockets import router as ws_router
from routes.webhooks import router as webhook_router
from agent_mcp.server import mcp 
from services.logging_service import setup_logging, get_logger
from middleware.error_handler import ErrorHandlerMiddleware

# Configure Logging
setup_logging()
logger = get_logger(__name__)

# Create the MCP App (Streamable HTTP)
# We use the transport requested by the user
mcp_app = mcp.http_app(transport="streamable-http")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Manage the lifespan of the MCP app
    # FastMCP's 'http_app' returns a Starlette app that has a .lifespan property context manager
    # We need to enter it.
    async with mcp_app.lifespan(app) as _:
        logger.info("Agentic Chaser Backend + MCP Server Started")
        yield
        logger.info("Agentic Chaser Backend Stopped")

app = FastAPI(lifespan=lifespan)

# Mount Route Handlers First
app.include_router(api_router, prefix="/api")
app.include_router(ws_router)
app.include_router(webhook_router)

# Error Handler - Catch all app/unhandled exceptions
app.add_middleware(ErrorHandlerMiddleware)

# CORS (Allow Frontend) - Outer layer to ensure headers on error responses
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount MCP Server
# Using /sse as the base path as requested for streamable http endpoints
app.mount("/sse", mcp_app)

@app.get("/")
def read_root():
    return {"status": "Agent Online", "mode": "Deterministic Policy Engine + FastMCP Host"}
