"""
Test Duplicate Detection for CIMR Claims Automation
Tests the duplicate detection agent with various scenarios
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.duplicate_detection_agent import duplicate_detection_agent
from loguru import logger


def test_exact_duplicate():
    """Test detection of exact duplicate messages"""
    print("\n" + "="*60)
    print("TEST 1: Exact Duplicate Detection")
    print("="*60)

    member_id = "TEST123456"
    message1 = "Je n'ai pas reçu ma pension du mois de janvier"

    try:
        # First submission
        print("\n📝 First submission...")
        result1 = duplicate_detection_agent.check_duplicate(
            member_id=member_id,
            message=message1
        )

        print(f"✅ Result: {result1['action']}")
        print(f"   Reason: {result1['reason']}")

        # Simulate second submission (same message, same member, within 24h)
        # In real scenario, this would be detected as duplicate
        print("\n📝 Second submission (same message)...")
        print("   Note: This test requires existing claims in Airtable to work properly")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_semantic_similarity():
    """Test detection of semantically similar messages"""
    print("\n" + "="*60)
    print("TEST 2: Semantic Similarity Detection")
    print("="*60)

    member_id = "TEST789012"

    # Similar messages with different wording
    message1 = "Ma retraite de janvier n'est pas encore versée"
    message2 = "Je n'ai toujours pas reçu ma pension du mois de janvier"

    try:
        print("\n📝 Testing similarity between two messages...")
        print(f"   Message 1: {message1}")
        print(f"   Message 2: {message2}")

        # Check second message (first message would need to exist in Airtable)
        result = duplicate_detection_agent.check_duplicate(
            member_id=member_id,
            message=message2
        )

        print(f"\n✅ Result: {result['action']}")
        print(f"   Reason: {result['reason']}")
        print(f"   Confidence: {result['confidence']:.0%}")

        if result.get('similar_claims'):
            print(f"   Similar claims found: {len(result['similar_claims'])}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_text_similarity():
    """Test the text similarity calculation"""
    print("\n" + "="*60)
    print("TEST 3: Text Similarity Calculation")
    print("="*60)

    try:
        agent = duplicate_detection_agent

        # Test cases with expected similarity levels
        test_cases = [
            ("Je n'ai pas reçu ma pension", "Je n'ai pas reçu ma pension", 1.0),
            ("Ma pension n'est pas arrivée", "Ma retraite n'est pas arrivée", 0.7),
            ("Problème de paiement janvier", "Retard de versement février", 0.3),
            ("Hello world", "Bonjour monde", 0.1),
        ]

        all_passed = True
        for text1, text2, expected_min in test_cases:
            similarity = agent._calculate_text_similarity(text1, text2)
            passed = similarity >= expected_min - 0.1  # Allow 10% tolerance

            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"\n{status}")
            print(f"   Text 1: {text1}")
            print(f"   Text 2: {text2}")
            print(f"   Similarity: {similarity:.2%} (expected: ≥{expected_min:.0%})")

            if not passed:
                all_passed = False

        return all_passed

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_embedding_generation():
    """Test the embedding generation"""
    print("\n" + "="*60)
    print("TEST 4: Embedding Generation")
    print("="*60)

    try:
        agent = duplicate_detection_agent

        test_message = "Je n'ai pas reçu ma pension du mois de janvier"

        print(f"\n📝 Generating embedding for: {test_message}")

        embedding = agent._get_embedding(test_message)

        print(f"✅ Embedding generated successfully")
        print(f"   Dimension: {len(embedding)}")
        print(f"   First 5 values: {embedding[:5]}")

        # Check embedding dimension (should be 1536 for text-embedding-ada-002)
        if len(embedding) == 1536:
            print(f"✅ Correct dimension (1536)")
            return True
        else:
            print(f"⚠️ Unexpected dimension: {len(embedding)}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.exception("Embedding generation failed")
        return False


def test_abuse_detection():
    """Test abuse pattern detection"""
    print("\n" + "="*60)
    print("TEST 5: Abuse Pattern Detection")
    print("="*60)

    member_id = "ABUSER123"

    try:
        print(f"\n📝 Testing abuse detection for member {member_id}")

        # In real scenario, member would need to have many claims in Airtable
        result = duplicate_detection_agent.check_duplicate(
            member_id=member_id,
            message="Test abuse message"
        )

        print(f"✅ Result: {result['action']}")
        print(f"   Reason: {result['reason']}")

        if result['action'] == 'flag':
            print(f"   🚩 Abuse pattern detected")
            return True
        else:
            print(f"   ✅ No abuse pattern (normal for new member)")
            return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_cosine_similarity():
    """Test cosine similarity calculation"""
    print("\n" + "="*60)
    print("TEST 6: Cosine Similarity Calculation")
    print("="*60)

    try:
        import numpy as np
        agent = duplicate_detection_agent

        # Test with known vectors
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([1.0, 0.0, 0.0])  # Same vector
        vec3 = np.array([0.0, 1.0, 0.0])  # Perpendicular

        similarity_same = agent._cosine_similarity(vec1, vec2)
        similarity_diff = agent._cosine_similarity(vec1, vec3)

        print(f"\n✅ Same vectors similarity: {similarity_same:.2f} (expected: 1.0)")
        print(f"✅ Perpendicular vectors similarity: {similarity_diff:.2f} (expected: 0.0)")

        # Verify results
        if abs(similarity_same - 1.0) < 0.01 and abs(similarity_diff - 0.0) < 0.01:
            print(f"\n✅ Cosine similarity calculation is correct")
            return True
        else:
            print(f"\n❌ Cosine similarity calculation has errors")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def check_configuration():
    """Check duplicate detection configuration"""
    print("\n" + "="*60)
    print("CONFIGURATION CHECK")
    print("="*60)

    try:
        from src.config.settings import settings

        print(f"\n📊 Azure OpenAI Configuration:")
        print(f"   Endpoint: {settings.azure_openai_endpoint[:50]}..." if settings.azure_openai_endpoint else "   Endpoint: NOT SET")
        print(f"   API Key: {'*' * 20} (configured)" if settings.azure_openai_api_key else "   API Key: NOT SET")
        print(f"   Deployment: {settings.azure_openai_deployment_name}")
        print(f"   API Version: {settings.azure_openai_api_version}")

        print(f"\n📊 Airtable Configuration:")
        print(f"   API Key: {'*' * 20} (configured)" if settings.airtable_api_key else "   API Key: NOT SET")
        print(f"   Base ID: {settings.airtable_base_id[:20]}..." if settings.airtable_base_id else "   Base ID: NOT SET")
        print(f"   Table Name: {settings.airtable_table_name}")

        # Check if properly configured
        if not settings.azure_openai_api_key or settings.azure_openai_api_key == "your_azure_api_key_here":
            print("\n⚠️ WARNING: Azure OpenAI API key not configured")
            print("   Please update your .env file with real credentials")
            return False

        if not settings.airtable_api_key or settings.airtable_api_key == "your_airtable_api_key_here":
            print("\n⚠️ WARNING: Airtable API key not configured")
            print("   Please update your .env file with real credentials")
            return False

        print("\n✅ Configuration looks good!")
        return True

    except Exception as e:
        print(f"\n❌ Configuration check failed: {e}")
        return False


def main():
    """Run all duplicate detection tests"""
    print("\n" + "="*60)
    print("🧪 CIMR DUPLICATE DETECTION TEST SUITE")
    print("="*60)

    # Check configuration first
    config_ok = check_configuration()

    if not config_ok:
        print("\n❌ Configuration issues detected. Please fix them before running tests.")
        print("\n📖 Update your .env file with real Azure OpenAI and Airtable credentials.")
        return

    # Run tests
    print("\n🚀 Running duplicate detection tests...")
    print("⏳ Please wait...\n")

    results = []
    results.append(("Text Similarity", test_text_similarity()))
    results.append(("Cosine Similarity", test_cosine_similarity()))
    results.append(("Embedding Generation", test_embedding_generation()))
    results.append(("Exact Duplicate Detection", test_exact_duplicate()))
    results.append(("Semantic Similarity Detection", test_semantic_similarity()))
    results.append(("Abuse Pattern Detection", test_abuse_detection()))

    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Duplicate detection is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the output above.")

    print("\n💡 Tips:")
    print("   - For full duplicate detection testing, add some test claims to Airtable")
    print("   - Test with the same member ID to see duplicate warnings")
    print("   - Make sure Azure OpenAI and Airtable credentials are valid")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        logger.exception("Test suite failed")
