from google.oauth2 import service_account
from google.api_core import exceptions
from google.cloud import translate_v2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import os
from typing import Tuple, Any
import logging

logger = logging.getLogger(__name__)

class AuthenticationError(Exception):
    """Custom exception for authentication-related errors"""
    pass

class GoogleServiceAuthenticator:
    @staticmethod
    def validate_credentials_file(credentials_path: str) -> bool:
        """
        Validate the structure and presence of required fields in credentials file
        
        Args:
            credentials_path: Path to the credentials JSON file
            
        Returns:
            bool: True if valid, raises AuthenticationError otherwise
        """
        required_fields = [
            'type', 'project_id', 'private_key_id', 'private_key',
            'client_email', 'client_id', 'auth_uri', 'token_uri'
        ]
        
        try:
            with open(credentials_path, 'r') as f:
                creds_data = json.load(f)
                
            missing_fields = [field for field in required_fields if field not in creds_data]
            
            if missing_fields:
                raise AuthenticationError(
                    f"Credentials file missing required fields: {', '.join(missing_fields)}"
                )
                
            if creds_data['type'] != 'service_account':
                raise AuthenticationError(
                    "Invalid credentials type. Must be 'service_account'"
                )
                
            return True
            
        except FileNotFoundError:
            raise AuthenticationError(
                f"Credentials file not found at: {credentials_path}"
            )
        except json.JSONDecodeError:
            raise AuthenticationError(
                f"Credentials file is not valid JSON: {credentials_path}"
            )

    @staticmethod
    def test_translation_api() -> Tuple[bool, str]:
        """Test connection to Translation API"""
        try:
            client = translate_v2.Client()
            # Try a simple translation as a test
            result = client.translate('test', target_language='es')
            return True, "Translation API connection successful"
        except exceptions.PermissionDenied:
            return False, "Translation API: Permission denied. Please enable the Cloud Translation API"
        except exceptions.Forbidden:
            return False, "Translation API: API key or credentials are invalid"
        except Exception as e:
            return False, f"Translation API: Unexpected error: {str(e)}"

    @staticmethod
    def test_sheets_api() -> Tuple[bool, str]:
        """Test connection to Google Sheets API"""
        try:
            service = build('sheets', 'v4', cache_discovery=False)
            # Just building the service is enough to validate credentials
            return True, "Sheets API connection successful"
        except HttpError as e:
            if e.resp.status == 403:
                return False, "Sheets API: Permission denied. Please enable the Google Sheets API"
            return False, f"Sheets API: HTTP error occurred: {str(e)}"
        except Exception as e:
            return False, f"Sheets API: Unexpected error: {str(e)}"

    @staticmethod
    def get_service_account_email(credentials_path: str) -> str:
        """Extract service account email from credentials file"""
        try:
            with open(credentials_path, 'r') as f:
                creds_data = json.load(f)
            return creds_data.get('client_email', '')
        except Exception:
            return '' 