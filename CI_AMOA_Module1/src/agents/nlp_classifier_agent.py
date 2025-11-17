"""
NLPClassifierAgent - Classifies claims using AI/NLP
"""
from textwrap import dedent
from pydantic import BaseModel, Field
from agno.agent import Agent
from loguru import logger
from datetime import datetime
from src.agents.base import get_azure_model


class ClassificationOutput(BaseModel):
    """Structured output for claim classification"""
    category: str = Field(
        ...,
        description="Claim category: Payment, Affiliation, Contribution, Death, or Technical"
    )
    confidence: float = Field(
        ...,
        description="Confidence score between 0.0 and 1.0"
    )
    reasoning: str = Field(
        ...,
        description="Explanation of why this category was chosen"
    )
    keywords: list[str] = Field(
        default_factory=list,
        description="Key words or phrases that influenced the classification"
    )
    requires_manual_review: bool = Field(
        default=False,
        description="True if confidence is low or claim is ambiguous"
    )


class NLPClassifierAgent:
    """
    Agent responsible for classifying claims into categories using NLP.
    Supports multilingual classification (French, Arabic, English, Amazigh).
    """
    
    def __init__(self):
        current_datetime = datetime.now().isoformat()
        
        self.agent = Agent(
            name="NLPClassifierAgent",
            model=get_azure_model(),
            output_schema=ClassificationOutput,
            instructions=dedent(f"""
            Current Date and Time: {current_datetime}
            
            You are an expert NLP classifier for CIMR pension fund claims.
            Analyze the claim message and classify it into ONE of the following categories:
            
            **Categories:**
            
            1. **Payment** - Pension payment issues (delays, missing payments, incorrect amounts, bank transfer problems)
               French: paiement, pension, versement, argent, virement, retard, non payé
               Arabic: الدفع, المعاش, التأخير, المبلغ
               
            2. **Affiliation** - Membership and enrollment (new registration, eligibility questions, membership status)
               French: affiliation, adhésion, inscription, membre, éligibilité
               Arabic: الانتماء, التسجيل, العضوية
               
            3. **Contribution** - Contribution inquiries (cotisation amounts, deduction questions, payment history)
               French: cotisation, contribution, prélèvement, retenue, montant
               Arabic: المساهمة, الاشتراك
               
            4. **Death** - Death-related claims (beneficiary rights, inheritance, death certificates, pension transfer)
               French: décès, mort, défunt, bénéficiaire, succession, héritage
               Arabic: الوفاة, المتوفى, المستفيد, الورثة
               
            5. **Technical** - System and access issues (login problems, website errors, password reset, technical glitches)
               French: problème technique, site web, connexion, accès, erreur système, mot de passe
               Arabic: مشكلة تقنية, موقع, الدخول
            
            **Classification Rules:**
            - Read the ENTIRE message carefully
            - Identify the PRIMARY issue (if multiple issues, choose the most critical)
            - Consider emotional tone and urgency indicators
            - Look for explicit category keywords and implicit context clues
            
            **Confidence Scoring:**
            - 0.95-1.0: Explicit category mention with clear supporting details
            - 0.80-0.94: Strong contextual indicators, unambiguous intent
            - 0.60-0.79: Reasonable confidence, some ambiguity possible
            - 0.40-0.59: Uncertain, multiple interpretations possible
            - Below 0.40: Unable to classify confidently - REQUIRES MANUAL REVIEW
            
            **Quality Standards:**
            - Extract 3-5 key words/phrases that influenced your decision
            - Provide clear reasoning explaining your classification
            - Flag for manual review if confidence < 0.60 OR claim contains multiple unrelated issues
            - Support all major languages (French, Arabic, English) equally
            
            **Output Requirements:**
            - category: EXACTLY one of: Payment, Affiliation, Contribution, Death, Technical
            - confidence: Float between 0.0 and 1.0
            - reasoning: 2-3 sentences explaining classification logic
            - keywords: List of 3-5 relevant phrases from the message
            - requires_manual_review: true if confidence < 0.60
            """),
            markdown=True
        )
    
    def classify_claim(self, ticket_id: str) -> ClassificationOutput:
        """
        Classify a claim by ticket ID
        
        Args:
            ticket_id: The claim ticket identifier
            
        Returns:
            ClassificationOutput: Structured classification result
        """
        # Get claim data directly from Airtable
        from src.utils.airtable_client import airtable_client
        result = airtable_client.get_record(ticket_id)
        if not result:
            raise ValueError(f"Could not retrieve claim {ticket_id}")
        
        claim_data = result.get('fields', {})
        message = claim_data.get('Message', '')
        
        prompt = f"""
        Classify this CIMR claim:
        
        Message: {message}
        
        Analyze the content and provide:
        - The most appropriate category (Payment, Affiliation, Contribution, Death, or Technical)
        - Confidence score (0.0 to 1.0)
        - Reasoning for your classification
        - Key words that influenced your decision
        - Whether this requires manual review (if confidence < 0.8)
        """
        
        response = self.agent.run(prompt)
        classification = response.content  # This will be a ClassificationOutput object
        
        # Update Airtable with the classification
        from src.utils.airtable_client import airtable_client
        airtable_client.update_record(ticket_id, {
            "Category": classification.category,
            "Confidence": classification.confidence
        })
        
        logger.info(f"✅ Classified claim {ticket_id} as {classification.category} (confidence: {classification.confidence})")
        
        return classification
    
    def batch_classify(self, ticket_ids: list) -> str:
        """
        Classify multiple claims
        
        Args:
            ticket_ids: List of ticket IDs to classify
            
        Returns:
            str: Batch classification results
        """
        prompt = f"""
        Please classify the following claims: {ticket_ids}
        
        For each claim:
        1. Retrieve and analyze the claim
        2. Classify into appropriate category
        3. Update with category and confidence
        4. Note any that need manual review
        
        Provide a summary table of all classifications.
        """
        
        response = self.agent.run(prompt)
        return response.content


# Create global instance
nlp_classifier_agent = NLPClassifierAgent()
