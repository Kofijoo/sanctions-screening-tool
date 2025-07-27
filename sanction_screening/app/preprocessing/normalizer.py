"""Advanced name normalization and transliteration"""
import re
from unidecode import unidecode

class NameNormalizer:
    """Advanced name normalization for international names"""
    
    def __init__(self):
        # Common name variations
        self.replacements = {
            'mohammed': ['muhammad', 'mohamed', 'mohammad'],
            'abdul': ['abd', 'abdel', 'abdal'],
            'al': ['el', 'ul'],
            'ibn': ['bin', 'ben']
        }
        
    def transliterate(self, text: str) -> str:
        """Convert non-Latin scripts to Latin"""
        if not text:
            return ""
        return unidecode(text)
    
    def normalize_arabic_names(self, text: str) -> str:
        """Normalize common Arabic name patterns"""
        # Handle Al- prefix variations
        text = re.sub(r'\bal[\s\-]', 'al ', text)
        
        # Handle common transliteration variations
        for standard, variants in self.replacements.items():
            for variant in variants:
                text = re.sub(rf'\b{variant}\b', standard, text)
                
        return text
    
    def normalize_spacing(self, text: str) -> str:
        """Standardize spacing around hyphens and apostrophes"""
        # Remove spaces around hyphens
        text = re.sub(r'\s*-\s*', '-', text)
        
        # Remove spaces around apostrophes
        text = re.sub(r"\s*'\s*", "'", text)
        
        return text
    
    def normalize(self, text: str) -> str:
        """Full normalization pipeline"""
        if not text:
            return ""
            
        # Transliterate first
        text = self.transliterate(text)
        
        # Normalize Arabic patterns
        text = self.normalize_arabic_names(text)
        
        # Fix spacing
        text = self.normalize_spacing(text)
        
        return text