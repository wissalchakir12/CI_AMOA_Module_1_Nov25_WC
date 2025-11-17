"""
Priority scoring API routes for CIMR Claims Automation v1
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from loguru import logger

from src.api.models import ClaimCategory, APIResponse
from src.utils.airtable_client import airtable_client

router = APIRouter()


@router.post("/{ticket_id}", response_model=APIResponse)
async def score_claim_priority(ticket_id: str):
    """
    Score the priority of a claim (1-5 scale)
    """
    try:
        # Get the claim from Airtable
        result = airtable_client.get_record(ticket_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        fields = result.get("fields", {})
        message = fields.get("Message", "")
        category = fields.get("Category", "")
        
        # TODO: Replace with actual AI priority scoring
        # For now, using simple rule-based scoring
        priority_score, reasoning = _calculate_priority(message, category)
        
        # Update the record with priority score
        update_fields = {
            "Priority": priority_score
        }
        
        airtable_client.update_record(ticket_id, update_fields)
        
        logger.info(f"Scored claim {ticket_id} priority as {priority_score}")
        
        return APIResponse(
            success=True,
            message="Priority scored successfully",
            data={
                "ticket_id": ticket_id,
                "priority_score": priority_score,
                "reasoning": reasoning,
                "category": category
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scoring priority for claim {ticket_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def _calculate_priority(message: str, category: str) -> tuple[int, str]:
    """
    Calculate priority score based on message content and category
    """
    message_lower = message.lower()
    priority_score = 1  # Default low priority
    reasoning_parts = []
    
    # High priority indicators
    high_priority_keywords = ["urgent", "urgente", "immédiat", "asap", "critique", "critical", "grave"]
    if any(keyword in message_lower for keyword in high_priority_keywords):
        priority_score = max(priority_score, 5)
        reasoning_parts.append("Contains urgent keywords")
    
    # Payment issues are generally high priority
    if category == "Payment" or "paiement" in message_lower or "pension" in message_lower:
        priority_score = max(priority_score, 4)
        reasoning_parts.append("Payment-related issue")
    
    # Death-related claims are high priority
    if category == "Death" or "décès" in message_lower or "mort" in message_lower:
        priority_score = max(priority_score, 5)
        reasoning_parts.append("Death-related claim")
    
    # Time-sensitive keywords
    time_keywords = ["depuis", "depuis 2 mois", "non payé", "retard", "delay", "late", "overdue"]
    if any(keyword in message_lower for keyword in time_keywords):
        priority_score = max(priority_score, 3)
        reasoning_parts.append("Time-sensitive issue")
    
    # Financial impact keywords
    financial_keywords = ["argent", "money", "perte", "loss", "erreur", "error", "incorrect"]
    if any(keyword in message_lower for keyword in financial_keywords):
        priority_score = max(priority_score, 3)
        reasoning_parts.append("Financial impact")
    
    # Technical issues are generally lower priority
    if category == "Technical" and priority_score == 1:
        priority_score = 2
        reasoning_parts.append("Technical issue")
    
    # Ensure priority is within valid range
    priority_score = max(1, min(5, priority_score))
    
    reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Standard processing"
    
    return priority_score, reasoning


@router.get("/{ticket_id}/priority", response_model=APIResponse)
async def get_claim_priority(ticket_id: str):
    """
    Get the current priority score of a claim
    """
    try:
        result = airtable_client.get_record(ticket_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        fields = result.get("fields", {})
        priority = fields.get("Priority")
        
        return APIResponse(
            success=True,
            message="Priority retrieved successfully",
            data={
                "ticket_id": ticket_id,
                "priority": priority
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting priority for claim {ticket_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
