from fuzzywuzzy import fuzz
from typing import List, Dict, Tuple
import logging
from config import Config

logger = logging.getLogger(__name__)

class VesselSearch:
    def __init__(self, threshold: int = Config.FUZZY_MATCH_THRESHOLD):
        """
        Initialize the vessel search with a matching threshold
        
        Args:
            threshold: Minimum fuzzy match score (0-100) to consider a match
        """
        self.threshold = threshold

    def find_matches(self, text: str, vessel_names: List[str]) -> List[Tuple[str, int, int]]:
        """
        Search for vessel names in text using fuzzy matching
        
        Args:
            text: Text to search in
            vessel_names: List of vessel names to search for
            
        Returns:
            List of tuples containing (vessel_name, score, position)
        """
        matches = []
        text_lower = text.lower()
        
        for vessel_name in vessel_names:
            vessel_lower = vessel_name.lower()
            
            # First try exact matching
            if vessel_lower in text_lower:
                position = text_lower.index(vessel_lower)
                matches.append((vessel_name, 100, position))
                continue
            
            # Try fuzzy matching on word boundaries
            words = text_lower.split()
            for i, word in enumerate(words):
                score = fuzz.ratio(vessel_lower, word)
                if score >= self.threshold:
                    # Calculate position by counting characters up to this word
                    position = len(' '.join(words[:i]))
                    matches.append((vessel_name, score, position))
        
        # Sort by score descending, then position
        return sorted(matches, key=lambda x: (-x[1], x[2]))

    def search_document(self, text_by_page: Dict[int, str], vessel_names: List[str]) -> Dict[int, List[Tuple[str, int, int]]]:
        """
        Search for vessel names across all pages of a document
        
        Args:
            text_by_page: Dictionary mapping page numbers to text content
            vessel_names: List of vessel names to search for
            
        Returns:
            Dictionary mapping page numbers to lists of matches
        """
        results = {}
        for page_num, text in text_by_page.items():
            matches = self.find_matches(text, vessel_names)
            if matches:
                results[page_num] = matches
        return results 