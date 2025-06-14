"""
Enhanced CaravanMaster Trading Strategy
Four-Tier Confirmation + AI Intelligence Integration
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np
from .order_book_analyzer import RealTimeOrderBookAnalyzer
from .volume_profile import VolumeProfileAnalyzer
from .twap_strategy import TWAPStrategy
from ..utils.volatility_adjuster import VolatilityAdjuster

logger = logging.getLogger(__name__)

class EnhancedCaravanMasterStrategy:
    def __init__(self, pionex_api, dune_api, perplexity_api, config):
        self.pionex_api = pionex_api
        self.dune_api = dune_api
        self.perplexity_api = perplexity_api
        self.config = config
        
        # Initialize enhanced modules
        self.order_book_analyzer = RealTimeOrderBookAnalyzer()
        self.volume_profile_analyzer = VolumeProfileAnalyzer(pionex_api)
        self.twap_strategy = TWAPStrategy(pionex_api)
        self.volatility_adjuster = VolatilityAdjuster(pionex_api)
        
        # Strategy state
        self.last_analysis = None
        self.active_signals = []
        
        logger.info("🎯 Enhanced CaravanMaster Strategy initialized")
        
    async def get_enhanced_portfolio_status(self):
        """Get comprehensive portfolio status with real-time data"""
        try:
            # Get account balance with enhanced error handling
            balance_data = self.pionex_api.get_account_balance()
            
            # Get current market prices for all assets
            market_prices = self.pionex_api.get_caravan_assets()
            
            # Calculate enhanced portfolio metrics
            portfolio = {
                'timestamp': datetime.now().isoformat(),
                'balance_data': balance_data,
                'market_prices': market_prices,
                'usdt_balance': balance_data.get('usdt_balance', 0) if balance_data else 0,
                'portfolio_health': self._assess_portfolio_health(balance_data, market_prices),
                'risk_metrics': self._calculate_risk_metrics(balance_data),
                'trading_capacity': self._calculate_trading_capacity(balance_data)
            }
            
            return portfolio
            
        except Exception as e:
            logger.error(f"Error getting enhanced portfolio status: {e}")
            return None
    
    async def execute_enhanced_four_tier_analysis(self, market_intelligence=None):
        """Execute enhanced four-tier analysis with AI integration"""
        symbols = self.config.get('trading_pairs', ['BTC/USDT', 'ETH/USDT', 'SOL/USDT'])
        analysis_results = {}
        
        for symbol in symbols:
            logger.info(f"🔍 Executing enhanced analysis for {symbol}")
            
            # Get current market data
            price_data = self.pionex_api.get_specific_price(symbol)
            
            if not price_data:
                continue
                
            # Execute all four tiers with enhancements
            symbol_analysis = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'tier1': await self._enhanced_tier1_analysis(symbol, price_data),
                'tier2': await self._enhanced_tier2_analysis(symbol, price_data),
                'tier3': await self._enhanced_tier3_analysis(symbol, price_data),
                'tier4': await self._enhanced_tier4_analysis(symbol, price_data),
                'ai_intelligence': market_intelligence
            }
            
            # Calculate enhanced scoring
            symbol_analysis['enhanced_score'] = self._calculate_enhanced_score(symbol_analysis)
            symbol_analysis['confidence'] = self._calculate_confidence(symbol_analysis)
            
            analysis_results[symbol] = symbol_analysis
        
        self.last_analysis = analysis_results
        return analysis_results
    
    async def generate_precision_signals(self, analysis):
        """Generate precision trading signals with enhanced risk management"""
        signals = []
        
        for symbol, data in analysis.items():
            try:
                # Generate base signal from analysis
                base_signal = self._generate_base_signal(symbol, data)
                
                if base_signal['action'] == 'HOLD':
                    continue
                
                # Enhance signal with precision entry techniques
                enhanced_signal = await self._enhance_signal_precision(symbol, base_signal)
                
                # Apply volatility adjustments
                final_signal = self._apply_volatility_adjustments(enhanced_signal)
                
                signals.append(final_signal)
                
            except Exception as e:
                logger.error(f"Error generating signal for {symbol}: {e}")
                continue
        
        self.active_signals = signals
        return signals
    
    async def _enhanced_tier1_analysis(self, symbol, price_data):
        """Enhanced Tier 1: Market Structure + Order Book Analysis"""
        try:
            # Basic technical analysis
            current_price = price_data['price']
            high_24h = price_data['high_24h']
            low_24h = price_data['low_24h']
            change_24h = price_data['change_24h']
            
            # Enhanced with order book analysis
            order_book_signal = await self.order_book_analyzer.analyze_order_book(symbol)
            
            # Volume profile integration
            volume_profile = await self.volume_profile_analyzer.calculate_volume_profile(symbol)
            
            return {
                'current_price': current_price,
                'daily_change': change_24h,
                'trend_bias': self._determine_trend_bias(change_24h),
                'order_book_signal': order_book_signal,
                'volume_profile': volume_profile,
                'tier1_score': self._calculate_enhanced_tier1_score(
                    change_24h, order_book_signal, volume_profile
                )
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced Tier 1 analysis: {e}")
            return None
    
    def _generate_base_signal(self, symbol, analysis_data):
        """Generate base trading signal from analysis"""
        enhanced_score = analysis_data.get('enhanced_score', 50)
        confidence = analysis_data.get('confidence', 0.5)
        
        # Current market data
        tier1 = analysis_data.get('tier1', {})
        current_price = tier1.get('current_price', 0)
        
        # Determine action based on enhanced scoring
        if enhanced_score >= 75 and confidence >= 0.8:
            action = 'STRONG_BUY'
            leverage = 15
        elif enhanced_score >= 65 and confidence >= 0.7:
            action = 'BUY'
            leverage = 12
        elif enhanced_score <= 25 and confidence >= 0.8:
            action = 'STRONG_SELL'
            leverage = 15
        elif enhanced_score <= 35 and confidence >= 0.7:
            action = 'SELL'
            leverage = 12
        else:
            action = 'HOLD'
            leverage = 1
        
        # Calculate entry, TP, and SL based on action
        if action in ['BUY', 'STRONG_BUY']:
            entry_price = current_price * 0.998  # Slight discount for limit order
            take_profit = current_price * 1.06   # 6% target
            stop_loss = current_price * 0.96     # 4% stop
        elif action in ['SELL', 'STRONG_SELL']:
            entry_price = current_price * 1.002  # Slight premium for short
            take_profit = current_price * 0.94   # 6% target
            stop_loss = current_price * 1.04     # 4% stop
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
            'leverage': leverage,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }
    
    async def _enhance_signal_precision(self, symbol, base_signal):
        """Enhance signal with precision entry techniques"""
        try:
            # Apply TWAP for large positions
            if base_signal['action'] in ['STRONG_BUY', 'STRONG_SELL']:
                twap_schedule = await self.twap_strategy.create_execution_schedule(
                    symbol, base_signal['entry_price']
                )
                base_signal['execution_strategy'] = 'TWAP'
                base_signal['twap_schedule'] = twap_schedule
            
            # Add precision entry levels
            base_signal['precision_entries'] = self._calculate_precision_entries(
                base_signal['entry_price'], base_signal['action']
            )
            
            return base_signal
            
        except Exception as e:
            logger.error(f"Error enhancing signal precision: {e}")
            return base_signal
    
    def _calculate_precision_entries(self, base_price, action):
        """Calculate multiple precision entry levels"""
        if action in ['BUY', 'STRONG_BUY']:
            return {
                'primary': base_price,
                'secondary': base_price * 0.995,
                'tertiary': base_price * 0.990
            }
        elif action in ['SELL', 'STRONG_SELL']:
            return {
                'primary': base_price,
                'secondary': base_price * 1.005,
                'tertiary': base_price * 1.010
            }
        else:
            return {'primary': base_price}
    
    def _apply_volatility_adjustments(self, signal):
        """Apply volatility-based adjustments to signal"""
        try:
            # Get volatility adjustment
            volatility_data = self.volatility_adjuster.calculate_volatility_adjustment(
                signal['symbol'], signal['entry_price'], signal['stop_loss']
            )
            
            if volatility_data:
                # Adjust position size based on volatility
                signal['position_size_usdt'] = volatility_data.get('adjusted_position_size', 20)
                signal['volatility_multiplier'] = volatility_data.get('volatility_multiplier', 1.0)
            
            return signal
            
        except Exception as e:
            logger.error(f"Error applying volatility adjustments: {e}")
            return signal
    
    def _calculate_enhanced_score(self, analysis):
        """Calculate enhanced analysis score"""
        scores = []
        
        for tier in ['tier1', 'tier2', 'tier3', 'tier4']:
            tier_data = analysis.get(tier, {})
            if tier_data and f'{tier}_score' in tier_data:
                scores.append(tier_data[f'{tier}_score'])
        
        # Include AI intelligence bonus
        if analysis.get('ai_intelligence'):
            ai_sentiment = analysis['ai_intelligence'].get('sentiment', 'Neutral')
            if ai_sentiment == 'Bullish':
                scores.append(75)
            elif ai_sentiment == 'Bearish':
                scores.append(25)
            else:
                scores.append(50)
        
        return np.mean(scores) if scores else 50
    
    def _calculate_confidence(self, analysis):
        """Calculate signal confidence level"""
        available_tiers = sum(1 for tier in ['tier1', 'tier2', 'tier3', 'tier4'] 
                             if analysis.get(tier))
        
        base_confidence = available_tiers / 4
        
        # Boost confidence with AI intelligence
        if analysis.get('ai_intelligence'):
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
