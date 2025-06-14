"""
Perplexity API Configuration for CaravanMasterX
"""

import os

PERPLEXITY_CONFIG = {
    'model': os.getenv('PERPLEXITY_MODEL', 'sonar-reasoning-pro'),
    'temperature': float(os.getenv('PERPLEXITY_TEMPERATURE', 0.2)),
    'max_tokens': int(os.getenv('PERPLEXITY_MAX_TOKENS', 1000)),
    'analysis_prompt': """
        Analyze current market conditions for {symbol} trading at {price}.
        Consider technical indicators, order book depth, and recent news.
        Provide specific entry/exit recommendations with price targets.
    """,
    'rate_limit': {
        'requests_per_minute': 30,
        'tokens_per_minute': 30000
    }
}
