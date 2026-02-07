from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID
from models.domain import Request, RequestStatus, RequestPriority, ActionAttempt, OwnerType

class PolicyEvaluator:
    """
    Stateless, Deterministic Policy Engine.
    Input: Request State + Current Time
    Output: Action (or None)
    """
    
    def evaluate(self, request: Request, current_time: datetime) -> Optional[ActionAttempt]:
        # Rule 0: If blocked or closed, do nothing
        if request.status in [RequestStatus.ESCALATED, RequestStatus.FULFILLED, RequestStatus.PAUSED, RequestStatus.CLOSED]:
            return None

        # Rule 1: Escalation on Max Retries
        if request.retry_count >= request.max_retries:
            return ActionAttempt(
                action_type="ESCALATE",
                request_id=request.id,
                reason=f"Max retries ({request.max_retries}) reached without fulfillment.",
                metadata={"urgency": request.priority}
            )

        # Rule 2: Escalation on Time + Urgency
        # e.g. High Priority items escalate faster
        time_elapsed = current_time - request.created_at
        if request.priority == RequestPriority.CRITICAL and time_elapsed.days > 14:
             return ActionAttempt(
                action_type="ESCALATE",
                request_id=request.id,
                reason="Critical request outstanding for >14 days.",
                metadata={"time_elapsed_days": time_elapsed.days}
            )

        # Rule 3: Routine Chasing (The Bread and Butter)
        if current_time >= request.next_action_at:
            return self._determine_chase_action(request)

        return None

    def _determine_chase_action(self, request: Request) -> ActionAttempt:
        """Determines the specific chase action (Email Client vs Provider)"""
        
        # Logic to choose template based on owner
        target = "Client" if request.owner_type == OwnerType.CLIENT else "Provider"
        phase = f"Reminder {request.retry_count + 1}"
        
        return ActionAttempt(
            action_type="SEND_REMINDER",
            request_id=request.id,
            reason=f"Scheduled chase due: {target} {phase}",
            metadata={
                "template": f"{target.lower()}_chase_level_{request.retry_count + 1}",
                "target_email": "lookup_needed" # In a real implementation, we'd have the email here or look it up
            }
        )

    def calculate_next_chase_time(self, request: Request) -> datetime:
        """Calculates the delay for the NEXT chase based on provider profiles or defaults"""
        # In a real app, we'd inject a ProviderProfileService here
        base_delay = 7 # days
        
        if request.owner_type == OwnerType.PROVIDER:
            # Example: Aviva might be slow
            # if request.provider_id == aviva_id: return now + 15 days
            base_delay = 10
            
        return datetime.now() + timedelta(days=base_delay)
