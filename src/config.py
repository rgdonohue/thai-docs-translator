import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Google Cloud settings
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    # File paths
    VESSEL_SPREADSHEET_ID = os.getenv('VESSEL_SPREADSHEET_ID')
    REPORTS_FOLDER_ID = os.getenv('REPORTS_FOLDER_ID')
    
    # Processing settings
    TRANSLATION_BATCH_SIZE = 1000  # characters
    FUZZY_MATCH_THRESHOLD = 80     # minimum score for fuzzy matching
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present"""
        required_vars = [
            'GOOGLE_CLOUD_PROJECT',
            'GOOGLE_APPLICATION_CREDENTIALS',
            'VESSEL_SPREADSHEET_ID',
            'REPORTS_FOLDER_ID'
        ]
        
        missing = [var for var in required_vars if not getattr(cls, var)]
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}") 