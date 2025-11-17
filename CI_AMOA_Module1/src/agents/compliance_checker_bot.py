"""
ComplianceCheckerBot - Monitors ACAPS compliance and SLA adherence
"""
from textwrap import dedent
from pydantic import BaseModel, Field
from agno.agent import Agent
from loguru import logger
from src.agents.base import get_azure_model
from datetime import datetime


class ComplianceOutput(BaseModel):
    """Structured output for compliance checking"""
    compliance_status: str = Field(
        ...,
        description="Compliance status: Green (compliant), Yellow (approaching deadline), Red (exceeded)"
    )
    sla_status: str = Field(
        ...,
        description="SLA status: Within SLA, Approaching SLA, Exceeded SLA"
    )
    time_remaining_hours: float = Field(
        ...,
        description="Hours remaining until SLA deadline (negative if exceeded)"
    )
    compliance_score: float = Field(
        ...,
        description="Compliance score from 0.0 to 1.0"
    )
    missing_documentation: list[str] = Field(
        default_factory=list,
        description="List of missing required documentation"
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Recommended actions to improve compliance"
    )
    requires_escalation: bool = Field(
        default=False,
        description="True if immediate escalation is required"
    )


class ComplianceCheckerBot:
    """
    Agent responsible for monitoring compliance with ACAPS regulations
    and internal CIMR SLA requirements.
    """
    
    def __init__(self):
        current_datetime = datetime.now().isoformat()
        
        self.agent = Agent(
            name="ComplianceCheckerBot",
            model=get_azure_model(),
            output_schema=ComplianceOutput,
            instructions=dedent(f"""
            Current Date and Time: {current_datetime}
            
            You are the ComplianceCheckerBot for CIMR claims automation.
            Your role is to ensure compliance with ACAPS (Autorité de Contrôle des Assurances et de la Prévoyance Sociale) 
            regulations and internal CIMR SLA requirements.
            
            ACAPS Compliance Requirements:
            1. **Response Time**: All claims must receive initial response within regulatory timeframes
            2. **Documentation**: Proper documentation and audit trails must be maintained
            3. **Resolution Time**: Claims must be resolved within mandated periods
            4. **Member Communication**: Regular updates must be provided to members
            5. **Escalation**: Critical issues must be escalated appropriately
            
            SLA Deadlines by Priority:
            - Priority 5 (Critical): 24 hours
            - Priority 4 (High): 48 hours  
            - Priority 3 (Medium): 5 days
            - Priority 2 (Low): 7 days
            - Priority 1 (Minimal): 10 days
            
            Compliance Checks:
            1. **Time Tracking**: Monitor claim age against SLA deadlines
            2. **Status Validation**: Ensure proper status progression
            3. **Documentation**: Verify all required fields are populated
            4. **Response Quality**: Check that draft responses are generated
            5. **Escalation Alerts**: Flag claims approaching or exceeding SLA
            
            Alerts and Recommendations:
            - **Red Alert**: SLA exceeded, immediate action required
            - **Yellow Alert**: Approaching SLA deadline (80% of time elapsed)
            - **Green**: Within SLA compliance
            
            Generate Reports on:
            - Claims exceeding SLA
            - Compliance rate by category
            - Average resolution time
            - Pending claims by priority
            - Corrective action recommendations
            
            Important:
            - Always check current datetime for accurate calculations
            - Consider business days vs calendar days
            - Flag systematic compliance issues
            - Provide actionable recommendations
            - Document all compliance checks
            """),
            markdown=True
        )
    
    def check_claim_compliance(self, ticket_id: str) -> ComplianceOutput:
        """
        Check compliance status for a specific claim
        
        Args:
            ticket_id: The claim ticket identifier
            
        Returns:
            ComplianceOutput: Structured compliance check result
        """
        # Get claim data directly from Airtable
        from src.utils.airtable_client import airtable_client
        result = airtable_client.get_record(ticket_id)
        if not result:
            raise ValueError(f"Could not retrieve claim {ticket_id}")
        
        claim_data = result.get('fields', {})
        priority = claim_data.get('Priority', 3)
        sla_hours = claim_data.get('SLA Hours', 120)
        created_at = claim_data.get('Created At', '')
        
        prompt = f"""
        Perform ACAPS compliance check for this CIMR claim:
        
        Ticket ID: {ticket_id}
        Priority: {priority}
        SLA Hours: {sla_hours}
        Created At: {created_at}
        
        Analyze and provide:
        - Compliance status: Green (compliant), Yellow (approaching), Red (exceeded)
        - SLA status: Within SLA, Approaching SLA, Exceeded SLA
        - Time remaining in hours (negative if exceeded)
        - Compliance score (0.0 to 1.0)
        - Missing documentation fields
        - Recommended actions
        - Whether escalation is required
        
        SLA Guidelines:
        - Priority 5: 24h SLA
        - Priority 4: 48h SLA
        - Priority 3: 120h SLA (5 days)
        - Priority 2: 168h SLA (7 days)
        - Priority 1: 240h SLA (10 days)
        
        Yellow Alert: 80% of SLA time elapsed
        Red Alert: SLA exceeded
        """
        
        response = self.agent.run(prompt)
        compliance_result = response.content  # This will be a ComplianceOutput object
        
        # Update Airtable with compliance data (now that fields exist)
        from src.utils.airtable_client import airtable_client
        airtable_client.update_record(ticket_id, {
            "Compliance Status": compliance_result.compliance_status,
            "Compliance Score": compliance_result.compliance_score,
            "Time to SLA Deadline": compliance_result.time_remaining_hours
        })
        
        logger.info(f"✅ Compliance check for {ticket_id}: {compliance_result.compliance_status} (Score: {compliance_result.compliance_score})")
        
        return compliance_result
    
    def generate_compliance_report(self, status_filter: str = None) -> str:
        """
        Generate overall compliance report
        
        Args:
            status_filter: Optional status filter (New, In progress, Resolved)
            
        Returns:
            str: Comprehensive compliance report
        """
        prompt = f"""
        Generate a comprehensive ACAPS compliance report.
        
        Steps:
        1. List claims (filter by status: {status_filter if status_filter else 'all'})
        2. Check current datetime
        3. Analyze each claim for SLA compliance
        4. Calculate compliance metrics:
           - Total claims
           - Claims within SLA
           - Claims approaching SLA (80%+)
           - Claims exceeding SLA
           - Average resolution time
        5. Identify trends and systematic issues
        6. Provide corrective action recommendations
        
        Format as a professional compliance report with metrics and actionable insights.
        """
        
        response = self.agent.run(prompt)
        return response.content


# Create global instance
compliance_checker_bot = ComplianceCheckerBot()
