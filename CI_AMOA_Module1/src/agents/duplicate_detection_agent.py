"""
Duplicate Detection Agent for CIMR Claims Automation
Detects duplicate and similar claims using semantic similarity (embeddings)
"""
import json
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from loguru import logger
from openai import AzureOpenAI
import numpy as np

from src.config.settings import settings
from src.utils.airtable_client import airtable_client


class DuplicateDetectionAgent:
    """Agent for detecting duplicate and similar claims using semantic analysis"""

    def __init__(self):
        """Initialize the duplicate detection agent"""
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint
        )
        self.embedding_model = "text-embedding-ada-002"  # Azure OpenAI embedding model

    def check_duplicate(
        self,
        member_id: str,
        message: str,
        category: Optional[str] = None
    ) -> Dict:
        """
        Check if a claim is a duplicate using multiple detection methods

        Args:
            member_id: Member's CIN/ID
            message: Claim message text
            category: Claim category (optional)

        Returns:
            Dict with duplicate detection results
        """
        logger.info(f"🔍 Checking for duplicates - Member: {member_id}")

        try:
            # 1. Get recent claims from the same member
            recent_claims = self._get_recent_claims(member_id, days=30)

            if not recent_claims:
                logger.info("✅ No recent claims found - proceeding")
                return {
                    "is_duplicate": False,
                    "confidence": 1.0,
                    "action": "allow",
                    "reason": "Aucune réclamation récente trouvée",
                    "similar_claims": []
                }

            # 2. Check for exact duplicates (Level 1: < 24h)
            exact_match = self._check_exact_duplicate(message, recent_claims, hours=24)
            if exact_match:
                logger.warning(f"🚫 Exact duplicate found: {exact_match['ticket_id']}")
                return {
                    "is_duplicate": True,
                    "confidence": 1.0,
                    "action": "block",
                    "reason": f"Réclamation identique soumise il y a {exact_match['hours_ago']}h",
                    "duplicate_ticket_id": exact_match['ticket_id'],
                    "similar_claims": [exact_match]
                }

            # 3. Check for semantic similarity (Level 2: < 7 days)
            semantic_match = self._check_semantic_similarity(
                message,
                recent_claims,
                category,
                days=7
            )

            if semantic_match and semantic_match['similarity'] >= 0.85:
                logger.warning(f"⚠️ Similar claim found: {semantic_match['ticket_id']} (similarity: {semantic_match['similarity']:.0%})")
                return {
                    "is_duplicate": True,
                    "confidence": semantic_match['similarity'],
                    "action": "warn",
                    "reason": f"Réclamation très similaire trouvée (similarité: {semantic_match['similarity']:.0%})",
                    "duplicate_ticket_id": semantic_match['ticket_id'],
                    "similar_claims": [semantic_match]
                }

            # 4. Check for abuse patterns
            abuse_check = self._check_abuse_pattern(member_id, recent_claims)
            if abuse_check['is_abuse']:
                logger.warning(f"🚩 Abuse pattern detected: {abuse_check['reason']}")
                return {
                    "is_duplicate": False,
                    "confidence": 0.9,
                    "action": "flag",
                    "reason": abuse_check['reason'],
                    "similar_claims": []
                }

            # 5. No duplicate detected
            logger.info("✅ No duplicates detected - proceeding")
            return {
                "is_duplicate": False,
                "confidence": 1.0,
                "action": "allow",
                "reason": "Nouvelle réclamation légitime",
                "similar_claims": []
            }

        except Exception as e:
            logger.error(f"❌ Duplicate detection failed: {e}")
            # In case of error, allow the claim to proceed
            return {
                "is_duplicate": False,
                "confidence": 0.5,
                "action": "allow",
                "reason": f"Erreur lors de la vérification: {str(e)}",
                "similar_claims": []
            }

    def _get_recent_claims(self, member_id: str, days: int = 30) -> List[Dict]:
        """
        Get recent claims from a member

        Args:
            member_id: Member's CIN/ID
            days: Number of days to look back

        Returns:
            List of recent claims
        """
        try:
            # Get all claims
            all_claims = airtable_client.get_recent_claims_by_member(member_id, days=days)

            logger.info(f"📊 Found {len(all_claims)} recent claims for member {member_id}")
            return all_claims

        except Exception as e:
            logger.error(f"Failed to retrieve recent claims: {e}")
            return []

    def _check_exact_duplicate(
        self,
        message: str,
        claims: List[Dict],
        hours: int = 24
    ) -> Optional[Dict]:
        """
        Check for exact duplicate messages in recent claims

        Args:
            message: New claim message
            claims: List of recent claims
            hours: Time window in hours

        Returns:
            Matching claim info or None
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        for claim in claims:
            # Check if claim is within time window
            created_at = claim.get('created_at')
            if not created_at:
                continue

            try:
                claim_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                if claim_time < cutoff_time:
                    continue
            except:
                continue

            # Calculate text similarity
            claim_message = claim.get('message', '')
            similarity = self._calculate_text_similarity(message, claim_message)

            # If very similar (>95%), consider it a duplicate
            if similarity > 0.95:
                hours_ago = (datetime.now() - claim_time).total_seconds() / 3600
                return {
                    'ticket_id': claim.get('ticket_id'),
                    'similarity': similarity,
                    'hours_ago': round(hours_ago, 1),
                    'message': claim_message,
                    'status': claim.get('status')
                }

        return None

    def _check_semantic_similarity(
        self,
        message: str,
        claims: List[Dict],
        category: Optional[str] = None,
        days: int = 7
    ) -> Optional[Dict]:
        """
        Check for semantically similar claims using embeddings

        Args:
            message: New claim message
            claims: List of recent claims
            category: Claim category (filter by category if provided)
            days: Number of days to look back

        Returns:
            Most similar claim info or None
        """
        try:
            cutoff_time = datetime.now() - timedelta(days=days)

            # Filter claims by time and category
            filtered_claims = []
            for claim in claims:
                created_at = claim.get('created_at')
                if not created_at:
                    continue

                try:
                    claim_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if claim_time < cutoff_time:
                        continue
                except:
                    continue

                # Filter by category if provided
                if category and claim.get('category') != category:
                    continue

                filtered_claims.append(claim)

            if not filtered_claims:
                return None

            # Get embedding for new message
            logger.info("🔮 Generating embedding for new message...")
            new_embedding = self._get_embedding(message)

            # Find most similar claim
            max_similarity = 0.0
            most_similar_claim = None

            for claim in filtered_claims:
                claim_message = claim.get('message', '')
                if not claim_message:
                    continue

                # Get embedding for existing claim
                claim_embedding = self._get_embedding(claim_message)

                # Calculate cosine similarity
                similarity = self._cosine_similarity(new_embedding, claim_embedding)

                if similarity > max_similarity:
                    max_similarity = similarity
                    most_similar_claim = claim

            if most_similar_claim and max_similarity >= 0.75:
                created_at = most_similar_claim.get('created_at', '')
                try:
                    claim_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    days_ago = (datetime.now() - claim_time).days
                except:
                    days_ago = 0

                logger.info(f"🔍 Found similar claim with {max_similarity:.0%} similarity")
                return {
                    'ticket_id': most_similar_claim.get('ticket_id'),
                    'similarity': max_similarity,
                    'days_ago': days_ago,
                    'message': most_similar_claim.get('message'),
                    'category': most_similar_claim.get('category'),
                    'status': most_similar_claim.get('status')
                }

            return None

        except Exception as e:
            logger.error(f"Semantic similarity check failed: {e}")
            return None

    def _check_abuse_pattern(self, member_id: str, claims: List[Dict]) -> Dict:
        """
        Check for abuse patterns

        Args:
            member_id: Member's CIN/ID
            claims: List of recent claims

        Returns:
            Dict with abuse detection results
        """
        # Count claims by time period
        now = datetime.now()
        count_today = 0
        count_week = 0

        for claim in claims:
            created_at = claim.get('created_at')
            if not created_at:
                continue

            try:
                claim_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

                if (now - claim_time).days == 0:
                    count_today += 1
                if (now - claim_time).days <= 7:
                    count_week += 1
            except:
                continue

        # Check thresholds
        if count_today >= 5:
            return {
                "is_abuse": True,
                "reason": f"Trop de réclamations aujourd'hui ({count_today} réclamations)",
                "action": "flag"
            }

        if count_week >= 15:
            return {
                "is_abuse": True,
                "reason": f"Trop de réclamations cette semaine ({count_week} réclamations)",
                "action": "flag"
            }

        return {"is_abuse": False}

    def _get_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding vector for text using Azure OpenAI

        Args:
            text: Text to embed

        Returns:
            Embedding vector as numpy array
        """
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.embedding_model
            )
            embedding = response.data[0].embedding
            return np.array(embedding)

        except Exception as e:
            logger.error(f"Failed to get embedding: {e}")
            # Return random embedding to avoid breaking the flow
            return np.random.rand(1536)  # text-embedding-ada-002 dimension

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity (0 to 1)
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate text similarity using sequence matching

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0 to 1)
        """
        # Normalize texts
        text1_normalized = text1.lower().strip()
        text2_normalized = text2.lower().strip()

        # Use SequenceMatcher for similarity
        similarity = SequenceMatcher(None, text1_normalized, text2_normalized).ratio()

        return similarity


# Singleton instance
duplicate_detection_agent = DuplicateDetectionAgent()
