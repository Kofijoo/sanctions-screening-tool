"""Name tokenization for matching"""
from typing import List, Set

class NameTokenizer:
    """Break names into searchable tokens"""
    
    def __init__(self):
        self.min_token_length = 2
        
    def tokenize(self, text: str) -> List[str]:
        """Split name into individual tokens"""
        if not text:
            return []
            
        # Split on whitespace and hyphens
        tokens = []
        for part in text.split():
            # Split hyphenated names
            sub_tokens = part.split('-')
            tokens.extend(sub_tokens)
            
        # Filter short tokens
        tokens = [t for t in tokens if len(t) >= self.min_token_length]
        
        return tokens
    
    def generate_ngrams(self, tokens: List[str], n: int = 2) -> List[str]:
        """Generate n-grams for partial matching"""
        if len(tokens) < n:
            return tokens
            
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngram = ' '.join(tokens[i:i+n])
            ngrams.append(ngram)
            
        return ngrams
    
    def get_all_variants(self, text: str) -> Set[str]:
        """Get all searchable variants of a name"""
        variants = set()
        
        # Original text
        variants.add(text)
        
        # Individual tokens
        tokens = self.tokenize(text)
        variants.update(tokens)
        
        # Bigrams for partial matching
        if len(tokens) > 1:
            bigrams = self.generate_ngrams(tokens, 2)
            variants.update(bigrams)
            
        # Remove empty strings
        variants.discard('')
        
        return variants