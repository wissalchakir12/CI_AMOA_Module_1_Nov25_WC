"""
Test script for CIMR Claims Automation with Structured Outputs
This test verifies that all agents properly save their outputs to Airtable
"""
import asyncio
import json
from loguru import logger
from datetime import datetime

from src.agents.claims_workflow import process_claim_async
from src.utils.airtable_client import airtable_client

async def test_complete_workflow():
    logger.info("======================================================================")
    logger.info("CIMR CLAIMS AUTOMATION - STRUCTURED OUTPUTS TEST")
    logger.info("======================================================================")

    # Test claim with structured data
    member_input = """
    Bonjour, je suis Ahmed Benali, mon CIN est C123456789.
    Je n'ai pas reçu ma pension de retraite depuis 2 mois et c'est très urgent. 
    J'ai besoin de cet argent pour payer mes médicaments et mes factures.
    Ma femme est malade et nous avons des difficultés financières.
    """
    channel = "Web"

    logger.info("📝 Processing claim through complete Agno Workflow...")
    logger.info(f"Input:\n{member_input}")

    # Process through workflow
    workflow_results = await process_claim_async(member_input, channel)

    logger.info("\n🎯 Workflow Results:")
    logger.info(f"✅ Success: {workflow_results['success']}")
    logger.info(f"✅ Workflow Name: {workflow_results.get('workflow_name')}")
    logger.info(f"✅ Ticket ID: {workflow_results.get('ticket_id')}")
    
    if not workflow_results['success']:
        logger.error(f"❌ Error: {workflow_results.get('error')}")
        return
    
    logger.info(f"\n📄 Workflow Output:\n{workflow_results.get('content')}")

    # Verify Airtable data persistence
    ticket_id = workflow_results.get('ticket_id')
    if ticket_id:
        logger.info(f"\n🔍 Verifying Airtable data persistence for Ticket ID: {ticket_id}")
        
        record = airtable_client.get_record(ticket_id)
        if record:
            fields = record.get('fields', {})
            
            logger.info("\n📊 Airtable Record Verification:")
            logger.info("=" * 50)
            
            # Check each field that should be populated by agents
            checks = [
                ("Member Name", "Ahmed Benali"),
                ("CIN / Adhérent ID", "C123456789"),
                ("Channel", "Web"),
                    ("Status", "In progress"),  # Should be "In progress" since workflow is running
                ("Case Status", "In progress"),  # Should be "In progress" since workflow is running
                ("Category", None),  # Should be set by NLPClassifierAgent
                ("Confidence", None),  # Should be set by NLPClassifierAgent
                ("Priority", None),  # Should be set by PriorityScoringAgent
                ("SLA Hours", None),  # Should be set by PriorityScoringAgent
                ("Compliance Status", None),  # Should be set by ComplianceCheckerBot
                ("Compliance Score", None),  # Should be set by ComplianceCheckerBot
                ("DraftResponse", None),  # Should be set by ResolutionGeneratorAgent
                ("Response Quality Score", None),  # Should be set by ResolutionGeneratorAgent
                ("Case Status", None),  # Should be set by CaseManagerAgent
                ("Requires Attention", None),  # Should be set by CaseManagerAgent
            ]
            
            all_passed = True
            for field_name, expected_value in checks:
                actual_value = fields.get(field_name)
                if expected_value is None:
                    # Field should be populated by agents
                    if actual_value is not None and actual_value != "":
                        logger.info(f"✅ {field_name}: {actual_value}")
                    else:
                        logger.error(f"❌ {field_name}: NOT SET (should be populated by agents)")
                        all_passed = False
                else:
                    # Field should match expected value
                    if actual_value == expected_value:
                        logger.info(f"✅ {field_name}: {actual_value}")
                    else:
                        logger.error(f"❌ {field_name}: {actual_value} (expected: {expected_value})")
                        all_passed = False
            
            logger.info("=" * 50)
            if all_passed:
                logger.info("🎉 ALL AGENT OUTPUTS SUCCESSFULLY SAVED TO AIRTABLE!")
            else:
                logger.error("❌ SOME AGENT OUTPUTS NOT SAVED TO AIRTABLE")
            
            # Show full record for debugging
            logger.info(f"\n📋 Full Airtable Record:")
            logger.info(json.dumps(fields, indent=2, ensure_ascii=False))
            
        else:
            logger.error(f"❌ Could not retrieve record {ticket_id} from Airtable")
    else:
        logger.error("❌ No ticket ID returned from workflow")

    logger.info("\n======================================================================")
    logger.info("🎉 Structured Outputs Test Completed!")

if __name__ == "__main__":
    asyncio.run(test_complete_workflow())
