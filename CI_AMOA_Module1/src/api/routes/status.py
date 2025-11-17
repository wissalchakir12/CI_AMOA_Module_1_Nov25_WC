"""
Status management API routes for CIMR Claims Automation v1
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from loguru import logger

from src.api.models import ClaimStatus, APIResponse, StatusUpdateRequest
from src.utils.airtable_client import airtable_client

router = APIRouter()


@router.put("/{ticket_id}", response_model=APIResponse)
async def update_claim_status(ticket_id: str, request: StatusUpdateRequest):
    """
    Update the status of a claim
    """
    try:
        # Validate status
        valid_statuses = [s.value for s in ClaimStatus]
        if request.status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Prepare update fields
        update_fields = {"Status": request.status}
        
        if request.assigned_agent:
            update_fields["Assigned Agent"] = request.assigned_agent
        
        # Update the record in Airtable
        result = airtable_client.update_record(ticket_id, update_fields)
        
        if not result:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        logger.info(f"Updated claim {ticket_id} status to {request.status}")
        
        return APIResponse(
            success=True,
            message=f"Claim status updated to {request.status}",
            data={
                "ticket_id": ticket_id,
                "status": request.status,
                "assigned_agent": request.assigned_agent,
                "notes": request.notes
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating status for claim {ticket_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{ticket_id}", response_model=APIResponse)
async def get_claim_status(ticket_id: str):
    """
    Get the current status of a claim
    """
    try:
        result = airtable_client.get_record(ticket_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        fields = result.get("fields", {})
        status = fields.get("Status", "New")
        assigned_agent = fields.get("Assigned Agent")
        
        return APIResponse(
            success=True,
            message="Status retrieved successfully",
            data={
                "ticket_id": ticket_id,
                "status": status,
                "assigned_agent": assigned_agent
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting status for claim {ticket_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/stats/summary", response_model=APIResponse)
async def get_status_summary():
    """
    Get summary statistics of claims by status
    """
    try:
        # Get all records
        records = airtable_client.list_records(max_records=1000)
        
        # Count by status
        status_counts = {}
        total_claims = len(records)
        
        for record in records:
            fields = record.get("fields", {})
            status = fields.get("Status", "New")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Calculate percentages
        status_percentages = {}
        for status, count in status_counts.items():
            status_percentages[status] = round((count / total_claims) * 100, 2) if total_claims > 0 else 0
        
        logger.info(f"Retrieved status summary: {status_counts}")
        
        return APIResponse(
            success=True,
            message="Status summary retrieved successfully",
            data={
                "total_claims": total_claims,
                "status_counts": status_counts,
                "status_percentages": status_percentages
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting status summary: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/stats/by-agent", response_model=APIResponse)
async def get_agent_stats():
    """
    Get statistics of claims by assigned agent
    """
    try:
        # Get all records
        records = airtable_client.list_records(max_records=1000)
        
        # Count by agent
        agent_counts = {}
        unassigned_count = 0
        
        for record in records:
            fields = record.get("fields", {})
            assigned_agent = fields.get("Assigned Agent")
            
            if assigned_agent:
                agent_counts[assigned_agent] = agent_counts.get(assigned_agent, 0) + 1
            else:
                unassigned_count += 1
        
        logger.info(f"Retrieved agent stats: {agent_counts}")
        
        return APIResponse(
            success=True,
            message="Agent statistics retrieved successfully",
            data={
                "agent_counts": agent_counts,
                "unassigned_count": unassigned_count,
                "total_agents": len(agent_counts)
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting agent stats: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
