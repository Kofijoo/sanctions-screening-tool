"""Configuration loader with validation"""
from . import settings, thresholds, endpoints

def validate_config():
    """Validate configuration for compliance requirements"""
    errors = []
    
    # Validate thresholds
    if thresholds.HIGH_RISK_THRESHOLD <= thresholds.MEDIUM_RISK_THRESHOLD:
        errors.append("HIGH_RISK_THRESHOLD must be > MEDIUM_RISK_THRESHOLD")
    
    if thresholds.MEDIUM_RISK_THRESHOLD <= thresholds.LOW_RISK_THRESHOLD:
        errors.append("MEDIUM_RISK_THRESHOLD must be > LOW_RISK_THRESHOLD")
    
    # Validate paths
    if not settings.DATA_DIR.exists():
        settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    if errors:
        raise ValueError(f"Configuration errors: {'; '.join(errors)}")
    
    return True

def get_config():
    """Get validated configuration"""
    validate_config()
    return {
        "settings": settings,
        "thresholds": thresholds,
        "endpoints": endpoints
    }