"""
Enhanced Trading Configuration Settings for CaravanMaster
"""

import os

TRADING_CONFIG = {
    # Enhanced trading pairs
    'trading_pairs': ['BTC/USDT', 'ETH/USDT', 'SOL/USDT'],
    
    # Enhanced risk management
    'max_position_size_percent': 25,  # 25% of portfolio per position
    'max_risk_per_trade_percent': 2,  # 2% max risk per trade
    'min_risk_reward_ratio': 2.0,
    'max_leverage': 20,  # Maximum leverage allowed
    
    # Enhanced position management
    'default_stop_loss_percent': 4.0,  # 4% default stop loss
    'default_take_profit_percent': 6.0,  # 6% default take profit
    'trailing_stop_threshold': 0.5,  # 50% of target for trailing stop
    
    # AI and intelligence settings
    'enable_ai_analysis': True,
    'ai_confidence_threshold': 0.7,
    'perplexity_model': os.getenv('PERPLEXITY_MODEL', 'sonar-reasoning-pro'),
    
    # Enhanced analysis settings
    'analysis_interval_seconds': 180,  # 3 minutes for enhanced analysis
    'required_confirmation_tiers': 3,  # Need at least 3 tiers confirming
    'min_confidence_score': 70,       # Minimum score for action
    
    # Precision entry settings
    'enable_layered_orders': True,
    'order_layers': 3,
    'layer_spacing_percent': 0.05,  # 0.05% between layers
    
    # Weekend trading enhancements
    'weekend_volatility_multiplier': 0.8,  # Reduce size on weekends
    'weekend_monitoring_interval': 30,  # Check every 30 minutes
    
    # TWAP settings
    'twap_duration_minutes': 60,
    'twap_intervals': 12,
    'enable_twap_for_large_orders': True,
    
    # Safety settings
    'enable_live_trading': False,     # Set to True for live trading
    'paper_trading_mode': True,       # Simulate trades
    'max_daily_trades': 15,           # Maximum trades per day
    'emergency_stop_loss_percent': 8, # Emergency stop at 8% loss
    
    # Logging and monitoring
    'log_level': 'INFO',
    'save_analysis_history': True,
    'analysis_history_days': 90,
    'enable_performance_tracking': True,
    
    # API settings
    'api_timeout_seconds': 30,
    'max_api_retries': 3,
    'retry_delay_seconds': 5,
    'enable_rate_limiting': True
}

# Enhanced market conditions
MARKET_CONDITIONS = {
    'high_volatility_threshold': 8.0,  # 8% daily range
    'low_liquidity_threshold': 0.5,    # 0.5% spread
    'weekend_adjustment_factor': 0.8,
    'news_impact_multiplier': 1.2
}

# Performance tracking
PERFORMANCE_METRICS = {
    'track_win_rate': True,
    'track_profit_factor': True,
    'track_max_drawdown': True,
    'track_sharpe_ratio': True,
    'benchmark_symbol': 'BTC/USDT'
}
