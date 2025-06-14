"""
Enhanced API Keys Configuration for CaravanMaster
Secure credential management with Perplexity integration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEYS = {
    'PERPLEXITY_API_KEY': os.getenv('PERPLEXITY_API_KEY'),
    'DUNE_API_KEY': os.getenv('DUNE_API_KEY'),
    'PIONEX_API_KEY': os.getenv('PIONEX_API_KEY'),
    'PIONEX_API_SECRET': os.getenv('PIONEX_SECRET_KEY'),
}

# Validation
def validate_api_keys():
    """Validate that all required API keys are present"""
    required_keys = ['PIONEX_API_KEY', 'PIONEX_API_SECRET', 'DUNE_API_KEY', 'PERPLEXITY_API_KEY']
    
    missing_keys = []
    for key in required_keys:
        if not API_KEYS[key] or API_KEYS[key] == f'your_{key.lower()}_here':
            missing_keys.append(key)
    
    if missing_keys:
        raise ValueError(f"Missing API keys: {', '.join(missing_keys)}")
    
    return True
