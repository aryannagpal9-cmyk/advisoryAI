"""
Agent Orchestrator
Central coordinator that routes queries to specialized agents.
"""
from typing import Dict, Any, List, Optional, Tuple
from uuid import uuid4
import re
from datetime import datetime

from .base import (
    AgentType, QueryIntent, AgentQuery, AgentResponse, BaseAgent
)
from services.llm_service import GroqService
from db.supabase import get_supabase
from services.logging_service import get_logger

logger = get_logger(__name__)


# Intent classification patterns for fast matching
INTENT_PATTERNS = {
    # Investment patterns
    QueryIntent.EQUITY_ANALYSIS: [
        r"underweight.*equit", r"equity.*allocation", r"risk.*profile.*equit"
    ],
    QueryIntent.ISA_ALLOWANCE: [
        r"isa\s*allowance", r"isa.*available", r"remaining.*isa"
    ],
    QueryIntent.ANNUAL_ALLOWANCE: [
        r"annual\s*allowance", r"pension.*allowance", r"aa.*available"
    ],
    QueryIntent.CASH_EXCESS: [
        r"cash.*excess", r"excess.*cash", r"cash.*above", r"surplus.*cash"
    ],
    QueryIntent.RETIREMENT_TRAJECTORY: [
        r"trajectory", r"retirement.*goal", r"won'?t\s*meet", r"shortfall"
    ],
    QueryIntent.PROTECTION_GAPS: [
        r"protection.*gap", r"no.*protection", r"life.*insurance.*need"
    ],
    QueryIntent.WITHDRAWAL_RATE: [
        r"withdrawal.*rate", r"more than.*4%", r"drawdown.*rate", r"sustainable.*withdrawal"
    ],
    QueryIntent.INTEREST_RATE_IMPACT: [
        r"interest.*rate", r"rate.*drop", r"rate.*impact"
    ],
    QueryIntent.LONG_TERM_CARE: [
        r"long.?term.*care", r"care.*cost", r"nursing.*home"
    ],
    QueryIntent.MARKET_CORRECTION: [
        r"market.*correction", r"20%.*drop", r"market.*crash", r"downturn"
    ],
    QueryIntent.EARLY_RETIREMENT: [
        r"early.*retire", r"retire.*early", r"retire.*next.*year"
    ],
    
    # Proactive patterns
    QueryIntent.OVERDUE_REVIEW: [
        r"review.*overdue", r"haven'?t.*review", r"12.*month", r"annual.*review.*due"
    ],
    QueryIntent.BUSINESS_OPPORTUNITY: [
        r"business.*owner", r"r&d.*tax", r"tax.*credit"
    ],
    QueryIntent.EDUCATION_PLANNING: [
        r"university", r"education.*plan", r"children.*approaching"
    ],
    QueryIntent.SIMILAR_PROFILES: [
        r"similar.*profile", r"like.*the\s+\w+s", r"same.*situation"
    ],
    QueryIntent.ESTATE_PLANNING: [
        r"estate.*plan", r"iht", r"inheritance", r"high.?net.?worth.*no.*estate"
    ],
    QueryIntent.EXIT_PLANNING: [
        r"exit.*plan", r"sell.*business", r"business.*succession"
    ],
    QueryIntent.BIRTHDAYS: [
        r"birthday.*this.*month", r"birthdays", r"client.*birthday"
    ],
    
    # Compliance patterns
    QueryIntent.RECOMMENDATION_HISTORY: [
        r"recommendation.*made", r"what.*recommend", r"rationale"
    ],
    QueryIntent.RISK_DISCUSSION: [
        r"risk.*discussion", r"exact.*wording", r"what.*said.*risk"
    ],
    QueryIntent.PLATFORM_RECOMMENDATIONS: [
        r"platform\s*x", r"recommended.*platform", r"which.*platform"
    ],
    QueryIntent.VOLATILITY_CONCERNS: [
        r"volatility.*concern", r"worried.*market", r"concern.*volatility"
    ],
    QueryIntent.SUSTAINABLE_INVESTING: [
        r"sustainable.*invest", r"esg", r"ethical.*invest"
    ],
    QueryIntent.PENDING_DOCUMENTS: [
        r"document.*waiting", r"pending.*document", r"still.*waiting"
    ],
    QueryIntent.PROMISED_ITEMS: [
        r"promise.*send", r"committed.*to", r"what.*promise"
    ],
    
    # Action patterns
    QueryIntent.SEND_EMAIL: [
        r"email", r"send\s+a\s+message", r"draft\s+an\s+email", r"write.*to.*client"
    ],
    QueryIntent.CREATE_TASK: [
        r"create\s+task", r"set\s+a\s+reminder", r"remind\s+me", r"add\s+to\s+do", r"task.*for"
    ],
    QueryIntent.SCHEDULE_MEETING: [
        r"schedule\s+meeting", r"book\s+a\s+call", r"set\s+up\s+a\s+time", r"meeting.*with"
    ],
    QueryIntent.CREATE_CASE: [
        r"create\s+case", r"new\s+case", r"start\s+a\s+case", r"open\s+a\s+case"
    ],
    
    # Business analytics patterns
    QueryIntent.CLIENT_CONCERNS: [
        r"concerns.*raised", r"client.*concerns", r"issues.*this.*month"
    ],
    QueryIntent.CONVERSION_RATES: [
        r"conversion.*rate", r"referral.*source", r"initial.*meeting"
    ],
    QueryIntent.RETIREMENT_BOOK: [
        r"approaching.*retirement", r"next.*5.*years", r"percentage.*book"
    ],
    QueryIntent.REVENUE_ANALYSIS: [
        r"revenue", r"highest.*value", r"most.*profitable"
    ],
    
    # Follow-up patterns
    QueryIntent.DRAFT_EMAIL: [
        r"draft.*email", r"write.*email", r"compose.*email", r"follow.?up.*email"
    ],
    QueryIntent.WAITING_INFO: [
        r"waiting.*on", r"waiting.*for.*info", r"pending.*from.*client"
    ],
    QueryIntent.OPEN_ACTIONS: [
        r"open.*action", r"action.*item", r"to.?do", r"task.*list"
    ],
    QueryIntent.OVERDUE_FOLLOWUPS: [
        r"overdue.*follow", r"overdue.*commit", r"missed.*deadline"
    ],
    
    # General
    QueryIntent.SEARCH: [
        r"find", r"search", r"show.*me", r"list"
    ]
}


class AgentOrchestrator:
    """
    Central orchestrator that:
    1. Classifies user intent
    2. Routes to appropriate agent(s)
    3. Aggregates and formats responses
    4. Maintains conversation context
    """
    
    def __init__(self):
        self.supabase = get_supabase()
        self.llm = GroqService()
        self.agents: Dict[AgentType, BaseAgent] = {}
        self._register_agents()
        
    def _register_agents(self):
        """Register all specialized agents."""
        from .investment_agent import InvestmentAgent
        from .proactive_agent import ProactiveAgent
        from .compliance_agent import ComplianceAgent
        from .business_agent import BusinessAgent
        from .followup_agent import FollowupAgent
        
        self.agents[AgentType.INVESTMENT] = InvestmentAgent(self.supabase, self.llm)
        self.agents[AgentType.PROACTIVE] = ProactiveAgent(self.supabase, self.llm)
        self.agents[AgentType.COMPLIANCE] = ComplianceAgent(self.supabase, self.llm)
        self.agents[AgentType.BUSINESS] = BusinessAgent(self.supabase, self.llm)
        self.agents[AgentType.FOLLOWUP] = FollowupAgent(self.supabase, self.llm)
    
    def _classify_intent_regex(self, query: str) -> Optional[QueryIntent]:
        """Fast regex-based intent classification."""
        query_lower = query.lower()
        
        for intent, patterns in INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent
        return None
    
    async def _classify_intent_llm(self, query: str) -> Tuple[QueryIntent, Dict[str, Any]]:
        """LLM-based intent classification for complex queries."""
        system_prompt = """You are an intent classifier for a financial advisor assistant.
        
Classify the user's query into ONE of these categories:

INVESTMENT QUERIES:
- EQUITY_ANALYSIS: Questions about equity allocation vs risk profile
- ISA_ALLOWANCE: Questions about ISA allowance remaining
- ANNUAL_ALLOWANCE: Questions about pension annual allowance
- CASH_EXCESS: Questions about excess cash above emergency fund
- RETIREMENT_TRAJECTORY: Questions about meeting retirement goals
- PROTECTION_GAPS: Questions about missing protection/insurance
- WITHDRAWAL_RATE: Questions about retiree withdrawal rates
- MARKET_CORRECTION: Questions about impact of market drops

PROACTIVE QUERIES:
- OVERDUE_REVIEW: Questions about clients needing reviews
- BUSINESS_OPPORTUNITY: Questions about business owner opportunities
- EDUCATION_PLANNING: Questions about children/university planning
- ESTATE_PLANNING: Questions about inheritance/IHT planning
- BIRTHDAYS: Questions about client birthdays
- CREATE_CASE: Requests to create/open a new case

COMPLIANCE QUERIES:
- RECOMMENDATION_HISTORY: Questions about past recommendations
- RISK_DISCUSSION: Questions about documented risk discussions
- PENDING_DOCUMENTS: Questions about outstanding documents

FOLLOW-UP QUERIES:
- DRAFT_EMAIL: Requests to draft/write emails
- SEND_EMAIL: Requests to officially send an email
- OPEN_ACTIONS: Questions about action items/tasks
- CREATE_TASK: Requests to create a new task/reminder
- SCHEDULE_MEETING: Requests to book/schedule a meeting
- OVERDUE_FOLLOWUPS: Questions about overdue commitments

BUSINESS QUERIES:
- CLIENT_CONCERNS: Questions about client concerns raised
- REVENUE_ANALYSIS: Questions about revenue/client value

ENTITY EXTRACTION:
- client_name: Extract the name of the client mentioned.
- case_title: If creating a case, what is the subject?
- task_title: If creating a task, what is the description?
- meeting_title: If scheduling a meeting, what is it about?
- subject/body: If drafting/sending email, what are the details?

Respond in JSON format:
{"intent": "INTENT_NAME", "entities": {"client_name": "...", "case_title": "...", "task_title": "...", "meeting_title": "...", "subject": "...", "body": "..."}}
"""
        try:
            response = self.llm.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            intent_str = result.get("intent", "UNKNOWN")
            entities = result.get("entities", {})
            
            try:
                intent = QueryIntent[intent_str]
            except KeyError:
                intent = QueryIntent.UNKNOWN
                
            return intent, entities
            
        except Exception as e:
            logger.error(f"LLM intent classification failed: {e}")
            return QueryIntent.UNKNOWN, {}
    
    def _find_agent_for_intent(self, intent: QueryIntent) -> Optional[BaseAgent]:
        """Find the agent that can handle the given intent."""
        for agent in self.agents.values():
            if agent.can_handle(intent):
                return agent
        return None
    
    async def _extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities like client names from query."""
        entities = {}
        
        # Simple client name extraction patterns
        client_patterns = [
            r"(?:for|with|to)\s+(?:the\s+)?(\w+(?:\s+\w+)?(?:\s+family)?)",
            r"(\w+(?:'s|s'))\s+(?:portfolio|account|case)",
            r"(?:client\s+)?(\w+\s+\w+)(?:\s+and|\s+who|\s+has|\s+is)"
        ]
        
        for pattern in client_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                entities["client_name"] = match.group(1).strip()
                break
        
        return entities
    
    async def process_query(
        self, 
        raw_query: str, 
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Main entry point for processing user queries.
        
        1. Classify intent (regex first, then LLM if needed)
        2. Extract entities
        3. Route to appropriate agent
        4. Store conversation
        5. Return response
        """
        session_id = session_id or str(uuid4())
        context = context or {}
        
        # Step 1: Fast regex classification
        intent = self._classify_intent_regex(raw_query)
        entities = {}
        
        # Step 2: Fall back to LLM if regex didn't match
        if intent is None:
            intent, entities = await self._classify_intent_llm(raw_query)
        else:
            entities = await self._extract_entities(raw_query)
        
        logger.info(f"Query classified as {intent.value} with entities {entities}")
        
        # Step 3: Build structured query
        agent_query = AgentQuery(
            raw_query=raw_query,
            intent=intent,
            entities=entities,
            context=context
        )
        
        # Step 4: Find and invoke agent
        agent = self._find_agent_for_intent(intent)
        
        if agent is None:
            # No specific agent, use general response
            return AgentResponse(
                success=False,
                data=None,
                message="I'm not sure how to help with that query. Could you rephrase it or be more specific?",
                agent_type=AgentType.CHAT,
                query_type=intent,
                follow_up_suggestions=[
                    "Show me clients needing annual reviews",
                    "Which clients have protection gaps?",
                    "Draft a follow-up email for my last meeting"
                ]
            )
        
        # Step 5: Process with the appropriate agent
        try:
            response = await agent.process(agent_query)
        except Exception as e:
            logger.error(f"Agent processing failed: {e}")
            response = AgentResponse(
                success=False,
                data=None,
                message=f"Error processing your query: {str(e)}",
                agent_type=agent.agent_type,
                query_type=intent
            )
        
        # Step 6: Store conversation
        await self._store_conversation(session_id, raw_query, response, intent, entities)
        
        return response
    
    async def _store_conversation(
        self,
        session_id: str,
        query: str,
        response: AgentResponse,
        intent: QueryIntent,
        entities: Dict[str, Any]
    ):
        """Store conversation in database for context."""
        try:
            # Store user message
            self.supabase.table("conversations").insert({
                "session_id": session_id,
                "role": "user",
                "content": query,
                "intent": intent.value,
                "entities": entities
            }).execute()
            
            # Store assistant response
            self.supabase.table("conversations").insert({
                "session_id": session_id,
                "role": "assistant",
                "content": response.message,
                "agent_used": response.agent_type.value
            }).execute()
        except Exception as e:
            logger.warning(f"Failed to store conversation: {e}")
    
    async def generate_insights(self) -> List[Dict[str, Any]]:
        """Generate proactive insights across all agents."""
        all_insights = []
        
        # Trigger each agent's insight generation
        proactive_agent = self.agents.get(AgentType.PROACTIVE)
        if proactive_agent:
            insights = await proactive_agent.generate_all_insights()
            all_insights.extend(insights)
        
        investment_agent = self.agents.get(AgentType.INVESTMENT)
        if investment_agent:
            insights = await investment_agent.generate_all_insights()
            all_insights.extend(insights)
        
        compliance_agent = self.agents.get(AgentType.COMPLIANCE)
        if compliance_agent:
            insights = await compliance_agent.generate_all_insights()
            all_insights.extend(insights)
        
        return all_insights

    async def run_autonomous_loop(self, simulated_now: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Trigger all agents to evaluate state and take autonomous actions.
        Returns a log of actions taken.
        """
        all_actions = []
        now = simulated_now or datetime.now()
        logger.info(f"Starting autonomous agent loop (SimDate: {now})...")
        
        for agent_type, agent in self.agents.items():
            try:
                actions = await agent.evaluate_and_act(simulated_now=now)
                if actions:
                    for action in actions:
                        action["agent"] = agent_type.value
                    all_actions.extend(actions)
            except Exception as e:
                logger.error(f"Error in autonomous loop for agent {agent_type.value}: {e}")
                
        return all_actions


# Singleton instance
_orchestrator: Optional[AgentOrchestrator] = None

def get_orchestrator() -> AgentOrchestrator:
    """Get or create the orchestrator singleton."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator
