"""Sanctions list ingestion manager"""
import pandas as pd
from typing import Dict, List
from .ofac import OFACLoader
from .un import UNLoader
from ..config import settings

class ListManager:
    """Manage loading from multiple sanctions list sources"""
    
    def __init__(self):
        self.loaders = {
            'OFAC': OFACLoader(),
            'UN': UNLoader()
        }
        
    def load_all(self) -> Dict[str, pd.DataFrame]:
        """Load all available sanctions lists"""
        results = {}
        errors = []
        
        for source, loader in self.loaders.items():
            try:
                print(f"Loading {source} sanctions list...")
                df = loader.load()
                results[source] = df
                print(f"✅ {source}: {len(df)} entries loaded")
            except Exception as e:
                error_msg = f"❌ {source}: {str(e)}"
                errors.append(error_msg)
                print(error_msg)
                
        if errors and not results:
            raise Exception(f"All list loading failed: {'; '.join(errors)}")
            
        return results
    
    def consolidate(self, list_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Combine all lists into single DataFrame"""
        if not list_data:
            return pd.DataFrame(columns=['name', 'source', 'list_type', 'date_added'])
            
        combined = pd.concat(list_data.values(), ignore_index=True)
        
        # Remove duplicates (same name from multiple sources)
        combined = combined.drop_duplicates(subset=['name'], keep='first')
        
        # Save consolidated list
        processed_dir = settings.DATA_DIR / "processed"
        processed_dir.mkdir(exist_ok=True)
        
        output_file = processed_dir / "consolidated_sanctions.csv"
        combined.to_csv(output_file, index=False)
        
        return combined