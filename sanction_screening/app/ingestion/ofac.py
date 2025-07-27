"""OFAC (US Treasury) sanctions list loader"""
import pandas as pd
from io import StringIO
from .base import BaseLoader
from ..config import endpoints

class OFACLoader(BaseLoader):
    """Load OFAC Specially Designated Nationals (SDN) list"""
    
    def __init__(self):
        super().__init__("OFAC")
        
    def load(self) -> pd.DataFrame:
        """Load and process OFAC SDN list"""
        # Download raw data
        raw_data = self.download(endpoints.OFAC_SDN_URL)
        self.save_raw(raw_data, "ofac_sdn.csv")
        
        # Parse CSV
        df = pd.read_csv(StringIO(raw_data))
        
        # Extract names (OFAC format has name in first column)
        processed = pd.DataFrame({
            'name': df.iloc[:, 1],  # Second column typically contains names
            'list_type': 'SDN',
            'entity_id': df.iloc[:, 0] if len(df.columns) > 0 else None
        })
        
        # Remove empty names
        processed = processed.dropna(subset=['name'])
        processed = processed[processed['name'].str.strip() != '']
        
        return self.standardize(processed)