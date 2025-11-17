"""
ResolutionGeneratorAgent - Generates personalized response drafts
"""
from textwrap import dedent
from pydantic import BaseModel, Field
from agno.agent import Agent
from loguru import logger
from src.agents.base import get_azure_model
from datetime import datetime


class ResolutionOutput(BaseModel):
    """Structured output for resolution generation"""
    draft_response: str = Field(
        ...,
        description="Complete draft response ready for member communication"
    )
    response_language: str = Field(
        default="French",
        description="Language used for the response (French, Arabic, English)"
    )
    internal_actions: list[str] = Field(
        default_factory=list,
        description="List of internal actions required for staff"
    )
    estimated_resolution_time: str = Field(
        ...,
        description="Estimated time to resolve the claim"
    )
    requires_manager_review: bool = Field(
        default=False,
        description="True if this response requires manager approval"
    )
    response_quality_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Quality score of the generated response (0.0 to 1.0)"
    )


class ResolutionGeneratorAgent:
    """
    Agent responsible for generating personalized, professional response drafts
    for claims based on category, priority, and member context.
    """
    
    def __init__(self):
        current_datetime = datetime.now().isoformat()
        
        self.agent = Agent(
            name="ResolutionGeneratorAgent",
            model=get_azure_model(),
            output_schema=ResolutionOutput,
            instructions=dedent(f"""
            Current Date and Time: {current_datetime}
            
            You are a professional response writer for CIMR (Caisse Interprofessionnelle Marocaine de Retraite).
            Generate empathetic, personalized, and actionable responses to member claims.
            
            **Response Formula (7-Part Structure):**
            
            1. **Personalized Greeting**
               - Use member's name: "Cher(e) [Name]," or "Madame/Monsieur [Name],"
               - Respectful and warm tone
            
            2. **Acknowledgment** (1-2 sentences)
               - Confirm receipt: "Nous avons bien reçu votre réclamation concernant..."
               - Show understanding: "Nous comprenons que..."
            
            3. **Empathy Statement** (1 sentence)
               - Death: "Nous présentons nos sincères condoléances pour votre perte."
               - Payment: "Nous comprenons l'importance de vos paiements de pension pour votre sécurité financière."
               - Other: "Nous comprenons votre préoccupation et sommes là pour vous aider."
            
            4. **Action Being Taken** (2-3 sentences)
               - Be specific: "Notre équipe [specific department] va..."
               - Explain the process clearly
               - Death: "Un conseiller spécialisé prendra en charge votre dossier."
               - Payment: "Nous vérifions immédiatement avec notre service financier."
               - Technical: "Notre équipe technique examine la situation."
            
            5. **Timeline** (1 sentence, based on priority)
               - Priority 5: "Vous recevrez une réponse complète dans les 24 heures."
               - Priority 4: "Nous vous contacterons dans les 48 heures."
               - Priority 3: "Un retour vous sera fait sous 5 jours ouvrés."
               - Priority 2-1: "Nous reviendrons vers vous dans les prochains jours."
            
            6. **Next Steps / What Member Should Know** (1-2 sentences)
               - What happens next
               - What member should expect
               - Any documents needed (if applicable)
            
            7. **Closing**
               - Offer: "N'hésitez pas à nous contacter pour toute question."
               - Sign-off: "Cordialement,\nL'équipe CIMR"
            
            **Category-Specific Guidance:**
            
            **Payment** (90% of claims):
            - Emphasize urgency and importance
            - Reference "service financier" or "département des pensions"
            - Mention verification of "dossier de paiement" and "coordonnées bancaires"
            - For delays: "Nous vérifions immédiatement la cause du retard"
            
            **Death** (Always Priority 5):
            - Lead with condolences: "Nous présentons nos sincères condoléances..."
            - Use phrase: "équipe spécialisée dans les successions"
            - Mention: "traitement prioritaire" and "accompagnement personnalisé"
            - Timeline: "sous 24 heures"
            
            **Affiliation**:
            - Reference: "service d'affiliation" and "éligibilité"
            - Mention: "vérification de votre dossier"
            - List any documents if needed
            
            **Contribution**:
            - Reference: "historique de cotisations" or "relevé de compte"
            - Explain: "analyse détaillée" will be provided
            
            **Technical**:
            - Acknowledge inconvenience
            - Reference: "service technique" or "support IT"
            - Offer workaround if possible
            
            **Language & Tone Requirements:**
            - MATCH the member's language (French, Arabic, or English)
            - Professional but warm - avoid overly formal/cold language
            - Use "vous" (formal), never "tu"
            - Culturally appropriate for Morocco
            - NO technical jargon without explanation
            - Perfect grammar and spelling
            
            **Response Quality Scoring (self-evaluate):**
            - 0.95-1.0: Highly personalized, perfect tone, actionable, complete
            - 0.85-0.94: Good personalization, clear, all elements present
            - 0.70-0.84: Adequate but generic, missing some personalization
            - Below 0.70: Needs improvement
            
            **Estimated Resolution Time:**
            - Death: "24 heures"
            - Payment (critical): "24-48 heures"
            - Payment (standard): "3-5 jours"
            - Other: "5-7 jours"
            
            **Quality Checklist:**
            ✓ Member name used in greeting
            ✓ Specific issue acknowledged
            ✓ Empathy shown
            ✓ Concrete action described
            ✓ Clear timeline provided
            ✓ Next steps explained
            ✓ Professional closing
            ✓ Language matches member's input
            ✓ Zero typos or grammar errors
            """),
            markdown=True
        )
    
    def generate_response(self, ticket_id: str) -> ResolutionOutput:
        """
        Generate a personalized response draft for a claim
        
        Args:
            ticket_id: The claim ticket identifier
            
        Returns:
            ResolutionOutput: Structured resolution generation result
        """
        # Get claim data directly from Airtable
        from src.utils.airtable_client import airtable_client
        result = airtable_client.get_record(ticket_id)
        if not result:
            raise ValueError(f"Could not retrieve claim {ticket_id}")
        
        claim_data = result.get('fields', {})
        member_name = claim_data.get('Member Name', '')
        category = claim_data.get('Category', '')
        priority = claim_data.get('Priority', 3)
        message = claim_data.get('Message', '')
        
        prompt = f"""
        Generate a professional response draft for this CIMR claim:
        
        Member: {member_name}
        Category: {category}
        Priority: {priority}
        Message: {message}
        
        Create a complete response that includes:
        - Professional greeting with member name
        - Acknowledgment of their concern
        - Clear explanation of actions being taken
        - Timeline based on priority level
        - Next steps for the member
        - Professional closing
        
        Also provide:
        - Language used (French/Arabic/English)
        - Internal actions required for staff
        - Estimated resolution time
        - Whether manager review is needed
        - Quality score (0.0 to 1.0)
        
        Priority Timeline Guidelines:
        - Priority 5: "dans les 24 heures"
        - Priority 4: "dans les 48 heures"
        - Priority 3: "dans les 5 jours ouvrés"
        - Priority 2-1: "dans les prochains jours"
        
        Ensure tone is empathetic, professional, and culturally appropriate.
        """
        
        response = self.agent.run(prompt)
        resolution_result = response.content  # This will be a ResolutionOutput object
        
        # Update Airtable with the resolution (now that fields exist)
        from src.utils.airtable_client import airtable_client
        airtable_client.update_record(ticket_id, {
            "DraftResponse": resolution_result.draft_response,
            "Response Quality Score": resolution_result.response_quality_score,
            "Response Language": resolution_result.response_language,
            "Estimated Resolution Time": resolution_result.estimated_resolution_time
        })
        
        logger.info(f"✅ Generated response for {ticket_id} (Quality: {resolution_result.response_quality_score})")
        
        return resolution_result
    
    def refine_response(self, ticket_id: str, feedback: str) -> str:
        """
        Refine a response draft based on feedback
        
        Args:
            ticket_id: The claim ticket identifier
            feedback: Feedback for improvement
            
        Returns:
            str: Refined response draft
        """
        prompt = f"""
        Please refine the response draft for claim {ticket_id} based on this feedback:
        
        Feedback: {feedback}
        
        Steps:
        1. Retrieve current draft response
        2. Incorporate the feedback
        3. Ensure all quality guidelines are met
        4. Update the claim record
        5. Present the refined version
        """
        
        response = self.agent.run(prompt)
        return response.content


# Create global instance
resolution_generator_agent = ResolutionGeneratorAgent()
