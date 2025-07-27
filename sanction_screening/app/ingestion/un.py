"""UN Security Council sanctions list loader"""
import pandas as pd
import xml.etree.ElementTree as ET
from .base import BaseLoader
from ..config import endpoints

class UNLoader(BaseLoader):
    """Load UN Security Council Consolidated List"""
    
    def __init__(self):
        super().__init__("UN")
        
    def load(self) -> pd.DataFrame:
        """Load and process UN consolidated list"""
        # Download raw XML
        raw_data = self.download(endpoints.UN_CONSOLIDATED_URL)
        self.save_raw(raw_data, "un_consolidated.xml")
        
        # Parse XML
        try:
            root = ET.fromstring(raw_data)
            names = []
            
            # Extract individual names (simplified XML parsing)
            for individual in root.findall('.//INDIVIDUAL'):
                name_elem = individual.find('.//FIRST_NAME')
                last_elem = individual.find('.//SECOND_NAME')
                
                if name_elem is not None and last_elem is not None:
                    full_name = f"{name_elem.text} {last_elem.text}".strip()
                    if full_name:
                        names.append({
                            'name': full_name,
                            'list_type': 'Individual'
                        })
            
            # Extract entity names
            for entity in root.findall('.//ENTITY'):
                name_elem = entity.find('.//FIRST_NAME')
                if name_elem is not None and name_elem.text:
                    names.append({
                        'name': name_elem.text.strip(),
                        'list_type': 'Entity'
                    })
                    
        except ET.ParseError as e:
            raise Exception(f"Failed to parse UN XML: {e}")
        
        if not names:
            raise Exception("No names extracted from UN list")
            
        df = pd.DataFrame(names)
        return self.standardize(df)