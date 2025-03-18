#!/usr/bin/env python3
"""
Vessel Search Script

This script searches for vessel names in translated files (or PDFs if needed)
and updates the fishing-vessels.csv file with matching reports.
"""

import pandas as pd
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set
import re
from fuzzywuzzy import fuzz
from tqdm import tqdm
import shutil
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/search.log')
    ]
)
logger = logging.getLogger(__name__)

def setup_directories():
    """Create necessary directories"""
    os.makedirs('logs', exist_ok=True)
    os.makedirs('output_data', exist_ok=True)

def load_vessel_data(csv_path: str) -> Tuple[pd.DataFrame, List[Tuple[str, str]]]:
    """
    Load vessel data from CSV
    
    Args:
        csv_path: Path to the vessels CSV file
        
    Returns:
        Tuple of (DataFrame, List of vessel name tuples)
    """
    try:
        df = pd.read_csv(csv_path)
        # Extract vessel names (English and Thai)
        vessel_names = list(zip(
            df['Vessel Name'].fillna('').astype(str),
            df['Thai name'].fillna('').astype(str)
        ))
        return df, vessel_names
    except Exception as e:
        logger.error(f"Failed to load CSV: {str(e)}")
        raise

def normalize_vessel_name(name: str) -> str:
    """
    Normalize vessel name for more consistent matching
    
    Args:
        name: Vessel name to normalize
        
    Returns:
        Normalized vessel name
    """
    if not name:
        return ""
    
    # Convert to lowercase
    name = name.lower()
    
    # Remove extra spaces
    name = re.sub(r'\s+', ' ', name).strip()
    
    # Handle common variations in vessel naming
    name = name.replace(".", "")  # Remove periods
    
    return name

def find_vessel_matches(text: str, vessel_names: List[Tuple[str, str]], threshold: int = 85) -> Set[str]:
    """
    Search for vessel names in text
    
    Args:
        text: Text to search in
        vessel_names: List of (english_name, thai_name) tuples
        threshold: Fuzzy match threshold
        
    Returns:
        Set of matched vessel names
    """
    matches = set()
    text_lower = text.lower()
    
    # For exact matching, prepare a normalized version of the text
    normalized_text = normalize_vessel_name(text)
    
    for eng_name, thai_name in vessel_names:
        # Clean and prepare names
        eng_name_orig = eng_name.strip()
        thai_name = thai_name.strip()
        
        # Skip empty names
        if not eng_name_orig and not thai_name:
            continue
        
        # Normalize English name for matching
        eng_name = normalize_vessel_name(eng_name_orig)
        
        # Try exact matching with normalized names first
        if eng_name and eng_name in normalized_text:
            matches.add(eng_name_orig)
            continue
            
        # Try exact matching with original case
        if eng_name_orig and eng_name_orig.lower() in text_lower:
            matches.add(eng_name_orig)
            continue
            
        # Thai text comparison
        if thai_name and thai_name in text:
            matches.add(eng_name_orig or thai_name)
            continue
        
        # For English names, try phrase matching (handles multi-word vessel names better)
        if eng_name and len(eng_name) > 3:
            # Look for exact phrases
            if re.search(r'\b' + re.escape(eng_name) + r'\b', normalized_text):
                matches.add(eng_name_orig)
                continue
                
            # Try fuzzy matching as last resort
            for phrase in re.findall(r'\b\w+(?:\s+\w+){0,3}\b', normalized_text):
                if len(phrase) > 3:  # Only check phrases with significant length
                    score = fuzz.ratio(eng_name, phrase)
                    if score >= threshold:
                        matches.add(eng_name_orig)
                        break
    
    return matches

def search_translated_files(translated_dir: str, vessel_names: List[Tuple[str, str]]) -> Dict[str, List[str]]:
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
    
    # Get all text files in directory
    text_files = list(translated_path.glob('*.txt'))
    
    # If no text files, try getting PDF files
    if not text_files:
        logger.warning(f"No text files found in {translated_dir}. Attempting to search PDFs directly.")
        text_files = list(translated_path.glob('*.pdf'))
        if not text_files:
            logger.error(f"No text or PDF files found in {translated_dir}")
            return {}
    
    # Search each file
    for file_path in tqdm(text_files, desc="Searching files"):
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Find matches in this file
            file_matches = find_vessel_matches(content, vessel_names)
            
            # Record matches
            for vessel_name in file_matches:
                if vessel_name not in matches:
                    matches[vessel_name] = []
                
                # Get original filename without path and any prefixes
                if file_path.name.startswith('translated_'):
                    original_name = file_path.name.replace('translated_', '', 1)
                    if original_name.endswith('.txt'):
                        original_name = original_name[:-4]  # Remove .txt extension
                    if not original_name.endswith('.pdf'):
                        original_name += '.pdf'  # Ensure .pdf extension
                else:
                    original_name = file_path.name
                
                matches[vessel_name].append(original_name)
                
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            continue
            
    return matches

def update_csv_with_matches(df: pd.DataFrame, matches: Dict[str, List[str]], output_path: str):
    """
    Update CSV with matching report links
    
    Args:
        df: DataFrame with vessel data
        matches: Dictionary mapping vessel names to lists of report links
        output_path: Path to save updated CSV
    """
    try:
        # Create a copy of the DataFrame to avoid modifying the original
        updated_df = df.copy()
        updated_count = 0
        
        # Update matches
        for vessel_name, report_links in matches.items():
            # Find all rows that match this vessel name (in either English or Thai)
            mask = (updated_df['Vessel Name'] == vessel_name) | (updated_df['Thai name'].astype(str) == vessel_name)
            
            if mask.any():
                # Join multiple links with semicolon if there are multiple matches
                links_str = '; '.join(report_links)
                
                # Update the matching rows
                updated_df.loc[mask, 'Link to report which mentions'] = links_str
                updated_count += mask.sum()
        
        # Save the updated DataFrame to the output path
        updated_df.to_csv(output_path, index=False)
        logger.info(f"Updated {updated_count} rows for {len(matches)} vessels in CSV file")
        
    except Exception as e:
        logger.error(f"Failed to update CSV file: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Search for vessel names in translated files')
    parser.add_argument('--input-csv', type=str, default='input_data/fishing-vessels.csv',
                      help='Path to the input vessel CSV file')
    parser.add_argument('--translated-dir', type=str, default='translated_pdfs',
                      help='Directory containing translated files')
    parser.add_argument('--output-csv', type=str, default='output_data/fishing-vessels-updated.csv',
                      help='Path to save the updated CSV file')
    parser.add_argument('--threshold', type=int, default=85,
                      help='Fuzzy matching threshold (0-100)')
    
    args = parser.parse_args()
    
    try:
        # Setup directories
        setup_directories()
        
        logger.info(f"Loading vessel data from {args.input_csv}")
        df, vessel_names = load_vessel_data(args.input_csv)
        
        logger.info(f"Searching for {len(vessel_names)} vessels in {args.translated_dir}")
        matches = search_translated_files(args.translated_dir, vessel_names)
        
        if matches:
            logger.info(f"Found matches for {len(matches)} vessels")
            update_csv_with_matches(df, matches, args.output_csv)
            logger.info(f"Updated CSV saved to {args.output_csv}")
        else:
            logger.warning("No vessel matches found in any document")
            # Still create output CSV even if no matches
            shutil.copy(args.input_csv, args.output_csv)
            logger.info(f"Copied original CSV to {args.output_csv}")
        
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 