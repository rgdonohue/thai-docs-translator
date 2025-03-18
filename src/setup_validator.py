import os
import sys
from pathlib import Path
from typing import List, Dict
import logging
from dotenv import load_dotenv
from auth import GoogleServiceAuthenticator, AuthenticationError
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SetupValidator:
    def __init__(self):
        """Initialize validator"""
        self.errors: List[str] = []
        self.warnings: List[str] = []
        load_dotenv()

    def validate_environment(self) -> bool:
        """Validate environment variables and paths"""
        required_vars = {
            'GOOGLE_CLOUD_PROJECT': 'Google Cloud Project ID',
            'GOOGLE_APPLICATION_CREDENTIALS': 'Path to credentials file',
            'VESSEL_SPREADSHEET_ID': 'Google Sheets spreadsheet ID',
            'REPORTS_FOLDER_ID': 'Google Drive folder ID'
        }
        
        for var, description in required_vars.items():
            value = os.getenv(var)
            if not value:
                self.errors.append(f"Missing environment variable: {var} ({description})")
            elif var == 'GOOGLE_APPLICATION_CREDENTIALS':
                if not os.path.exists(value):
                    self.errors.append(f"Credentials file not found at: {value}")

        return len(self.errors) == 0

    def validate_folder_structure(self) -> bool:
        """Validate required folders exist"""
        required_folders = ['input_pdfs', 'translated_pdfs', 'logs']
        
        for folder in required_folders:
            if not os.path.exists(folder):
                try:
                    os.makedirs(folder)
                    logger.info(f"Created missing folder: {folder}")
                except Exception as e:
                    self.errors.append(f"Failed to create folder {folder}: {str(e)}")
        
        return len(self.errors) == 0

    def validate_credentials(self) -> bool:
        """Validate Google credentials and API access"""
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
        
        try:
            # Validate credentials file structure
            GoogleServiceAuthenticator.validate_credentials_file(creds_path)
            
            # Test Translation API
            trans_success, trans_message = GoogleServiceAuthenticator.test_translation_api()
            if not trans_success:
                self.errors.append(trans_message)
            
            # Test Sheets API
            sheets_success, sheets_message = GoogleServiceAuthenticator.test_sheets_api()
            if not sheets_success:
                self.errors.append(sheets_message)
            
            # Get service account email for user information
            service_email = GoogleServiceAuthenticator.get_service_account_email(creds_path)
            if service_email:
                logger.info(f"Service account email: {service_email}")
                logger.info("Make sure this email has access to your spreadsheet and Drive folder")
            
        except AuthenticationError as e:
            self.errors.append(str(e))
            return False
        
        return len(self.errors) == 0

    def validate_dependencies(self) -> bool:
        """Validate Python dependencies"""
        required_packages = {
            'google-cloud-translate': '3.12.0',
            'google-api-python-client': '2.108.0',
            'pdfplumber': '0.10.3',
            'python-dotenv': '1.0.0'
        }
        
        import pkg_resources
        
        for package, version in required_packages.items():
            try:
                installed = pkg_resources.get_distribution(package)
                if installed.version != version:
                    self.warnings.append(
                        f"Package version mismatch: {package} "
                        f"(installed: {installed.version}, required: {version})"
                    )
            except pkg_resources.DistributionNotFound:
                self.errors.append(f"Missing required package: {package}")
        
        return len(self.errors) == 0

    def run_all_validations(self) -> bool:
        """Run all validation checks"""
        logger.info("Starting setup validation...")
        
        validations = [
            (self.validate_environment, "Environment variables"),
            (self.validate_folder_structure, "Folder structure"),
            (self.validate_credentials, "Google credentials"),
            (self.validate_dependencies, "Dependencies")
        ]
        
        all_passed = True
        for validation_func, description in validations:
            try:
                logger.info(f"\nChecking {description}...")
                if not validation_func():
                    all_passed = False
            except Exception as e:
                self.errors.append(f"Error during {description} validation: {str(e)}")
                all_passed = False
        
        self._print_results()
        return all_passed

    def _print_results(self):
        """Print validation results"""
        if self.errors:
            logger.error("\n❌ Validation failed with the following errors:")
            for error in self.errors:
                logger.error(f"  • {error}")
        
        if self.warnings:
            logger.warning("\n⚠️ Validation succeeded with warnings:")
            for warning in self.warnings:
                logger.warning(f"  • {warning}")
        
        if not self.errors and not self.warnings:
            logger.info("\n✅ All validations passed successfully!")

def main():
    validator = SetupValidator()
    if not validator.run_all_validations():
        sys.exit(1)

if __name__ == "__main__":
    main() 