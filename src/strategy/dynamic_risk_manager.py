import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

class RiskLevel(Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

@dataclass
class RiskMetrics:
    """Risk assessment metrics"""
    volatility: float
    var_95: float  # Value at Risk 95%
    var_99: float  # Value at Risk 99%
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    risk_level: RiskLevel
    timestamp: pd.Timestamp

class DynamicRiskManager:
    """
    Enhanced Dynamic Risk Management for CaravanMasterX
    Implements volatility-adjusted position sizing and advanced risk metrics
    """
    
    def __init__(self, base_risk_per_trade: float = 0.01,
                 max_portfolio_risk: float = 0.30,
                 max_total_exposure: float = 0.90):
        """
        Initialize risk manager
        
        Args:
            base_risk_per_trade: Base risk percentage per trade (1%)
            max_portfolio_risk: Maximum portfolio risk (30%)
            max_total_exposure: Maximum total exposure (90%)
        """
        self.base_risk_per_trade = base_risk_per_trade
        self.max_portfolio_risk = max_portfolio_risk
        self.max_total_exposure = max_total_exposure
        self.logger = logging.getLogger(__name__)
        
    def calculate_position_size(self, account_balance: float,
                               entry_price: float,
                               stop_loss: float,
                               volatility_adjustment: float = 1.0,
                               market_regime: str = "normal") -> Dict:
        """
        Calculate dynamic position size based on volatility and market conditions
        
        Args:
            account_balance: Current account balance
            entry_price: Planned entry price
            stop_loss: Stop loss price
            volatility_adjustment: Volatility-based adjustment factor
            market_regime: Current market regime (normal, volatile, extreme)
            
        Returns:
            Dictionary with position sizing information
        """
        # Calculate stop loss distance in percentage
        stop_loss_pct = abs(entry_price - stop_loss) / entry_price
        
        # Base risk amount
        base_risk_amount = account_balance * self.base_risk_per_trade
        
        # Apply volatility adjustment
        volatility_adjusted_risk = base_risk_amount / volatility_adjustment
        
        # Apply market regime adjustment
        regime_multiplier = self._get_regime_multiplier(market_regime)
        adjusted_risk_amount = volatility_adjusted_risk * regime_multiplier
        
        # Calculate position size
        position_size = adjusted_risk_amount / stop_loss_pct
        max_position_size = account_balance * self.max_portfolio_risk
        
        # Ensure position doesn't exceed maximum
        final_position_size = min(position_size, max_position_size)
        
        # Calculate leverage if applicable
        leverage = final_position_size / account_balance if account_balance > 0 else 1
        
        return {
            'position_size_usd': final_position_size,
            'position_size_base': final_position_size / entry_price,
            'risk_amount': adjusted_risk_amount,
            'risk_percentage': (adjusted_risk_amount / account_balance) * 100,
            'leverage': leverage,
            'stop_loss_distance_pct': stop_loss_pct * 100,
            'volatility_adjustment': volatility_adjustment,
            'regime_multiplier': regime_multiplier
        }
    
    def calculate_kelly_criterion(self, win_rate: float, 
                                 avg_win: float, 
                                 avg_loss: float) -> float:
        """
        Calculate optimal position size using Kelly Criterion
        
        Args:
            win_rate: Historical win rate (0-1)
            avg_win: Average winning trade return
            avg_loss: Average losing trade return (positive value)
            
        Returns:
            Optimal position size fraction (0-1)
        """
        if avg_loss <= 0:
            return 0
        
        # Kelly formula: f = (bp - q) / b
        # where b = avg_win/avg_loss, p = win_rate, q = 1 - win_rate
        b = avg_win / avg_loss
        p = win_rate
        q = 1 - win_rate
        
        kelly_fraction = (b * p - q) / b
        
        # Apply conservative adjustment (use half Kelly)
        conservative_kelly = max(0, min(kelly_fraction * 0.5, 0.25))  # Cap at 25%
        
        return conservative_kelly
    
    def _get_regime_multiplier(self, market_regime: str) -> float:
        """
        Get risk adjustment multiplier based on market regime
        """
        regime_map = {
            "normal": 1.0,
            "volatile": 0.7,
            "extreme": 0.5
        }
        return regime_map.get(market_regime.lower(), 1.0) 