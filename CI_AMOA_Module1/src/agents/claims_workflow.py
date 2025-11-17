"""
CIMR Claims Automation Workflow using Agno Framework
Based on: https://docs.agno.com/concepts/workflows/building-workflow
"""
import json
from agno.workflow import Workflow, StepInput, StepOutput
from loguru import logger

from src.agents.input_parser_agent import input_parser_agent
from src.utils.airtable_client import airtable_client
from src.agents.nlp_classifier_agent import nlp_classifier_agent
from src.agents.priority_scoring_agent import priority_scoring_agent
from src.agents.compliance_checker_bot import compliance_checker_bot
from src.agents.resolution_generator_agent import resolution_generator_agent
from src.agents.case_manager_agent import case_manager_agent
from src.utils.email_service import email_service
from src.agents.duplicate_detection_agent import duplicate_detection_agent


# Step 1: Parse Input - Extract structured data using AI
def parse_input_step(step_input: StepInput) -> StepOutput:
    """Parse unstructured input into structured claim data"""
    logger.info("Step 1: Parsing claim input with AI...")
    
    try:
        # Use the input parser agent to extract structured data
        claim_data = input_parser_agent.parse_input(step_input.input)
        
        logger.info(f"✅ Parsed claim for: {claim_data.member_name}")
        
        # Store claim data in content as JSON string
        import json
        return StepOutput(
            content=json.dumps({
                "message": f"Parsed claim data for {claim_data.member_name}",
                "claim_data": claim_data.dict()
            })
        )
        
    except Exception as e:
        logger.error(f"❌ Input parsing failed: {e}")
        raise


# Step 1.5: Check for Duplicates
def duplicate_check_step(step_input: StepInput) -> StepOutput:
    """Check for duplicate or similar claims"""
    logger.info("Step 1.5: Checking for duplicates...")

    try:
        import json
        # Get parsed claim data from previous step content
        previous_data = json.loads(step_input.previous_step_content)
        claim_data = previous_data.get('claim_data')

        if not claim_data:
            raise ValueError("No claim data found from previous step")

        # Check for duplicates
        duplicate_result = duplicate_detection_agent.check_duplicate(
            member_id=claim_data['member_id'],
            message=claim_data['message'],
            category=None  # Category not yet determined
        )

        action = duplicate_result.get('action', 'allow')
        reason = duplicate_result.get('reason', '')
        confidence = duplicate_result.get('confidence', 0.0)

        # Handle different actions
        if action == "block":
            # Block the claim - it's an exact duplicate
            logger.error(f"🚫 BLOCKED: {reason}")
            duplicate_ticket = duplicate_result.get('duplicate_ticket_id', 'unknown')
            raise ValueError(
                f"Réclamation rejetée: {reason}. "
                f"Réclamation existante: {duplicate_ticket}"
            )

        elif action == "warn":
            # Warn but allow to proceed
            logger.warning(f"⚠️ WARNING: {reason} (confidence: {confidence:.0%})")
            # Add warning to claim data
            claim_data['duplicate_warning'] = {
                'message': reason,
                'duplicate_ticket_id': duplicate_result.get('duplicate_ticket_id'),
                'confidence': confidence
            }

        elif action == "flag":
            # Flag for manual review
            logger.warning(f"🚩 FLAGGED: {reason}")
            claim_data['requires_attention'] = True
            claim_data['flag_reason'] = reason

        else:
            # Allow - no duplicates found
            logger.info(f"✅ {reason}")

        return StepOutput(
            content=json.dumps({
                "message": "Duplicate check passed",
                "duplicate_check": duplicate_result,
                "claim_data": claim_data
            })
        )

    except ValueError as e:
        # Reraise ValueError for blocking
        raise
    except Exception as e:
        # For other errors, log and continue
        logger.error(f"❌ Duplicate check failed: {e}")
        logger.warning("⚠️ Continuing without duplicate check")
        # Return original claim data
        return StepOutput(
            content=step_input.previous_step_content
        )


# Step 2: Create Claim Record in Airtable
def create_claim_step(step_input: StepInput) -> StepOutput:
    """Create claim record in Airtable"""
    logger.info("Step 2: Creating claim record in Airtable...")
    
    try:
        import json
        # Get parsed claim data from previous step content
        previous_data = json.loads(step_input.previous_step_content)
        claim_data = previous_data.get('claim_data')
        
        if not claim_data:
            raise ValueError("No claim data found from previous step")
        
        # Create claim record in Airtable directly
        fields = {
            "Member Name": claim_data['member_name'],
            "CIN / Adhérent ID": claim_data['member_id'],
            "Channel": claim_data['channel'],
            "Message": claim_data['message']
        }
        
        if claim_data.get('attachment_url'):
            fields["Attachment URL"] = claim_data['attachment_url']
        
        result = airtable_client.create_record(fields)
        
        if not result:
            raise ValueError("Failed to create claim in Airtable")
        
        ticket_id = result.get('id')
        logger.info(f"✅ Created claim record. Ticket ID: {ticket_id}")

        # Send confirmation email if member_email is provided
        if claim_data.get('member_email'):
            try:
                email_service.send_claim_confirmation(
                    member_email=claim_data['member_email'],
                    member_name=claim_data['member_name'],
                    ticket_id=ticket_id,
                    claim_category="En cours de classification"
                )
                logger.info(f"✅ Confirmation email sent for ticket {ticket_id}")
            except Exception as e:
                logger.warning(f"⚠️ Could not send confirmation email: {e}")

        return StepOutput(
            content=json.dumps({
                "message": f"Claim created successfully. Ticket ID: {ticket_id}",
                "ticket_id": ticket_id,
                "member_name": claim_data['member_name']
            })
        )
        
    except Exception as e:
        logger.error(f"❌ Claim creation failed: {e}")
        raise


# Step 3: Classification
def classification_step(step_input: StepInput) -> StepOutput:
    """Classify the claim using NLP"""
    logger.info("Step 3: Classifying claim with AI...")
    
    try:
        import json
        previous_data = json.loads(step_input.previous_step_content)
        ticket_id = previous_data.get('ticket_id')
        
        if not ticket_id:
            raise ValueError("No ticket_id found from previous step")
        
        # Call the classifier agent - now returns structured data
        classification_result = nlp_classifier_agent.classify_claim(ticket_id)
        
        logger.info(f"✅ Classification completed: {classification_result.category} (confidence: {classification_result.confidence})")
        
        return StepOutput(
            content=json.dumps({
                "message": f"Classified as {classification_result.category} with {classification_result.confidence} confidence",
                "ticket_id": ticket_id,
                "category": classification_result.category,
                "confidence": classification_result.confidence
            })
        )
        
    except Exception as e:
        logger.error(f"❌ Classification failed: {e}")
        raise


# Step 4: Priority Scoring
def priority_step(step_input: StepInput) -> StepOutput:
    """Score the priority of the claim"""
    logger.info("Step 4: Scoring priority with AI...")
    
    try:
        import json
        previous_data = json.loads(step_input.previous_step_content)
        ticket_id = previous_data.get('ticket_id')
        
        if not ticket_id:
            raise ValueError("No ticket_id found from previous step")
        
        # Call the priority scoring agent - now returns structured data
        priority_result = priority_scoring_agent.score_priority(ticket_id)
        
        logger.info(f"✅ Priority scoring completed: {priority_result.priority_score} (SLA: {priority_result.sla_hours}h)")
        
        return StepOutput(
            content=json.dumps({
                "message": f"Priority {priority_result.priority_score} assigned with {priority_result.sla_hours}h SLA",
                "ticket_id": ticket_id,
                "priority": priority_result.priority_score,
                "sla_hours": priority_result.sla_hours
            })
        )
        
    except Exception as e:
        logger.error(f"❌ Priority scoring failed: {e}")
        raise


# Step 5: Compliance Check
def compliance_step(step_input: StepInput) -> StepOutput:
    """Check compliance with ACAPS requirements"""
    logger.info("Step 5: Checking ACAPS compliance...")
    
    try:
        import json
        previous_data = json.loads(step_input.previous_step_content)
        ticket_id = previous_data.get('ticket_id')
        
        if not ticket_id:
            raise ValueError("No ticket_id found from previous step")
        
        # Call the compliance checker - now returns structured data
        compliance_result = compliance_checker_bot.check_claim_compliance(ticket_id)
        
        logger.info(f"✅ Compliance check completed: {compliance_result.compliance_status} (Score: {compliance_result.compliance_score})")
        
        return StepOutput(
            content=json.dumps({
                "message": f"Compliance: {compliance_result.compliance_status} (Score: {compliance_result.compliance_score})",
                "ticket_id": ticket_id,
                "compliance_status": compliance_result.compliance_status,
                "compliance_score": compliance_result.compliance_score
            })
        )
        
    except Exception as e:
        logger.error(f"❌ Compliance check failed: {e}")
        raise


# Step 6: Resolution Generation
def resolution_step(step_input: StepInput) -> StepOutput:
    """Generate draft response with AI"""
    logger.info("Step 6: Generating resolution draft with AI...")
    
    try:
        import json
        previous_data = json.loads(step_input.previous_step_content)
        ticket_id = previous_data.get('ticket_id')
        
        if not ticket_id:
            raise ValueError("No ticket_id found from previous step")
        
        # Call the resolution generator - now returns structured data
        resolution_result = resolution_generator_agent.generate_response(ticket_id)
        
        logger.info(f"✅ Resolution draft generated (Quality: {resolution_result.response_quality_score})")
        
        return StepOutput(
            content=json.dumps({
                "message": f"Resolution draft generated with {resolution_result.response_quality_score} quality score",
                "ticket_id": ticket_id,
                "draft_response": resolution_result.draft_response[:100] + "..." if len(resolution_result.draft_response) > 100 else resolution_result.draft_response,
                "quality_score": resolution_result.response_quality_score
            })
        )
        
    except Exception as e:
        logger.error(f"❌ Resolution generation failed: {e}")
        raise


# Step 7: Case Management
def case_management_step(step_input: StepInput) -> StepOutput:
    """Generate case summary"""
    logger.info("Step 7: Generating case summary...")
    
    try:
        import json
        previous_data = json.loads(step_input.previous_step_content)
        ticket_id = previous_data.get('ticket_id')
        
        if not ticket_id:
            raise ValueError("No ticket_id found from previous step")
        
        # Call the case manager - now returns structured data
        case_summary = case_manager_agent.get_case_summary(ticket_id)
        
        logger.info(f"✅ Case summary generated: {case_summary.case_status} (Attention: {case_summary.requires_attention})")
        
        return StepOutput(
            content=json.dumps({
                "message": f"Workflow completed successfully for ticket {ticket_id}",
                "summary": f"Status: {case_summary.case_status}, Attention Required: {case_summary.requires_attention}",
                "ticket_id": ticket_id,
                "case_status": case_summary.case_status,
                "requires_attention": case_summary.requires_attention
            })
        )
        
    except Exception as e:
        logger.error(f"❌ Case management failed: {e}")
        raise


# Create the CIMR Claims Processing Workflow
# Using custom Python functions as steps per Agno documentation
# Reference: https://docs.agno.com/concepts/workflows/building-workflow
claims_workflow = Workflow(
    name="CIMR Claims Processing Workflow",
    description="Automated end-to-end claim processing from intake to resolution with duplicate detection",
    steps=[
        parse_input_step,       # Step 1: Parse input with AI (structured output)
        duplicate_check_step,   # Step 1.5: Check for duplicates (NEW)
        create_claim_step,      # Step 2: Create claim record in Airtable
        classification_step,    # Step 3: Classify claim category with AI
        priority_step,          # Step 4: Score priority and set SLA with AI
        compliance_step,        # Step 5: Check ACAPS compliance
        resolution_step,        # Step 6: Generate draft response with AI
        case_management_step,   # Step 7: Case summary and management
    ],
)


def process_claim(member_input: str, channel: str = "Web") -> dict:
    """
    Process a claim through the complete workflow
    
    Args:
        member_input: The member's claim message (can be unstructured)
        channel: Channel used (Web, Email, etc.)
        
    Returns:
        dict: Workflow execution results
    """
    logger.info(f"Starting CIMR Claims Workflow for channel: {channel}")
    
    try:
        # Run the workflow with the claim input
        response = claims_workflow.run(
            input=member_input,
            markdown=True
        )
        
        logger.info(f"✅ Workflow completed successfully")
        
        # Extract ticket_id from the final step's output
        try:
            final_output_content = json.loads(response.content)
            ticket_id = final_output_content.get('ticket_id')
            logger.info(f"✅ Extracted ticket ID: {ticket_id}")
        except:
            ticket_id = None
            logger.warning("⚠️ Could not extract ticket ID from workflow output")
        
        return {
            "success": True,
            "content": response.content if hasattr(response, 'content') else str(response),
            "workflow_name": claims_workflow.name,
            "ticket_id": ticket_id,
        }
        
    except Exception as e:
        logger.error(f"❌ Workflow execution failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def process_claim_async(member_input: str, channel: str = "Web") -> dict:
    """
    Async version of process_claim
    
    Args:
        member_input: The member's claim message (can be unstructured)
        channel: Channel used (Web, Email, etc.)
        
    Returns:
        dict: Workflow execution results
    """
    logger.info(f"Starting CIMR Claims Workflow (async) for channel: {channel}")
    
    try:
        # Run the workflow asynchronously
        response = await claims_workflow.arun(
            input=member_input,
            markdown=True
        )
        
        logger.info(f"✅ Workflow completed successfully")
        
        # Extract ticket_id from the final step's output
        try:
            final_output_content = json.loads(response.content)
            ticket_id = final_output_content.get('ticket_id')
            logger.info(f"✅ Extracted ticket ID: {ticket_id}")
        except:
            ticket_id = None
            logger.warning("⚠️ Could not extract ticket ID from workflow output")
        
        return {
            "success": True,
            "content": response.content if hasattr(response, 'content') else str(response),
            "workflow_name": claims_workflow.name,
            "ticket_id": ticket_id,
        }
        
    except Exception as e:
        logger.error(f"❌ Workflow execution failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }
