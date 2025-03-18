import pandas as pd
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class CSVProcessor:
    def __init__(self, csv_path: str):
        """
        Initialize CSV processor
        
        Args:
            csv_path: Path to the vessels CSV file
        """
        self.csv_path = csv_path
        self.df = pd.read_csv(csv_path)
        
    def get_vessel_names(self) -> List[Tuple[str, str]]:
        """
        Get list of vessel names (both English and Thai)
        
        Returns:
            List of tuples containing (english_name, thai_name)
        """
        return list(zip(
            self.df['Vessel Name'].fillna(''),
            self.df['Thai name'].fillna('')
        ))
    
    def update_matches(self, matches: Dict[str, List[str]]):
        """
        Update CSV with matching report links
        
        Args:
            matches: Dictionary mapping vessel names to lists of report links
        """
        try:
            # Create a mapping of vessel name to report links
            for vessel_name, report_links in matches.items():
                # Find all rows that match this vessel name (in either English or Thai)
                mask = (self.df['Vessel Name'] == vessel_name) | (self.df['Thai name'] == vessel_name)
                
                if mask.any():
                    # Join multiple links with semicolon if there are multiple matches
                    links_str = '; '.join(report_links)
                    self.df.loc[mask, 'Link to report which mentions'] = links_str
            
            # Save the updated DataFrame back to CSV
            self.df.to_csv(self.csv_path, index=False)
            logger.info(f"Updated {len(matches)} vessels in CSV file")
            
        except Exception as e:
            logger.error(f"Failed to update CSV file: {str(e)}")
            raise 