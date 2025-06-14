"""
Helper utilities for CaravanMasterX
Common functions and utilities
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

def format_currency(amount, symbol="USDT"):
    """Format currency amount for display"""
    return f"{amount:,.2f} {symbol}"

def format_percentage(value, decimals=2):
    """Format percentage for display"""
    return f"{value:.{decimals}f}%"

def calculate_percentage_change(old_value, new_value):
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 0
    return ((new_value - old_value) / old_value) * 100

def retry_with_backoff(func, max_retries=3, delay=1.0):
    """Retry function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            wait_time = delay * (2 ** attempt)
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
            time.sleep(wait_time)

def validate_trading_pair(symbol):
    """Validate trading pair format"""
    if '/' not in symbol:
        return False
    
    parts = symbol.split('/')
    if len(parts) != 2:
        return False
    
    base, quote = parts
    if not base or not quote:
        return False
    
    return True

def safe_float(value, default=0.0):
    """Safely convert value to float"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    """Safely convert value to integer"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def timestamp_to_string(timestamp=None):
    """Convert timestamp to readable string"""
    if timestamp is None:
        timestamp = time.time()
    
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def log_trade_signal(symbol, action, confidence, tier_scores):
    """Log trading signal in structured format"""
    logger.info(f"TRADE SIGNAL: {symbol}")
    logger.info(f"  Action: {action}")
    logger.info(f"  Confidence: {confidence:.1%}")
    logger.info(f"  Tier Scores:")
    for tier, score in tier_scores.items():
        logger.info(f"    {tier}: {score:.1f}/100")

def create_summary_table(data, headers):
    """Create ASCII table for terminal display"""
    if not data or not headers:
        return "No data to display"
    
    # Calculate column widths
    col_widths = {}
    for header in headers:
        col_widths[header] = len(header)
    
    for row in data:
        for header in headers:
            value = str(row.get(header, ''))
            col_widths[header] = max(col_widths[header], len(value))
    
    # Create table
    separator = "+" + "+".join("-" * (col_widths[h] + 2) for h in headers) + "+"
    header_row = "|" + "|".join(f" {h:<{col_widths[h]}} " for h in headers) + "|"
    
    result = [separator, header_row, separator]
    
    for row in data:
        row_str = "|"
        for header in headers:
            value = str(row.get(header, ''))
            row_str += f" {value:<{col_widths[header]}} |"
        result.append(row_str)
    
    result.append(separator)
    return "\n".join(result)
