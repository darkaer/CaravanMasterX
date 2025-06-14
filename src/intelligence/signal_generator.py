"""
Signal Generator for CaravanMasterX
Enhanced trading signal generation with AI integration
"""

import logging
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)

class SignalGenerator:
    def __init__(self, perplexity_api, pionex_api):
        self.perplexity_api = perplexity_api
        self.pionex_api = pionex_api
        self.signals = {}
        
        logger.info("Signal Generator initialized")
    
    async def generate_signals(self, market_data, ai_analysis=None):
        """Generate trading signals with AI enhancement"""
        try:
            signals = []
            
            for symbol, data in market_data.items():
                # Generate base signal from technical analysis
                base_signal = self._generate_technical_signal(symbol, data)
                
                # Enhance with AI insights if available
                if ai_analysis:
                    enhanced_signal = self._enhance_with_ai(base_signal, ai_analysis)
                else:
                    enhanced_signal = base_signal
                
                # Add confidence score
                enhanced_signal['confidence'] = self._calculate_confidence(enhanced_signal)
                
                signals.append(enhanced_signal)
            
            self.signals = {signal['symbol']: signal for signal in signals}
            return signals
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
            return []
    
    def _generate_technical_signal(self, symbol, data):
        """Generate signal based on technical analysis"""
        current_price = data.get('price', 0)
        high_24h = data.get('high_24h', 0)
        low_24h = data.get('low_24h', 0)
        change_24h = data.get('change_24h', 0)
        
        # Simple trend-based signal
        if change_24h > 3:
            action = 'BUY'
            confidence = 0.7
        elif change_24h < -3:
            action = 'SELL'
            confidence = 0.7
        else:
            action = 'HOLD'
            confidence = 0.5
        
        # Calculate entry, TP, and SL
        if action == 'BUY':
            entry_price = current_price * 0.998  # Slight discount
            take_profit = current_price * 1.05   # 5% target
            stop_loss = current_price * 0.97     # 3% stop
        elif action == 'SELL':
            entry_price = current_price * 1.002  # Slight premium
            take_profit = current_price * 0.95   # 5% target
            stop_loss = current_price * 1.03     # 3% stop
        else:
            entry_price = current_price
            take_profit = current_price
            stop_loss = current_price
        
        return {
            'symbol': symbol,
            'action': action,
            'entry_price': entry_price,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }
    
    def _enhance_with_ai(self, base_signal, ai_analysis):
        """Enhance signal with AI insights"""
        symbol = base_signal['symbol']
        
        # Check if AI has insights for this symbol
        ai_sentiment = ai_analysis.get('sentiment', 'Neutral')
        
        # Adjust confidence based on AI sentiment
        if ai_sentiment == 'Bullish' and base_signal['action'] == 'BUY':
            base_signal['confidence'] += 0.1
            base_signal['ai_enhanced'] = True
        elif ai_sentiment == 'Bearish' and base_signal['action'] == 'SELL':
            base_signal['confidence'] += 0.1
            base_signal['ai_enhanced'] = True
        elif ai_sentiment != 'Neutral' and base_signal['action'] != 'HOLD':
            base_signal['confidence'] -= 0.1
            base_signal['ai_enhanced'] = True
        
        # Cap confidence at 0.95
        base_signal['confidence'] = min(base_signal['confidence'], 0.95)
        
        return base_signal
    
    def _calculate_confidence(self, signal):
        """Calculate final confidence score"""
        base_confidence = signal.get('confidence', 0.5)
        
        # Adjust based on market conditions
        if 'ai_enhanced' in signal and signal['ai_enhanced']:
            return min(base_confidence + 0.05, 0.95)
        
        return base_confidence
    
    def get_signal(self, symbol):
        """Get the latest signal for a specific symbol"""
        return self.signals.get(symbol)
