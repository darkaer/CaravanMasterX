"""
Volatility Adjuster for CaravanMasterX
Dynamic position sizing based on market conditions
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)

class VolatilityAdjuster:
    def __init__(self, pionex_api):
        self.pionex_api = pionex_api
        
    def calculate_position_size(self, symbol, base_size):
        """Calculate volatility-adjusted position size"""
        volatility = self._calculate_historical_volatility(symbol)
        adjustment_factor = self._get_adjustment_factor(volatility)
        
        return base_size * adjustment_factor
    
    def _calculate_historical_volatility(self, symbol, period=14):
        """Calculate 14-period historical volatility"""
        data = self.pionex_api.get_historical_data(symbol, '1d')
        returns = np.log(data['close'] / data['close'].shift(1))
        return returns.rolling(period).std().iloc[-1] * np.sqrt(365)
    
    def _get_adjustment_factor(self, volatility):
        """Get position size multiplier based on volatility"""
        if volatility < 0.05:
            return 1.2
        elif volatility < 0.1:
            return 1.0
        elif volatility < 0.2:
            return 0.8
        else:
            return 0.5
