import pdfplumber
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        """Initialize the PDF processor"""
        pass

    def extract_text(self, pdf_path: str) -> Dict[int, str]:
        """
        Extract text from a PDF file, maintaining page structure
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary mapping page numbers to extracted text
        """
        try:
            text_by_page = {}
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        text_by_page[page_num] = text.strip()
                    else:
                        logger.warning(f"No text extracted from page {page_num}")
            
            return text_by_page
        
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            raise

    def get_text_chunks(self, text: str, chunk_size: int = 1000) -> List[str]:
        """
        Split text into chunks for efficient translation
        
        Args:
            text: Text to split
            chunk_size: Maximum size of each chunk
            
        Returns:
            List of text chunks
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_len = len(word)
            if current_length + word_len + 1 <= chunk_size:
                current_chunk.append(word)
                current_length += word_len + 1
            else:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = word_len
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks 