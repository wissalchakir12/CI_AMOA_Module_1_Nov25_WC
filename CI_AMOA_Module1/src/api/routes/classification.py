"""
Classification API routes for CIMR Claims Automation v1
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from loguru import logger

from src.api.models import ClaimCategory, APIResponse
from src.utils.airtable_client import airtable_client

router = APIRouter()


@router.post("/{ticket_id}", response_model=APIResponse)
async def classify_claim(ticket_id: str):
    """
    Classify a claim using AI (placeholder implementation)
    """
    try:
        # Get the claim from Airtable
        result = airtable_client.get_record(ticket_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        fields = result.get("fields", {})
        message = fields.get("Message", "")
        
        # TODO: Replace with actual AI classification
        # For now, using simple keyword-based classification
        category, confidence = _classify_message(message)
        
        # Update the record with classification results
        update_fields = {
            "Category": category.value,
            "Confidence": confidence
        }
        
        airtable_client.update_record(ticket_id, update_fields)
        
        logger.info(f"Classified claim {ticket_id} as {category.value} (confidence: {confidence})")
        
        return APIResponse(
            success=True,
            message="Claim classified successfully",
            data={
                "ticket_id": ticket_id,
                "category": category.value,
                "confidence": confidence,
                "message": message[:100] + "..." if len(message) > 100 else message
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error classifying claim {ticket_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def _classify_message(message: str) -> tuple[ClaimCategory, float]:
    """
    Simple keyword-based classification (placeholder for AI)
    """
    message_lower = message.lower()
    
    # Payment-related keywords
    payment_keywords = ["paiement", "pension", "versement", "argent", "salaire", "retraite", "payment", "money"]
    if any(keyword in message_lower for keyword in payment_keywords):
        return ClaimCategory.PAYMENT, 0.85
    
    # Affiliation-related keywords
    affiliation_keywords = ["affiliation", "adhésion", "inscription", "membre", "affiliation", "join"]
    if any(keyword in message_lower for keyword in affiliation_keywords):
        return ClaimCategory.AFFILIATION, 0.80
    
    # Contribution-related keywords
    contribution_keywords = ["cotisation", "contribution", "prélèvement", "deduction", "contribution"]
    if any(keyword in message_lower for keyword in contribution_keywords):
        return ClaimCategory.CONTRIBUTION, 0.82
    
    # Death-related keywords
    death_keywords = ["décès", "mort", "défunt", "succession", "héritage", "death", "deceased"]
    if any(keyword in message_lower for keyword in death_keywords):
        return ClaimCategory.DEATH, 0.90
    
    # Technical-related keywords
    technical_keywords = ["problème", "erreur", "bug", "technique", "système", "technical", "issue", "problem"]
    if any(keyword in message_lower for keyword in technical_keywords):
        return ClaimCategory.TECHNICAL, 0.75
    
    # Default to technical if no clear match
    return ClaimCategory.TECHNICAL, 0.50


@router.get("/{ticket_id}/category", response_model=APIResponse)
async def get_claim_category(ticket_id: str):
    """
    Get the current category of a claim
    """
    try:
        result = airtable_client.get_record(ticket_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        fields = result.get("fields", {})
        category = fields.get("Category")
        confidence = fields.get("Confidence")
        
        return APIResponse(
            success=True,
            message="Category retrieved successfully",
            data={
                "ticket_id": ticket_id,
                "category": category,
                "confidence": confidence
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting category for claim {ticket_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
