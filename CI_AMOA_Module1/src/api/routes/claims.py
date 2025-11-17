"""
Claims API routes for CIMR Claims Automation v1
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
from loguru import logger

from src.api.models import ClaimSubmission, ClaimResponse, APIResponse
from src.utils.airtable_client import airtable_client
from src.agents.claims_workflow import process_claim_async

router = APIRouter()


@router.post("/", response_model=APIResponse)
async def create_claim(claim: ClaimSubmission):
    """
    Create a new claim and process it through the complete AI workflow
    """
    try:
        logger.info(f"Processing new claim from {claim.member_name} via {claim.channel.value}")
        
        # Prepare claim message for workflow
        claim_message = f"""
New claim submission:

Member Name: {claim.member_name}
CIN / Adhérent ID: {claim.member_id}
Channel: {claim.channel.value}
Message: {claim.message}
"""
        
        if claim.attachment_url:
            claim_message += f"Attachment URL: {claim.attachment_url}\n"
        
        # Process through Agno Workflow
        workflow_result = await process_claim_async(
            member_input=claim_message,
            channel=claim.channel.value
        )
        
        if not workflow_result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=f"Workflow execution failed: {workflow_result.get('error')}"
            )
        
        logger.info(f"✅ Workflow completed successfully")
        
        return APIResponse(
            success=True,
            message="Claim created and processed successfully through AI workflow",
            data={
                "workflow_name": workflow_result.get('workflow_name'),
                "content": workflow_result.get('content'),
                "created_at": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing claim: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{ticket_id}", response_model=ClaimResponse)
async def get_claim(ticket_id: str):
    """
    Get a specific claim by ticket ID
    """
    try:
        result = airtable_client.get_record(ticket_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        fields = result.get("fields", {})
        
        # Convert Airtable response to ClaimResponse
        # Parse dates from Airtable or use record metadata
        created_at_str = fields.get("Created At") or result.get("createdTime")
        last_updated_str = fields.get("Last Updated") or result.get("createdTime")
        
        claim_response = ClaimResponse(
            ticket_id=ticket_id,
            member_name=fields.get("Member Name", ""),
            member_id=fields.get("CIN / Adhérent ID", ""),
            channel=fields.get("Channel", "Web"),
            message=fields.get("Message", ""),
            attachment_url=fields.get("Attachment URL"),
            category=fields.get("Category"),
            confidence=fields.get("Confidence"),
            priority=fields.get("Priority"),
            sla_hours=fields.get("SLA Hours"),
            status=fields.get("Status", "New"),
            assigned_agent=fields.get("Assigned Agent"),
            requires_attention=fields.get("Requires Attention"),
            draft_response=fields.get("DraftResponse"),
            response_quality_score=fields.get("Response Quality Score"),
            response_language=fields.get("Response Language"),
            created_at=datetime.fromisoformat(created_at_str.replace('Z', '+00:00')) if created_at_str else datetime.now(),
            last_updated=datetime.fromisoformat(last_updated_str.replace('Z', '+00:00')) if last_updated_str else datetime.now()
        )
        
        return claim_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting claim {ticket_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/", response_model=List[ClaimResponse])
async def list_claims(status: str = None, limit: int = 50):
    """
    List all claims with optional filtering
    """
    try:
        # Build filter formula if status is provided
        filter_formula = None
        if status:
            filter_formula = f"{{Status}} = '{status}'"
        
        # Get records from Airtable
        records = airtable_client.list_records(
            filter_formula=filter_formula,
            max_records=limit
        )
        
        claims = []
        for record in records:
            fields = record.get("fields", {})
            
            # Parse dates from Airtable or use record metadata
            created_at_str = fields.get("Created At") or record.get("createdTime")
            last_updated_str = fields.get("Last Updated") or record.get("createdTime")
            
            claim = ClaimResponse(
                ticket_id=record.get("id", ""),
                member_name=fields.get("Member Name", ""),
                member_id=fields.get("CIN / Adhérent ID", ""),
                channel=fields.get("Channel", "Web"),
                message=fields.get("Message", ""),
                attachment_url=fields.get("Attachment URL"),
                category=fields.get("Category"),
                confidence=fields.get("Confidence"),
                priority=fields.get("Priority"),
                sla_hours=fields.get("SLA Hours"),
                status=fields.get("Status", "New"),
                assigned_agent=fields.get("Assigned Agent"),
                requires_attention=fields.get("Requires Attention"),
                draft_response=fields.get("DraftResponse"),
                response_quality_score=fields.get("Response Quality Score"),
                response_language=fields.get("Response Language"),
                created_at=datetime.fromisoformat(created_at_str.replace('Z', '+00:00')) if created_at_str else datetime.now(),
                last_updated=datetime.fromisoformat(last_updated_str.replace('Z', '+00:00')) if last_updated_str else datetime.now()
            )
            claims.append(claim)
        
        logger.info(f"Retrieved {len(claims)} claims")
        return claims
        
    except Exception as e:
        logger.error(f"Error listing claims: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{ticket_id}/status", response_model=APIResponse)
async def update_claim_status(ticket_id: str, status: str, assigned_agent: str = None):
    """
    Update claim status and optionally assign to agent
    """
    try:
        # Prepare update fields
        fields = {"Status": status}
        if assigned_agent:
            fields["Assigned Agent"] = assigned_agent
        
        # Update record in Airtable
        result = airtable_client.update_record(ticket_id, fields)
        
        if not result:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        logger.info(f"Updated claim {ticket_id} status to {status}")
        
        return APIResponse(
            success=True,
            message=f"Claim status updated to {status}",
            data={
                "ticket_id": ticket_id,
                "status": status,
                "assigned_agent": assigned_agent,
                "updated_at": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating claim {ticket_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
