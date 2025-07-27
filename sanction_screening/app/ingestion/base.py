"""Base loader for sanctions list ingestion"""
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
from ..config import settings, endpoints

class BaseLoader:
    """Base class for sanctions list loaders"""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.timestamp = datetime.now()
        
    def download(self, url: str) -> str:
        """Download data from URL with error handling"""
        try:
            response = requests.get(
                url, 
                headers=endpoints.REQUEST_HEADERS,
                timeout=settings.API_TIMEOUT
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise Exception(f"Failed to download {self.source_name}: {e}")
    
    def save_raw(self, data: str, filename: str):
        """Save raw data for audit trail"""
        raw_dir = settings.DATA_DIR / "raw"
        raw_dir.mkdir(exist_ok=True)
        
        filepath = raw_dir / f"{filename}_{self.timestamp.strftime('%Y%m%d_%H%M%S')}"
        filepath.write_text(data, encoding='utf-8')
        
    def standardize(self, data: pd.DataFrame) -> pd.DataFrame:
        """Convert to standard format"""
        required_columns = ['name', 'source', 'list_type', 'date_added']
        
        # Add missing columns with defaults
        for col in required_columns:
            if col not in data.columns:
                if col == 'source':
                    data[col] = self.source_name
                elif col == 'date_added':
                    data[col] = self.timestamp
                else:
                    data[col] = None
                    
        return data[required_columns]