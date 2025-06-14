"""
Perplexity API Configuration for CaravanMasterX
"""

PERPLEXITY_CONFIG = {
    'model': 'llama-3.1-sonar-small-128k-online',
    'temperature': 0.2,
    'max_tokens': 1000,
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
