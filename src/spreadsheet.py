from google.oauth2 import service_account
from googleapiclient.discovery import build
from typing import List, Dict, Any
import logging
from config import Config

logger = logging.getLogger(__name__)

class SpreadsheetManager:
    def __init__(self, spreadsheet_id: str):
        """
        Initialize the spreadsheet manager
        
        Args:
            spreadsheet_id: ID of the Google Spreadsheet to work with
        """
        self.spreadsheet_id = spreadsheet_id
        self.service = self._create_sheets_service()

    def _create_sheets_service(self):
        """Create and return an authorized Sheets API service instance"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                Config.GOOGLE_APPLICATION_CREDENTIALS,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            return build('sheets', 'v4', credentials=credentials)
        except Exception as e:
            logger.error(f"Failed to create Sheets service: {str(e)}")
            raise

    def read_vessel_names(self, range_name: str) -> List[str]:
        """
        Read vessel names from the spreadsheet
        
        Args:
            range_name: A1 notation of the range to read
            
        Returns:
            List of vessel names
        """
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            return [row[0] for row in values if row]  # Assuming vessel names are in first column
        
        except Exception as e:
            logger.error(f"Error reading vessel names: {str(e)}")
            raise

    def update_matches(self, updates: List[Dict[str, Any]]):
        """
        Update spreadsheet with matching results
        
        Args:
            updates: List of dictionaries containing vessel name and matching report links
        """
        try:
            data = []
            for update in updates:
                data.append({
                    'range': update['range'],
                    'values': [[update['link']]]
                })

            body = {
                'valueInputOption': 'USER_ENTERED',
                'data': data
            }

            self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()
            
        except Exception as e:
            logger.error(f"Error updating spreadsheet: {str(e)}")
            raise 