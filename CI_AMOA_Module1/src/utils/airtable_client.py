"""
Airtable client for CIMR Claims Automation v1
"""
from typing import Dict, List, Optional, Any
import requests
from loguru import logger
from src.config import settings


class AirtableClient:
    """Client for interacting with Airtable API"""
    
    def __init__(self):
        self.api_key = settings.airtable_api_key
        self.base_id = settings.airtable_base_id
        self.table_name = settings.airtable_table_name
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_record(self, fields: Dict[str, Any]) -> Optional[Dict]:
        """Create a new record in Airtable"""
        try:
            data = {"fields": fields}
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            logger.info(f"Created record in Airtable: {response.json().get('id')}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating Airtable record: {e}")
            return None
    
    def get_record(self, record_id: str) -> Optional[Dict]:
        """Get a specific record by ID"""
        try:
            response = requests.get(
                f"{self.base_url}/{record_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting Airtable record {record_id}: {e}")
            return None
    
    def update_record(self, record_id: str, fields: Dict[str, Any]) -> Optional[Dict]:
        """Update a record in Airtable"""
        try:
            data = {"fields": fields}
            response = requests.patch(
                f"{self.base_url}/{record_id}",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            logger.info(f"Updated Airtable record: {record_id}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating Airtable record {record_id}: {e}")
            return None
    
    def list_records(self, filter_formula: Optional[str] = None, max_records: int = 100) -> List[Dict]:
        """List records from Airtable with optional filtering"""
        try:
            params = {"maxRecords": max_records}
            if filter_formula:
                params["filterByFormula"] = filter_formula
            
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Retrieved {len(data.get('records', []))} records from Airtable")
            return data.get("records", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Error listing Airtable records: {e}")
            return []
    
    def search_records(self, field: str, value: str) -> List[Dict]:
        """Search records by field value"""
        filter_formula = f"{{{field}}} = '{value}'"
        return self.list_records(filter_formula=filter_formula)

    def get_recent_claims_by_member(self, member_id: str, days: int = 30) -> List[Dict]:
        """
        Get recent claims from a specific member

        Args:
            member_id: Member's CIN/ID
            days: Number of days to look back

        Returns:
            List of recent claims with standardized format
        """
        try:
            # Create filter formula for Airtable
            # Filter by member ID and created date (last N days)
            filter_formula = f"{{CIN / Adhérent ID}} = '{member_id}'"

            logger.info(f"🔍 Fetching recent claims for member {member_id} (last {days} days)")

            records = self.list_records(filter_formula=filter_formula, max_records=100)

            # Transform Airtable records to standardized format
            claims = []
            for record in records:
                fields = record.get('fields', {})

                claim = {
                    'ticket_id': record.get('id'),
                    'member_id': fields.get('CIN / Adhérent ID'),
                    'member_name': fields.get('Member Name'),
                    'message': fields.get('Message', ''),
                    'category': fields.get('Category'),
                    'status': fields.get('Status', 'New'),
                    'created_at': fields.get('Created At'),
                    'priority': fields.get('Priority'),
                    'channel': fields.get('Channel')
                }
                claims.append(claim)

            logger.info(f"✅ Found {len(claims)} claims for member {member_id}")
            return claims

        except Exception as e:
            logger.error(f"Error fetching recent claims for member {member_id}: {e}")
            return []


# Global Airtable client instance
airtable_client = AirtableClient()
