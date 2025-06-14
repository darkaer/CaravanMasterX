"""
Volume Profile Analysis for CaravanMasterX
Institutional-grade volume analysis
"""

import logging
import pandas as pd

logger = logging.getLogger(__name__)

class VolumeProfileAnalyzer:
    def __init__(self, pionex_api):
        self.pionex_api = pionex_api
        
    def calculate_value_area(self, symbol, timeframe='1h', bins=20):
        """Calculate Volume Value Area"""
        data = self.pionex_api.get_historical_data(symbol, timeframe)
        
        # Calculate volume profile
        min_price = data['low'].min()
        max_price = data['high'].max()
        bin_size = (max_price - min_price) / bins
        
        volume_profile = []
        for i in range(bins):
            price_level = min_price + i * bin_size
            volume = data[(data['low'] >= price_level) & 
                        (data['high'] <= price_level + bin_size)]['volume'].sum()
            volume_profile.append((price_level, volume))
        
        # Find Value Area (70% of total volume)
        sorted_profile = sorted(volume_profile, key=lambda x: x[1], reverse=True)
        total_volume = sum([v[1] for v in volume_profile])
        cumulative = 0
        value_area = []
        
        for level in sorted_profile:
            cumulative += level[1]
            value_area.append(level[0])
            if cumulative >= total_volume * 0.7:
                break
                
        return {
            'value_area_low': min(value_area),
            'value_area_high': max(value_area),
            'point_of_control': sorted_profile[0][0]
        }
