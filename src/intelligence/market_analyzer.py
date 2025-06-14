"""
Market Intelligence Engine using Perplexity API
Advanced market analysis and signal generation
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class MarketIntelligenceEngine:
    def __init__(self, perplexity_api, pionex_api):
        self.perplexity_api = perplexity_api
        self.pionex_api = pionex_api
        
        logger.info("🧠 Market Intelligence Engine initialized")
    
    async def generate_market_analysis(self):
        """Generate comprehensive market analysis using AI"""
        try:
            # Get current market data
            symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
            market_data = {}
            
            for symbol in symbols:
                price_data = self.pionex_api.get_specific_price(symbol)
                if price_data:
                    market_data[symbol] = price_data
            
            # Generate AI analysis
            ai_analysis = await self.perplexity_api.generate_market_analysis(
                symbols, market_data
            )
            
            # Enhance with structured insights
            enhanced_analysis = self._enhance_analysis(ai_analysis, market_data)
            
            return enhanced_analysis
            
        except Exception as e:
            logger.error(f"Error generating market analysis: {e}")
            return None
    
    def _enhance_analysis(self, ai_analysis, market_data):
        """Enhance AI analysis with structured insights"""
        try:
            enhanced = {
                'timestamp': datetime.now().isoformat(),
                'ai_analysis': ai_analysis,
                'market_data': market_data,
                'sentiment': ai_analysis.get('sentiment', 'Neutral'),
                'key_insights': ai_analysis.get('key_insights', []),
                'trading_opportunities': self._identify_opportunities(market_data),
                'risk_assessment': self._assess_market_risks(market_data)
            }
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Error enhancing analysis: {e}")
            return ai_analysis
    
    def _identify_opportunities(self, market_data):
        """Identify trading opportunities from market data"""
        opportunities = []
        
        for symbol, data in market_data.items():
            change_24h = data.get('change_24h', 0)
            
            if change_24h < -5:
                opportunities.append({
                    'symbol': symbol,
                    'type': 'OVERSOLD_BOUNCE',
                    'description': f'{symbol} down {change_24h:.1f}% - potential reversal',
                    'confidence': 0.7
                })
            elif change_24h > 5:
                opportunities.append({
                    'symbol': symbol,
                    'type': 'MOMENTUM_CONTINUATION',
                    'description': f'{symbol} up {change_24h:.1f}% - momentum play',
                    'confidence': 0.6
                })
        
        return opportunities
    
    def _assess_market_risks(self, market_data):
        """Assess current market risks"""
        risks = []
        
        # Calculate overall market volatility
        volatilities = []
        for symbol, data in market_data.items():
            high = data.get('high_24h', 0)
            low = data.get('low_24h', 0)
            current = data.get('price', 0)
            
            if current > 0:
                volatility = ((high - low) / current) * 100
                volatilities.append(volatility)
        
        avg_volatility = sum(volatilities) / len(volatilities) if volatilities else 0
        
        if avg_volatility > 8:
            risks.append({
                'type': 'HIGH_VOLATILITY',
                'description': f'Market showing high volatility ({avg_volatility:.1f}%)',
                'severity': 'HIGH'
            })
        
        return risks
