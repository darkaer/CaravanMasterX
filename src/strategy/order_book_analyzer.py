"""
Order Book Analyzer for CaravanMasterX
Real-time market depth analysis
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)

class RealTimeOrderBookAnalyzer:
    def __init__(self):
        self.order_books = {}
        
    def update_order_book(self, symbol, bids, asks):
        """Update order book data"""
        self.order_books[symbol] = {
            'bids': bids,
            'asks': asks,
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_liquidity_imbalance(self, symbol):
        """Calculate bid-ask liquidity ratio"""
        book = self.order_books.get(symbol)
        if not book:
            return None
            
        bid_volume = sum([bid[1] for bid in book['bids'][:5]])
        ask_volume = sum([ask[1] for ask in book['asks'][:5]])
        
        return (bid_volume - ask_volume) / (bid_volume + ask_volume)
    
    def detect_support_resistance(self, symbol):
        """Identify key support/resistance levels"""
        book = self.order_books.get(symbol)
        if not book:
            return None
            
        return {
            'support': book['bids'][0][0],
            'resistance': book['asks'][0][0]
        }
