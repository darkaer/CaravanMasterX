import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from dataclasses import dataclass

from .portfolio_optimizer import PortfolioOptimizer
from .dynamic_risk_manager import DynamicRiskManager
from src.apis.dune_api_client import DuneAPIClient
from src.ml.crypto_price_predictor import CryptoPricePredictor

@dataclass
class TradingSignal:
    """Enhanced trading signal with ML and on-chain data"""
    symbol: str
    direction: str  # LONG/SHORT
    entry_price: float
    stop_loss: float
    take_profit: float
    leverage: float
    position_size_usd: float
    confidence_score: float
    signal_sources: List[str]
    risk_metrics: Dict
    ml_prediction: Optional[Dict] = None
    onchain_analysis: Optional[Dict] = None
    timestamp: datetime = None

class EnhancedCaravanMasterX:
    """
    Fully integrated CaravanMasterX trading system with all enhancements
    """
    
    def __init__(self, config: Dict):
        """
        Initialize enhanced trading system
        
        Args:
            config: Configuration dictionary with API keys and settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self._initialize_components()
        
        # Trading state
        self.active_positions = []
        self.trading_enabled = True
        
    def _initialize_components(self):
        """Initialize all enhancement components"""
        # Portfolio optimization
        self.portfolio_optimizer = PortfolioOptimizer()
        
        # Risk management
        self.risk_manager = DynamicRiskManager(
            base_risk_per_trade=self.config.get('base_risk_per_trade', 0.01),
            max_portfolio_risk=self.config.get('max_portfolio_risk', 0.30),
            max_total_exposure=self.config.get('max_total_exposure', 0.90)
        )
        
        # On-chain analytics
        self.dune_client = DuneAPIClient(
            api_key=self.config['dune_api_key']
        )
        
        # Machine learning predictions
        self.ml_engine = CryptoPricePredictor(
            sequence_length=self.config.get('ml_sequence_length', 60),
            prediction_horizon=self.config.get('ml_prediction_horizon', 1),
            model_type=self.config.get('ml_model_type', 'ensemble')
        )
        
        # Supported assets
        self.assets = self.config.get('assets', ['BTC-USD', 'ETH-USD', 'SOL-USD'])
    
    async def analyze_market_conditions(self) -> Dict:
        """
        Comprehensive market analysis combining all data sources
        
        Returns:
            Market analysis results
        """
        self.logger.info("Starting comprehensive market analysis...")
        
        try:
            # Example: Get on-chain analysis (replace with actual Dune queries)
            # whale_data = await self.dune_client.get_whale_transactions()
            # mvrv_data = await self.dune_client.get_mvrv_data()
            onchain_analysis = {'combined_signal': 'neutral', 'combined_confidence': 0.5}  # Placeholder
            
            market_conditions = {
                'onchain_signal': onchain_analysis.get('combined_signal', 'neutral'),
                'onchain_confidence': onchain_analysis.get('combined_confidence', 0),
                'market_regime': 'normal',  # Placeholder
                'risk_assessment': {},      # Placeholder
                'timestamp': datetime.now().isoformat()
            }
            
            return market_conditions
            
        except Exception as e:
            self.logger.error(f"Market analysis failed: {e}")
            return {
                'onchain_signal': 'neutral',
                'onchain_confidence': 0,
                'market_regime': 'normal',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def generate_trading_signals(self, price_data: Dict[str, pd.DataFrame]) -> List[TradingSignal]:
        """
        Generate enhanced trading signals for all assets
        
        Args:
            price_data: Dictionary mapping asset symbols to price DataFrames
            
        Returns:
            List of trading signals
        """
        self.logger.info("Generating enhanced trading signals...")
        
        # Get market conditions
        market_conditions = await self.analyze_market_conditions()
        
        signals = []
        
        for asset in self.assets:
            if asset not in price_data:
                self.logger.warning(f"No price data available for {asset}")
                continue
                
            try:
                # Get ML prediction (placeholder, implement as needed)
                ml_prediction = None
                if hasattr(self.ml_engine, 'predict'):
                    ml_prediction = self.ml_engine.predict(price_data[asset])
                
                # Generate base technical signal (placeholder)
                technical_signal = {
                    'direction': 'LONG',
                    'entry_price': price_data[asset]['close'].iloc[-1],
                    'stop_loss': price_data[asset]['close'].iloc[-1] * 0.97,
                    'take_profit': price_data[asset]['close'].iloc[-1] * 1.05,
                    'confidence_score': 0.7
                }
                
                # Combine signals (simple example)
                combined_signal = TradingSignal(
                    symbol=asset,
                    direction=technical_signal['direction'],
                    entry_price=technical_signal['entry_price'],
                    stop_loss=technical_signal['stop_loss'],
                    take_profit=technical_signal['take_profit'],
                    leverage=1.0,
                    position_size_usd=1000.0,
                    confidence_score=technical_signal['confidence_score'],
                    signal_sources=['technical', 'ml', 'onchain'],
                    risk_metrics={},
                    ml_prediction=ml_prediction,
                    onchain_analysis=market_conditions,
                    timestamp=datetime.now()
                )
                signals.append(combined_signal)
                
            except Exception as e:
                self.logger.error(f"Signal generation failed for {asset}: {e}")
                continue
        
        return signals
    
    async def execute_risk_adjusted_trade(self, signal: TradingSignal, 
                                        account_balance: float) -> Dict:
        """
        Execute trade with comprehensive risk management
        
        Args:
            signal: Trading signal to execute
            account_balance: Current account balance
            
        Returns:
            Trade execution results
        """
        # Calculate position size with risk management
        position_info = self.risk_manager.calculate_position_size(
            account_balance=account_balance,
            entry_price=signal.entry_price,
            stop_loss=signal.stop_loss,
            volatility_adjustment=signal.risk_metrics.get('volatility_adjustment', 1.0) if signal.risk_metrics else 1.0,
            market_regime=signal.risk_metrics.get('market_regime', 'normal') if signal.risk_metrics else 'normal'
        )
        
        # Example: Check risk limits (implement as needed)
        risk_check = {'approved': True, 'size_reduction_factor': 1.0}
        
        if not risk_check['approved']:
            return {
                'status': 'rejected',
                'reason': 'Risk limits exceeded',
                'risk_check': risk_check
            }
        
        # Apply any position size adjustments
        final_position_size = position_info['position_size_usd'] * risk_check['size_reduction_factor']
        
        # Create trade order
        trade_order = {
            'symbol': signal.symbol,
            'direction': signal.direction,
            'entry_price': signal.entry_price,
            'stop_loss': signal.stop_loss,
            'take_profit': signal.take_profit,
            'position_size_usd': final_position_size,
            'leverage': position_info['leverage'],
            'confidence_score': signal.confidence_score,
            'risk_metrics': position_info,
            'timestamp': datetime.now()
        }
        
        # Add to active positions
        self.active_positions.append(trade_order)
        
        return {
            'status': 'executed',
            'trade_order': trade_order,
            'risk_check': risk_check
        } 