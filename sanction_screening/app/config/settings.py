"""Core application settings and environment configuration"""
import os
from pathlib import Path

# Environment
ENVIRONMENT = os.getenv("SLST_ENV", "development")
DEBUG = ENVIRONMENT == "development"

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Security
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "1000"))

# Compliance
AUDIT_ENABLED = os.getenv("AUDIT_ENABLED", "true").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")