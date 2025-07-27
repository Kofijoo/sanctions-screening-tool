"""Basic text cleaning for name preprocessing"""
import re
import string

class TextCleaner:
    """Clean and standardize text for matching"""
    
    def __init__(self):
        # Common punctuation to remove
        self.punctuation = string.punctuation.replace("'", "")  # Keep apostrophes
        
    def clean(self, text: str) -> str:
        """Basic text cleaning"""
        if not text or not isinstance(text, str):
            return ""
            
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove punctuation except apostrophes
        text = text.translate(str.maketrans('', '', self.punctuation))
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def remove_titles(self, text: str) -> str:
        """Remove common titles and honorifics"""
        titles = [
            'mr', 'mrs', 'ms', 'miss', 'dr', 'prof', 'sir', 'lady',
            'lord', 'sheikh', 'imam', 'mullah', 'ayatollah'
        ]
        
        words = text.split()
        filtered = [w for w in words if w not in titles]
        return ' '.join(filtered)
    
    def remove_common_words(self, text: str) -> str:
        """Remove common connecting words"""
        stop_words = ['and', 'or', 'the', 'of', 'bin', 'ibn', 'abu', 'al']
        
        words = text.split()
        filtered = [w for w in words if w not in stop_words]
        return ' '.join(filtered)