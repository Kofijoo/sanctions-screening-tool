"""Matching thresholds and business rules for compliance screening"""

# Fuzzy matching thresholds (0-100 scale)
EXACT_MATCH_THRESHOLD = 100
HIGH_RISK_THRESHOLD = 85
MEDIUM_RISK_THRESHOLD = 70
LOW_RISK_THRESHOLD = 60

# Business rules
MIN_NAME_LENGTH = 3
REQUIRE_MANUAL_REVIEW_ABOVE = HIGH_RISK_THRESHOLD
AUTO_CLEAR_BELOW = LOW_RISK_THRESHOLD

# List priorities (higher = more critical)
LIST_PRIORITIES = {
    "OFAC": 100,
    "UN": 90,
    "HMT": 80,
    "EU": 70
}