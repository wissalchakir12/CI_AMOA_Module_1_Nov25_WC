"""
Input Parser Agent - Extracts structured claim data from user input
Based on: https://docs.agno.com/examples/getting-started/05-structured-output
"""
from textwrap import dedent
from typing import Optional
from pydantic import BaseModel, Field
from agno.agent import Agent
from loguru import logger

from src.agents.base import get_azure_model
from datetime import datetime


class ClaimInput(BaseModel):
    """Structured claim input data"""
    member_name: str = Field(
        ...,
        description="Full name of the member submitting the claim"
    )
    member_id: str = Field(
        ...,
        description="CIN or Adhérent ID of the member"
    )
    channel: str = Field(
        default="Web",
        description="Channel through which the claim was submitted (Web, Email, WhatsApp)"
    )
    message: str = Field(
        ...,
        description="The actual claim message or complaint from the member"
    )
    attachment_url: Optional[str] = Field(
        None,
        description="URL to any attached document or file"
    )


class InputParserAgent:
    """
    Agent that parses unstructured claim input into structured data
    """
    
    def __init__(self):
        # Get current datetime for dynamic context
        current_datetime = datetime.now().isoformat()
        
        self.agent = Agent(
            name="InputParserAgent",
            model=get_azure_model(),
            description=dedent("""
            You are an expert data extraction specialist for CIMR (Caisse Interprofessionnelle Marocaine de Retraite).
            Your role is to carefully extract and structure claim information from various input formats.
            You handle multilingual inputs (French, Arabic, English, Amazigh) with precision.
            """),
            instructions=dedent(f"""
            Current Date and Time: {current_datetime}
            
            Extract the following information from the claim submission:
            
            1. Member Name: The full name of the person submitting the claim
               - Look for patterns like "je suis [Name]", "I am [Name]", "My name is [Name]"
               - Extract full name (first and last name)
            
            2. Member ID (CIN / Adhérent ID): The identification number
               - Look for "CIN:", "CIN / Adhérent ID:", "ID:", "Numéro:"
               - Extract the alphanumeric identifier
            
            3. Channel: The submission channel (default to "Web" if not specified)
               - Look for "Channel:", "Via:", "Canal:"
               - Common values: Web, Email, WhatsApp
            
            4. Message: The actual claim or complaint
               - Extract the main complaint message
               - Look for keywords like "Message:", "Réclamation:", "Problème:"
               - Include the full description of the issue
            
            5. Attachment URL: Any file or document URL (optional)
               - Look for "Attachment:", "Document:", "Fichier:", URLs
            
            Handle variations in format:
            - Structured format with labels
            - Natural language format
            - Mixed French/Arabic text
            - Incomplete information (use reasonable defaults)
            
            Be thorough and accurate in extraction!
            """),
            output_schema=ClaimInput,
            markdown=True
        )
    
    def parse_input(self, raw_input: str) -> ClaimInput:
        """
        Parse raw claim input into structured ClaimInput
        
        Args:
            raw_input: Unstructured claim text
            
        Returns:
            ClaimInput: Structured claim data
        """
        logger.info("Parsing claim input...")
        
        try:
            response = self.agent.run(raw_input)
            
            # The response.content will be a ClaimInput object due to output_schema
            claim_data = response.content
            
            logger.info(f"✅ Parsed claim for member: {claim_data.member_name}")
            
            return claim_data
            
        except Exception as e:
            logger.error(f"❌ Error parsing input: {e}")
            raise


# Global instance
input_parser_agent = InputParserAgent()

