from fuzzywuzzy import fuzz
from typing import List, Dict, Tuple
import logging
from pathlib import Path
import re

logger = logging.getLogger(__name__)

class VesselSearch:
    def __init__(self, threshold: int = 85):
        """
        Initialize vessel search with matching threshold
        
        Args:
            threshold: Minimum fuzzy match score (0-100)
        """
        self.threshold = threshold

    def find_vessel_matches(self, text: str, vessel_names: List[Tuple[str, str]]) -> List[str]:
        """
        Search for vessel names in text
        
        Args:
            text: Text to search in
            vessel_names: List of (english_name, thai_name) tuples
            
        Returns:
            List of matched vessel names
        """
        matches = set()
        text_lower = text.lower()
        
        for eng_name, thai_name in vessel_names:
            # Clean and prepare names
            eng_name = eng_name.strip()
            thai_name = thai_name.strip()
            
            # Skip empty names
            if not eng_name and not thai_name:
                continue
                
            # Try exact matching first
            if eng_name and eng_name.lower() in text_lower:
                matches.add(eng_name)
            if thai_name and thai_name in text:  # Thai text comparison
                matches.add(eng_name or thai_name)
                
            # Try fuzzy matching for English names
            if eng_name:
                words = text_lower.split()
                for word in words:
                    if len(word) > 3:  # Only check words longer than 3 characters
                        score = fuzz.ratio(eng_name.lower(), word)
                        if score >= self.threshold:
                            matches.add(eng_name)
                            break
        
        return list(matches)

    def search_translated_files(self, translated_dir: str, vessel_names: List[Tuple[str, str]]) -> Dict[str, List[str]]:
        """
        Search all translated files for vessel names
        
        Args:
            translated_dir: Directory containing translated files
            vessel_names: List of (english_name, thai_name) tuples
            
        Returns:
            Dictionary mapping vessel names to lists of file paths
        """
        matches = {}
        translated_path = Path(translated_dir)
        
        try:
            for file_path in translated_path.glob('*.txt'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Find matches in this file
                    file_matches = self.find_vessel_matches(content, vessel_names)
                    
                    # Record matches
                    for vessel_name in file_matches:
                        if vessel_name not in matches:
                            matches[vessel_name] = []
                        # Store original PDF name (remove 'translated_' prefix and '.txt' suffix)
                        original_pdf = file_path.name.replace('translated_', '').replace('.txt', '.pdf')
                        matches[vessel_name].append(original_pdf)
                        
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error accessing translated directory: {str(e)}")
            raise
            
        return matches 