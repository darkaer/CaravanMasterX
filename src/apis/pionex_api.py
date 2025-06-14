"""
Pionex API Integration for CaravanMasterX
Enhanced with WebSocket support and error handling
"""

import requests
import hmac
import hashlib
import time
import json
import logging
from urllib.parse import urlencode
from datetime import datetime

logger = logging.getLogger(__name__)

class PionexAPI:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.pionex.com"
        
        logger.info("Pionex API initialized")
        
    def generate_signature(self, method, path, timestamp, params=None, data=None):
        """Generate correct Pionex API signature with proper JSON formatting"""
        if params is None:
            params = {}
        
        # Add timestamp to parameters
        params['timestamp'] = timestamp
        
        # Sort parameters and create query string
        query_string = urlencode(sorted(params.items()))
        
        # Create path URL with query parameters
        path_url = f"{path}?{query_string}"
        
        # Start building the message with METHOD + PATH_URL
        message = f"{method.upper()}{path_url}"
        
        # For POST and DELETE requests, append JSON body with CORRECT separators
        if data is not None and method.upper() in ['POST', 'DELETE']:
            # Critical fix: Use separators with spaces
            message += json.dumps(data, separators=(', ', ': '))
        
        # Generate HMAC SHA256 signature
        signature = hmac.new(
            self.api_secret.encode('utf-8'), 
            message.encode('utf-8'), 
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def make_request(self, method, endpoint, params=None, data=None):
        """Make authenticated request to Pionex API with enhanced error handling"""
        url = f"{self.base_url}{endpoint}"
        timestamp = str(int(time.time() * 1000))
        
        if params is None:
            params = {}
        params['timestamp'] = timestamp
        
        signature = self.generate_signature(method, endpoint, timestamp, params, data)
        
        headers = {
            'PIONEX-KEY': self.api_key,
            'PIONEX-SIGNATURE': signature,
            'Content-Type': 'application/json'
        }
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            logger.debug(f"API Request: {method} {endpoint} - Status: {response.status_code}")
            
            # Check if response is valid JSON
            try:
                return response.json()
            except ValueError:
                logger.error(f"Invalid JSON response: {response.text}")
                return {"error": "Invalid JSON response"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return {"error": f"Request failed: {str(e)}"}
    
    def get_account_balance(self):
        """Get account balance with comprehensive error handling"""
        result = self.make_request('GET', '/api/v1/account/balances')
        
        # Check if result is a string (error response)
        if isinstance(result, str):
            logger.error(f"Received string response instead of JSON: {result}")
            return {"error": f"API returned string response: {result}"}
        
        # Check if result is None or empty
        if not result:
            logger.error("No response received from Pionex API")
            return {"error": "No response received from API"}
        
        # Check if the request was successful
        if not result.get('result', False):
            error_msg = f"Pionex API request failed: {result.get('message', 'Unknown error')}"
            logger.error(error_msg)
            return {
                "error": error_msg,
                "code": result.get('code', 'UNKNOWN'),
                "raw_response": result
            }
        
        # Process balance data with type checking
        try:
            balances = {}
            for balance_item in result.get('data', {}).get('balances', []):
                symbol = balance_item.get('coin', '')
                
                try:
                    available = float(balance_item.get('free', 0))
                    frozen = float(balance_item.get('frozen', 0))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Could not convert balance values for {symbol}: {e}")
                    continue
                
                if available > 0 or frozen > 0:
                    balances[symbol] = {
                        'available': available,
                        'frozen': frozen,
                        'total': available + frozen
                    }
            
            return {
                'success': True,
                'balances': balances,
                'usdt_balance': balances.get('USDT', {}).get('available', 0)
            }
        except Exception as e:
            logger.error(f"Error processing balance data: {e}")
            return {"error": f"Error processing balance data: {e}"}
    
    def get_market_prices(self):
        """Get current market prices for all tickers"""
        return self.make_request('GET', '/api/v1/market/tickers')
    
    def get_specific_price(self, symbol):
        """Get current price for specific symbol"""
        tickers = self.get_market_prices()
        if isinstance(tickers, dict) and 'data' in tickers:
            for ticker in tickers['data']:
                if ticker.get('symbol') == symbol:
                    return {
                        'symbol': symbol,
                        'price': float(ticker.get('close', 0)),
                        'high_24h': float(ticker.get('high', 0)),
                        'low_24h': float(ticker.get('low', 0)),
                        'volume_24h': float(ticker.get('volume', 0)),
                        'change_24h': float(ticker.get('change', 0))
                    }
        return None
    
    def get_caravan_assets(self):
        """Get prices for CaravanMaster target assets"""
        assets = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        results = {}
        
        for asset in assets:
            price_data = self.get_specific_price(asset)
            if price_data:
                results[asset] = price_data
                
        return results
    
    def place_order(self, symbol, side, amount, price=None, order_type='LIMIT'):
        """Place trading order with enhanced error handling"""
        endpoint = '/api/v1/trade/order'
        
        order_data = {
            "symbol": symbol.replace('/', '_'),
            "side": side.upper(),
            "type": order_type.upper(),
            "size": str(amount)
        }
        
        if price and order_type.upper() == 'LIMIT':
            order_data["price"] = str(price)
        
        logger.info(f"Placing {side} {order_type} order: {amount} {symbol} at {price}")
        return self.make_request('POST', endpoint, data=order_data)
    
    def get_order_book(self, symbol, limit=20):
        """Get order book for a specific symbol"""
        endpoint = '/api/v1/market/depth'
        params = {
            'symbol': symbol.replace('/', '_'),
            'limit': limit
        }
        
        return self.make_request('GET', endpoint, params=params)
    
    def get_historical_data(self, symbol, interval='1h', limit=100):
        """Get historical kline data"""
        endpoint = '/api/v1/market/kline'
        params = {
            'symbol': symbol.replace('/', '_'),
            'interval': interval,
            'limit': limit
        }
        
        return self.make_request('GET', endpoint, params=params)
