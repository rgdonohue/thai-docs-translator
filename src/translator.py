from google.cloud import translate_v2 as translate
from typing import List, Dict
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)

class Translator:
    def __init__(self):
        """Initialize the translator client"""
        try:
            self.client = translate.Client()
        except Exception as e:
            logger.error(f"Failed to initialize translation client: {str(e)}")
            raise

    def translate_text(self, text: str, target_language: str = 'en') -> str:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language code (default: 'en' for English)
            
        Returns:
            Translated text
        """
        try:
            result = self.client.translate(
                text,
                target_language=target_language
            )
            return result['translatedText']
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            raise

    def batch_translate(self, texts: List[str], target_language: str = 'en') -> List[str]:
        """
        Translate multiple texts in batch
        
        Args:
            texts: List of texts to translate
            target_language: Target language code
            
        Returns:
            List of translated texts
        """
        translated_texts = []
        for text in tqdm(texts, desc="Translating"):
            translated = self.translate_text(text, target_language)
            translated_texts.append(translated)
        return translated_texts

    def translate_document(self, text_by_page: Dict[int, str]) -> Dict[int, str]:
        """
        Translate an entire document maintaining page structure
        
        Args:
            text_by_page: Dictionary of page numbers to text content
            
        Returns:
            Dictionary of page numbers to translated content
        """
        translated_doc = {}
        for page_num, text in text_by_page.items():
            translated_doc[page_num] = self.translate_text(text)
        return translated_doc 