"""
Risk Management Module for CaravanMasterX
Advanced position sizing and risk control
"""

import logging
from typing import Dict, Optional
import numpy as np

logger = logging.getLogger(__name__)

class RiskManager:
    def __init__(self, config, account_balance=None):
        self.config = config
        self.account_balance = account_balance or 100.0
        self.max_position_size_percent = config.get('max_position_size_percent', 30)
        self.max_risk_per_trade_percent = config.get('max_risk_per_trade_percent', 2)
        self.min_risk_reward_ratio = config.get('min_risk_reward_ratio', 2.0)
        
        logger.info("Risk Manager initialized")
        
    def update_account_balance(self, balance):
        """Update account balance for accurate position sizing"""
        self.account_balance = balance
        logger.info(f"Account balance updated: {balance} USDT")
        
    def calculate_position_size(self, entry_price, stop_loss, leverage=1):
        """Calculate optimal position size based on risk management rules"""
        # Maximum risk amount
        max_risk_amount = self.account_balance * (self.max_risk_per_trade_percent / 100)
        
        # Risk per unit
        risk_per_unit = abs(entry_price - stop_loss)
        
        if risk_per_unit <= 0:
            logger.warning("Invalid stop loss level, risk per unit is zero or negative")
            return 0
        
        # Calculate position size
        position_size_units = max_risk_amount / risk_per_unit
        position_size_value = position_size_units * entry_price
        
        # Apply maximum position size limit
        max_position_value = self.account_balance * (self.max_position_size_percent / 100)
        
        # Adjust for leverage
        if leverage > 1:
            position_size_value = position_size_value * leverage
            
        # Ensure position doesn't exceed maximum
        final_position_value = min(position_size_value, max_position_value)
        
        logger.info(f"Calculated position size: {final_position_value:.2f} USDT (leverage: {leverage}x)")
        
        return {
            'position_size_value': final_position_value,
            'position_size_units': final_position_value / entry_price,
            'risk_amount': max_risk_amount,
            'risk_percent': self.max_risk_per_trade_percent,
            'leverage': leverage
        }
    
    def validate_trade(self, entry_price, take_profit, stop_loss):
        """Validate trade setup against risk management rules"""
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        
        if risk <= 0:
            logger.warning("Invalid stop loss, risk is zero or negative")
            return {'valid': False, 'reason': 'Invalid stop loss'}
        
        risk_reward_ratio = reward / risk
        
        validation = {
            'valid': risk_reward_ratio >= self.min_risk_reward_ratio,
            'risk_reward_ratio': risk_reward_ratio,
            'min_required': self.min_risk_reward_ratio,
            'risk_amount': risk,
            'reward_amount': reward
        }
        
        if not validation['valid']:
            validation['reason'] = f"Risk/reward ratio {risk_reward_ratio:.2f} below minimum {self.min_risk_reward_ratio}"
            logger.warning(f"Trade validation failed: {validation['reason']}")
        else:
            logger.info(f"Trade validated with R:R ratio of {risk_reward_ratio:.2f}")
        
        return validation
    
    def adjust_for_weekend(self, position_size, leverage):
        """Adjust position size for weekend trading"""
        weekend_multiplier = 0.8  # Reduce position size by 20% on weekends
        
        adjusted_position = position_size * weekend_multiplier
        logger.info(f"Weekend adjustment: Position size reduced from {position_size:.2f} to {adjusted_position:.2f}")
        
        return adjusted_position
    
    def calculate_max_drawdown(self, positions):
        """Calculate maximum drawdown for current positions"""
        if not positions:
            return 0
            
        total_risk = sum([p.get('risk_amount', 0) for p in positions])
        max_drawdown_percent = total_risk / self.account_balance * 100
        
        logger.info(f"Maximum potential drawdown: {max_drawdown_percent:.2f}%")
        return max_drawdown_percent
