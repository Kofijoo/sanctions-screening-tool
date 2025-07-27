"""Main preprocessing pipeline"""
import pandas as pd
from typing import Dict, List
from .cleaner import TextCleaner
from .normalizer import NameNormalizer
from .tokenizer import NameTokenizer

class NameProcessor:
    """Complete name preprocessing pipeline"""
    
    def __init__(self):
        self.cleaner = TextCleaner()
        self.normalizer = NameNormalizer()
        self.tokenizer = NameTokenizer()
        
    def process_single(self, name: str) -> Dict[str, any]:
        """Process a single name through full pipeline"""
        if not name:
            return {
                'original': '',
                'cleaned': '',
                'normalized': '',
                'tokens': [],
                'variants': set()
            }
            
        # Step 1: Clean
        cleaned = self.cleaner.clean(name)
        cleaned = self.cleaner.remove_titles(cleaned)
        cleaned = self.cleaner.remove_common_words(cleaned)
        
        # Step 2: Normalize
        normalized = self.normalizer.normalize(cleaned)
        
        # Step 3: Tokenize
        tokens = self.tokenizer.tokenize(normalized)
        variants = self.tokenizer.get_all_variants(normalized)
        
        return {
            'original': name,
            'cleaned': cleaned,
            'normalized': normalized,
            'tokens': tokens,
            'variants': variants
        }
    
    def process_dataframe(self, df: pd.DataFrame, name_column: str = 'name') -> pd.DataFrame:
        """Process entire DataFrame of names"""
        if name_column not in df.columns:
            raise ValueError(f"Column '{name_column}' not found in DataFrame")
            
        processed_data = []
        
        for _, row in df.iterrows():
            name = row[name_column]
            processed = self.process_single(name)
            
            # Combine original row data with processed data
            result = row.to_dict()
            result.update(processed)
            processed_data.append(result)
            
        return pd.DataFrame(processed_data)
    
    def create_search_index(self, df: pd.DataFrame) -> Dict[str, List[int]]:
        """Create search index for fast lookups"""
        index = {}
        
        for idx, row in df.iterrows():
            variants = row.get('variants', set())
            
            for variant in variants:
                if variant not in index:
                    index[variant] = []
                index[variant].append(idx)
                
        return index