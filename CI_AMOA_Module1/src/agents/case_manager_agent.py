"""
CaseManagerAgent - Manages case lifecycle and status tracking
"""
from textwrap import dedent
from pydantic import BaseModel, Field
from agno.agent import Agent
from loguru import logger
from src.agents.base import get_azure_model
from datetime import datetime


class CaseSummaryOutput(BaseModel):
    """Structured output for case summary"""
    case_status: str = Field(
        ...,
        description="Current case status: New, In progress, Resolved"
    )
    workflow_progress: str = Field(
        ...,
        description="Text description of workflow progress status"
    )
    assigned_agent: str = Field(
        default="",
        description="Name of the assigned internal agent"
    )
    time_to_sla_deadline: float = Field(
        ...,
        description="Hours remaining until SLA deadline (negative if exceeded)"
    )
    compliance_status: str = Field(
        ...,
        description="Current compliance status: Green, Yellow, Red"
    )
    next_actions: list[str] = Field(
        default_factory=list,
        description="Recommended next actions for this case"
    )
    case_age_hours: float = Field(
        ...,
        description="Age of the case in hours since creation"
    )
    requires_attention: bool = Field(
        default=False,
        description="True if this case requires immediate attention"
    )


class CaseManagerAgent:
    """
    Agent responsible for managing the complete lifecycle of claims,
    status updates, and member notifications.
    """
    
    def __init__(self):
        current_datetime = datetime.now().isoformat()
        
        self.agent = Agent(
            name="CaseManagerAgent",
            model=get_azure_model(),
            output_schema=CaseSummaryOutput,
            instructions=dedent(f"""
            Current Date and Time: {current_datetime}
            
            You are the CaseManagerAgent for CIMR claims automation.
            Your role is to manage the complete lifecycle of claims from creation to resolution.
            
            Claim Lifecycle Stages:
            
            1. **New** (Initial State)
               - Claim just created
               - Awaiting classification and priority assignment
               - No agent assigned yet
            
            2. **In progress** (Active State)
               - Classification and priority completed
               - Agent assigned
               - Draft response generated
               - Being actively worked on
            
            3. **Resolved** (Final State)
               - Issue addressed
               - Response sent to member
               - Case closed
               - Follow-up optional
            
            Status Management Rules:
            - New → In progress: After classification & priority assignment
            - In progress → Resolved: After issue resolution and member notification
            - Can update at any stage with new information
            - Must document all status changes
            
            Responsibilities:
            
            **Case Tracking:**
            - Monitor claim progress through pipeline
            - Ensure timely status updates
            - Track which claims need attention
            - Identify bottlenecks
            
            **Agent Assignment:**
            - Assign appropriate internal agent based on category
            - Balance workload across team
            - Escalate high-priority cases
            - Re-assign if needed
            
            **Notifications:**
            - Member: Status updates, timeline changes
            - Internal: Escalations, SLA alerts
            - Management: Compliance reports
            
            **Reporting:**
            - Active claims count by status
            - Resolution rate and time
            - Agent workload distribution
            - SLA compliance metrics
            
            **Quality Assurance:**
            - Verify all workflow steps completed
            - Ensure documentation completeness
            - Check response quality
            - Monitor member satisfaction
            
            **Escalation Criteria:**
            - Priority 5 claims (immediate)
            - SLA deadline approaching (< 20% time remaining)
            - Complex cases requiring expert review
            - Member follow-up requests
            - Compliance violations
            
            Best Practices:
            - Update status promptly
            - Document all actions and decisions
            - Communicate proactively with members
            - Maintain audit trail
            - Follow ACAPS guidelines
            - Ensure data privacy and confidentiality
            """),
            markdown=True
        )
    
    def update_status(self, ticket_id: str, new_status: str, notes: str = None) -> str:
        """
        Update claim status with proper validation
        
        Args:
            ticket_id: The claim ticket identifier
            new_status: New status (New, In progress, Resolved)
            notes: Optional notes about the status change
            
        Returns:
            str: Status update confirmation
        """
        prompt = f"""
        Please update the status for claim {ticket_id} to: {new_status}
        
        {f"Notes: {notes}" if notes else ""}
        
        Steps:
        1. Retrieve current claim status
        2. Validate the status transition
        3. Ensure all prerequisite steps are complete:
           - New → In progress: Classification and priority should be set
           - In progress → Resolved: Draft response should exist
        4. Update the claim status
        5. Document the status change
        6. Provide confirmation
        
        Report any issues or missing prerequisites.
        """
        
        response = self.agent.run(prompt)
        return response.content
    
    def assign_agent(self, ticket_id: str, agent_name: str) -> str:
        """
        Assign internal agent to a claim
        
        Args:
            ticket_id: The claim ticket identifier
            agent_name: Name of the agent to assign
            
        Returns:
            str: Assignment confirmation
        """
        prompt = f"""
        Please assign claim {ticket_id} to agent: {agent_name}
        
        Steps:
        1. Retrieve claim details
        2. Verify claim is ready for assignment (has category and priority)
        3. Update assigned_agent field
        4. Change status to "In progress" if currently "New"
        5. Confirm assignment
        """
        
        response = self.agent.run(prompt)
        return response.content
    
    def get_case_summary(self, ticket_id: str) -> CaseSummaryOutput:
        """
        Get comprehensive case summary
        
        Args:
            ticket_id: The claim ticket identifier
            
        Returns:
            CaseSummaryOutput: Structured case summary
        """
        # Get claim data directly from Airtable
        from src.utils.airtable_client import airtable_client
        result = airtable_client.get_record(ticket_id)
        if not result:
            raise ValueError(f"Could not retrieve claim {ticket_id}")
        
        claim_data = result.get('fields', {})
        
        prompt = f"""
        Generate a comprehensive case summary for this CIMR claim:
        
        Ticket ID: {ticket_id}
        Current Status: {claim_data.get('Status', 'New')}
        Category: {claim_data.get('Category', '')}
        Priority: {claim_data.get('Priority', 3)}
        Assigned Agent: {claim_data.get('Assigned Agent', '')}
        Created At: {claim_data.get('Created At', '')}
        SLA Hours: {claim_data.get('SLA Hours', 120)}
        
        Analyze and provide:
        - Current case status (MUST be "In progress" since workflow is running)
        - Workflow progress (which steps are completed)
        - Assigned agent name
        - Time remaining to SLA deadline
        - Compliance status
        - Recommended next actions
        - Case age in hours
        - Whether immediate attention is required
        
        Workflow Steps to Check:
        1. Input parsing (completed)
        2. Claim creation (completed)
        3. Classification (check if Category exists)
        4. Priority scoring (check if Priority exists)
        5. Compliance check (check if Compliance Status exists)
        6. Resolution generation (check if DraftResponse exists)
        7. Case management (this step)
        
        IMPORTANT: Since this workflow is running and all steps are being executed,
        the case status MUST be "In progress" - not "New". A claim is only "New" 
        if it hasn't been processed by any agents yet.
        
        Determine if case requires attention based on:
        - Priority 5 cases
        - SLA deadline approaching (< 20% time remaining)
        - Missing critical workflow steps
        - Compliance violations
        """
        
        response = self.agent.run(prompt)
        case_summary = response.content  # This will be a CaseSummaryOutput object
        
        # Update Airtable with case management data (now that fields exist and are confirmed)
        from src.utils.airtable_client import airtable_client
        airtable_client.update_record(ticket_id, {
            "Status": case_summary.case_status,  # Use agent's determined status
            "Case Status": case_summary.case_status,  # Use agent's output for Case Status
            "Requires Attention": case_summary.requires_attention,
            "Assigned Agent": case_summary.assigned_agent
        })
        
        logger.info(f"✅ Case summary for {ticket_id}: {case_summary.case_status} (Attention: {case_summary.requires_attention})")
        
        return case_summary
    
    def generate_workload_report(self) -> str:
        """
        Generate agent workload distribution report
        
        Returns:
            str: Workload report
        """
        prompt = """
        Please generate a workload distribution report.
        
        Steps:
        1. List all active claims (status: New or In progress)
        2. Group by assigned agent
        3. Count claims per agent
        4. Analyze by priority
        5. Identify overloaded agents
        6. Suggest workload rebalancing if needed
        
        Format as a clear report with actionable recommendations.
        """
        
        response = self.agent.run(prompt)
        return response.content


# Create global instance
case_manager_agent = CaseManagerAgent()
