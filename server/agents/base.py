"""
Agent Base Class and Shared Utilities
Common functionality for all specialized agents.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AgentType(Enum):
    INVESTMENT = "investment"
    PROACTIVE = "proactive"
    COMPLIANCE = "compliance"
    BUSINESS = "business"
    FOLLOWUP = "followup"
    CHAT = "chat"


class QueryIntent(Enum):
    # Investment queries
    EQUITY_ANALYSIS = "equity_analysis"
    ISA_ALLOWANCE = "isa_allowance"
    ANNUAL_ALLOWANCE = "annual_allowance"
    CASH_EXCESS = "cash_excess"
    RETIREMENT_TRAJECTORY = "retirement_trajectory"
    PROTECTION_GAPS = "protection_gaps"
    WITHDRAWAL_RATE = "withdrawal_rate"
    INTEREST_RATE_IMPACT = "interest_rate_impact"
    LONG_TERM_CARE = "long_term_care"
    MARKET_CORRECTION = "market_correction"
    EARLY_RETIREMENT = "early_retirement"
    
    # Proactive queries
    OVERDUE_REVIEW = "overdue_review"
    BUSINESS_OPPORTUNITY = "business_opportunity"
    EDUCATION_PLANNING = "education_planning"
    SIMILAR_PROFILES = "similar_profiles"
    ESTATE_PLANNING = "estate_planning"
    CASHFLOW_SERVICE = "cashflow_service"
    NO_PROTECTION = "no_protection"
    EXIT_PLANNING = "exit_planning"
    BIRTHDAYS = "birthdays"
    
    # Compliance queries
    RECOMMENDATION_HISTORY = "recommendation_history"
    RISK_DISCUSSION = "risk_discussion"
    PLATFORM_RECOMMENDATIONS = "platform_recommendations"
    VOLATILITY_CONCERNS = "volatility_concerns"
    SUSTAINABLE_INVESTING = "sustainable_investing"
    PENDING_DOCUMENTS = "pending_documents"
    PROMISED_ITEMS = "promised_items"
    
    # Business queries
    CLIENT_CONCERNS = "client_concerns"
    SERVICE_UTILIZATION = "service_utilization"
    CONVERSION_RATES = "conversion_rates"
    RETIREMENT_BOOK = "retirement_book"
    REVENUE_ANALYSIS = "revenue_analysis"
    SATISFIED_CLIENTS = "satisfied_clients"
    RECOMMENDATION_PUSHBACK = "recommendation_pushback"
    VALUE_ADDED = "value_added"
    LIFE_EVENT_TRIGGERS = "life_event_triggers"
    
    # Follow-up queries
    DRAFT_EMAIL = "draft_email"
    WAITING_INFO = "waiting_info"
    OPEN_ACTIONS = "open_actions"
    OVERDUE_FOLLOWUPS = "overdue_followups"
    
    # Action intents
    SEND_EMAIL = "send_email"
    CREATE_TASK = "create_task"
    SCHEDULE_MEETING = "schedule_meeting"
    CREATE_CASE = "create_case"
    
    # General
    SEARCH = "search"
    UNKNOWN = "unknown"


@dataclass
class AgentQuery:
    """Structured query for agents to process."""
    raw_query: str
    intent: QueryIntent
    entities: Dict[str, Any]  # Extracted entities (client names, dates, etc.)
    context: Dict[str, Any]  # Session context
    

@dataclass
class AgentResponse:
    """Structured response from agents."""
    success: bool
    data: Any
    message: str
    agent_type: AgentType
    query_type: QueryIntent
    metadata: Optional[Dict[str, Any]] = None
    follow_up_suggestions: Optional[List[str]] = None


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(self, supabase, llm_service):
        self.supabase = supabase
        self.llm = llm_service
        
    @property
    @abstractmethod
    def agent_type(self) -> AgentType:
        """Return the type of this agent."""
        pass
    
    @property
    @abstractmethod
    def supported_intents(self) -> List[QueryIntent]:
        """Return list of intents this agent can handle."""
        pass
    
    @abstractmethod
    async def process(self, query: AgentQuery) -> AgentResponse:
        """Process a query and return response."""
        pass
        
    async def generate_all_insights(self) -> List[Dict[str, Any]]:
        """Generate proactive insights (optional override)."""
        return []
        
    async def evaluate_and_act(self, simulated_now: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Autonomous Loop: Evaluate current state and take actions.
        Returns a list of actions taken (e.g. {"action": "EMAIL_SENT", "details": ...})
        """
        return []
    
    def can_handle(self, intent: QueryIntent) -> bool:
        """Check if this agent can handle the given intent."""
        return intent in self.supported_intents
    
    async def _execute_query(self, table: str, select: str = "*", filters: dict = None) -> List[dict]:
        """Helper to execute Supabase queries."""
        query = self.supabase.table(table).select(select)
        if filters:
            for key, value in filters.items():
                if isinstance(value, dict):
                    op = value.get("op", "eq")
                    val = value.get("value")
                    if op == "gt":
                        query = query.gt(key, val)
                    elif op == "lt":
                        query = query.lt(key, val)
                    elif op == "gte":
                        query = query.gte(key, val)
                    elif op == "lte":
                        query = query.lte(key, val)
                    elif op == "in":
                        query = query.in_(key, val)
                    elif op == "like":
                        query = query.like(key, val)
                    elif op == "ilike":
                        query = query.ilike(key, val)
                else:
                    query = query.eq(key, value)
        result = query.execute()
        return result.data if result.data else []
