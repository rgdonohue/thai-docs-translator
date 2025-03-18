import logging
from pathlib import Path
import os
from typing import List, Dict
from tqdm import tqdm
import sys

from config import Config
from pdf_processor import PDFProcessor
from translator import Translator
from search import VesselSearch
from csv_processor import CSVProcessor
from setup_validator import SetupValidator
from auth import AuthenticationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/processing.log')
    ]
)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, csv_path: str):
        """Initialize all components"""
        try:
            # Validate setup first
            validator = SetupValidator()
            if not validator.run_all_validations():
                raise RuntimeError("Setup validation failed. Please fix the issues and try again.")
            
            Config.validate()
            self.pdf_processor = PDFProcessor()
            self.translator = Translator()
            self.vessel_search = VesselSearch()
            self.csv_processor = CSVProcessor(csv_path)
            
        except AuthenticationError as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            raise

    def process_document(self, pdf_path: str, output_path: str) -> str:
        """
        Process a single document: extract text, translate, and save
        
        Args:
            pdf_path: Path to the PDF file
            output_path: Path to save the translated text
            
        Returns:
            Path to the translated text file
        """
        try:
            # Extract text
            logger.info(f"Processing {pdf_path}")
            text_by_page = self.pdf_processor.extract_text(pdf_path)
            
            if not text_by_page:
                logger.warning(f"No text extracted from {pdf_path}")
                return None
            
            # Translate
            logger.info("Translating document")
            translated_pages = self.translator.translate_document(text_by_page)
            
            # Save translated text
            self._save_translation(translated_pages, output_path)
            return output_path
            
        except Exception as e:
            logger.error(f"Error processing document {pdf_path}: {str(e)}")
            return None

    def _save_translation(self, translated_pages: Dict[int, str], output_path: str):
        """Save translated text to file"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                for page_num in sorted(translated_pages.keys()):
                    f.write(f"--- Page {page_num} ---\n")
                    f.write(translated_pages[page_num])
                    f.write('\n\n')
        except Exception as e:
            logger.error(f"Failed to save translation to {output_path}: {str(e)}")
            raise

def main():
    try:
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Initialize processor with CSV file
        csv_path = 'input_data/fishing-vessels.csv'
        processor = DocumentProcessor(csv_path)
        
        # Process all PDFs in the input directory
        input_dir = "input_pdfs"
        output_dir = "translated_pdfs"
        
        pdf_files = list(Path(input_dir).glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF files found in {input_dir}")
            return
        
        # Process and translate PDFs
        failed_files = []
        for pdf_file in tqdm(pdf_files, desc="Processing documents"):
            try:
                output_path = Path(output_dir) / f"translated_{pdf_file.name}.txt"
                if processor.process_document(str(pdf_file), str(output_path)) is None:
                    failed_files.append(pdf_file.name)
            
            except Exception as e:
                logger.error(f"Failed to process {pdf_file.name}: {str(e)}")
                failed_files.append(pdf_file.name)
        
        # Search for vessel names in translated files
        logger.info("Searching for vessel matches...")
        vessel_names = processor.csv_processor.get_vessel_names()
        matches = processor.vessel_search.search_translated_files(output_dir, vessel_names)
        
        # Update CSV with matches
        if matches:
            logger.info(f"Found matches for {len(matches)} vessels")
            processor.csv_processor.update_matches(matches)
        else:
            logger.warning("No vessel matches found in any document")
        
        # Report results
        logger.info(f"\nProcessing complete:")
        logger.info(f"- Successfully processed: {len(pdf_files) - len(failed_files)} files")
        logger.info(f"- Vessels with matches: {len(matches)}")
        logger.info(f"- Failed files: {len(failed_files)}")
        
        if failed_files:
            logger.error("Failed files:")
            for file in failed_files:
                logger.error(f"  - {file}")
        
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 