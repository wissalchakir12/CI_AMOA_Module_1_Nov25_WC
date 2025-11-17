"""
PriorityScoringAgent - Evaluates claim urgency and priority
"""
from textwrap import dedent
from pydantic import BaseModel, Field
from agno.agent import Agent
from loguru import logger
from src.agents.base import get_azure_model
from datetime import datetime


class PriorityOutput(BaseModel):
    """Structured output for priority scoring"""
    priority_score: int = Field(
        ...,
        ge=1,
        le=5,
        description="Priority score from 1 (minimal) to 5 (critical)"
    )
    sla_hours: int = Field(
        ...,
        description="SLA deadline in hours (24, 48, 120, 168, 240)"
    )
    urgency_factors: list[str] = Field(
        default_factory=list,
        description="List of factors that influenced the priority score"
    )
    reasoning: str = Field(
        ...,
        description="Detailed explanation of the priority assignment"
    )
    requires_escalation: bool = Field(
        default=False,
        description="True if this is a critical case requiring immediate attention"
    )
    recommended_actions: list[str] = Field(
        default_factory=list,
        description="Recommended immediate actions for this priority level"
    )


class PriorityScoringAgent:
    """
    Agent responsible for evaluating claim urgency and assigning priority scores.
    Provides SLA recommendations based on priority.
    """
    
    def __init__(self):
        current_datetime = datetime.now().isoformat()
        
        self.agent = Agent(
            name="PriorityScoringAgent",
            model=get_azure_model(),
            output_schema=PriorityOutput,
            instructions=dedent(f"""
            Current Date and Time: {current_datetime}
            
            You are an urgency evaluation expert for CIMR pension fund claims.
            Analyze each claim and assign a priority score (1-5) based on urgency and impact.
            
            **Priority Matrix:**
            
            **Priority 5 - CRITICAL** (SLA: 24 hours)
            Triggers:
            - Death category claims (always Priority 5)
            - Complete pension payment stoppage (2+ months)
            - Explicit "urgent/critique/emergency" mentions + financial distress
            - Member states they have "no income" or "sans ressources"
            Indicators: décès, urgent, critique, non payé depuis, sans ressources, besoin immédiat
            
            **Priority 4 - HIGH** (SLA: 48 hours)
            Triggers:
            - Payment delays of 1-2 months
            - Significant payment errors (wrong amount received)
            - Affiliation blocking access to pension
            - Legal/administrative deadlines mentioned
            Indicators: retard paiement, erreur montant, pas reçu, délai, bloqué
            
            **Priority 3 - MEDIUM** (SLA: 5 business days)
            Triggers:
            - Recent payment issues (< 1 month delay)
            - Affiliation questions with moderate urgency
            - Contribution amount queries
            - Document update requests
            Indicators: question, demande, changement, vérification, mise à jour
            
            **Priority 2 - LOW** (SLA: 7 business days)
            Triggers:
            - Technical issues (non-critical, workarounds available)
            - General information requests
            - Documentation inquiries
            - Minor website problems
            Indicators: site web, accès, information, renseignement
            
            **Priority 1 - MINIMAL** (SLA: 10 business days)
            Triggers:
            - General inquiries without urgency
            - Informational brochure requests
            - Future planning questions
            Indicators: pourriez-vous, j'aimerais savoir, information générale
            
            **Scoring Logic:**
            
            1. **Base Priority by Category:**
               - Death → Start at 5
               - Payment → Start at 3-4 (depending on duration)
               - Affiliation → Start at 3
               - Contribution → Start at 2-3
               - Technical → Start at 2
            
            2. **Urgency Multipliers** (adjust +1 or +2):
               - Explicit urgency words ("urgent", "critique", "immédiat")
               - Duration mentioned ("> 2 months" = +2, "> 1 month" = +1)
               - Financial hardship indicated ("sans ressources", "ne peux pas payer")
               - Elderly/vulnerable member context
            
            3. **De-escalation** (adjust -1):
               - Polite/informational tone without urgency
               - Future-oriented questions
               - "Pas urgent" or "quand vous pourrez" mentioned
            
            **SLA Calculation:**
            - Priority 5 → 24 hours
            - Priority 4 → 48 hours
            - Priority 3 → 120 hours (5 business days)
            - Priority 2 → 168 hours (7 business days)
            - Priority 1 → 240 hours (10 business days)
            
            **Requires Escalation:**
            - Set to true ONLY for Priority 5 (Critical)
            - These require immediate supervisor notification
            
            **Quality Standards:**
            - Explain your priority reasoning in 2-3 clear sentences
            - Cite specific phrases from the message that influenced your decision
            - Be consistent: similar claims should get similar scores
            - When in doubt between two levels, choose the HIGHER priority (better safe than sorry)
            """),
            markdown=True
        )
    
    def score_priority(self, ticket_id: str) -> PriorityOutput:
        """
        Score the priority of a claim
        
        Args:
            ticket_id: The claim ticket identifier
            
        Returns:
            PriorityOutput: Structured priority scoring result
        """
        # Get claim data directly from Airtable
        from src.utils.airtable_client import airtable_client
        result = airtable_client.get_record(ticket_id)
        if not result:
            raise ValueError(f"Could not retrieve claim {ticket_id}")
        
        claim_data = result.get('fields', {})
        message = claim_data.get('Message', '')
        category = claim_data.get('Category', '')
        
        prompt = f"""
        Evaluate the priority for this CIMR claim:
        
        Category: {category}
        Message: {message}
        
        Analyze and provide:
        - Priority score (1-5): 1=minimal, 2=low, 3=medium, 4=high, 5=critical
        - SLA deadline in hours: 24h (critical), 48h (high), 120h (medium), 168h (low), 240h (minimal)
        - Urgency factors that influenced your decision
        - Detailed reasoning for the priority assignment
        - Whether this requires escalation (Priority 5)
        - Recommended immediate actions
        
        Priority Guidelines:
        - Priority 5: Death claims, complete income loss, explicit urgency
        - Priority 4: Payment delays >1 month, significant errors
        - Priority 3: Minor issues, general questions
        - Priority 2: Technical issues, documentation
        - Priority 1: Informational requests
        """
        
        response = self.agent.run(prompt)
        priority_result = response.content  # This will be a PriorityOutput object
        
        # Update Airtable with the priority (now that fields exist)
        from src.utils.airtable_client import airtable_client
        airtable_client.update_record(ticket_id, {
            "Priority": priority_result.priority_score,
            "SLA Hours": priority_result.sla_hours,
            "Requires Escalation": priority_result.requires_escalation
        })
        
        logger.info(f"✅ Scored claim {ticket_id} priority: {priority_result.priority_score} (SLA: {priority_result.sla_hours}h)")
        
        return priority_result
    
    def re_evaluate_priority(self, ticket_id: str, new_information: str) -> str:
        """
        Re-evaluate priority based on new information
        
        Args:
            ticket_id: The claim ticket identifier
            new_information: New context or information
            
        Returns:
            str: Updated priority evaluation
        """
        prompt = f"""
        Re-evaluate the priority for claim {ticket_id} based on new information:
        
        New Information: {new_information}
        
        Please:
        1. Retrieve current claim status and priority
        2. Consider the new information
        3. Determine if priority should change
        4. Update if necessary
        5. Explain any changes or confirm current priority
        """
        
        response = self.agent.run(prompt)
        return response.content


# Create global instance
priority_scoring_agent = PriorityScoringAgent()
