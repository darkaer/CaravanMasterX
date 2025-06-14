"""
Dune Analytics API Integration for CaravanMasterX
On-chain intelligence and blockchain analytics
"""

import requests
import time
import logging
from datetime import datetime
import os
import random

logger = logging.getLogger(__name__)

DUNE_API_KEY = os.getenv('DUNE_API_KEY')
print("DUNE_API_KEY loaded:", (DUNE_API_KEY[:6] + '...' if DUNE_API_KEY else 'NOT SET'))
BASE_URL = 'https://api.dune.com/api/v1'

# Rate limiting parameters
REQUESTS_PER_MIN = 40
REQUEST_INTERVAL = 60 / REQUESTS_PER_MIN

# Composite signal weights
WEIGHTS = {
    'exchange_flows': 0.25,
    'whale_activity': 0.25,
    'defi_liquidations': 0.20,
    'stablecoin_flows': 0.15,
    'dex_volume': 0.15
}

class DuneAPI:
    def __init__(self):
        self.headers = {
            'Content-Type': 'application/json',
            'X-DUNE-API-KEY': DUNE_API_KEY
        }
        self.last_request_time = 0

    def _wait(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < REQUEST_INTERVAL:
            time.sleep(REQUEST_INTERVAL - elapsed)

    def create_query(self, sql, name=None, description=None, is_private=True):
        self._wait()
        url = f"{BASE_URL}/query"
        payload = {
            'query_sql': sql,
            'is_private': is_private
        }
        if name:
            payload['name'] = name
        if description:
            payload['description'] = description
        response = requests.post(url, headers=self.headers, json=payload)
        self.last_request_time = time.time()
        if response.status_code == 200:
            return response.json().get('query_id')
        else:
            raise Exception(f"Create query error: {response.status_code} {response.text}")

    def run_query(self, query_id):
        self._wait()
        url = f"{BASE_URL}/query/{query_id}/execute"
        response = requests.post(url, headers=self.headers)
        self.last_request_time = time.time()
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Run query error: {response.status_code} {response.text}")

    def get_query_results(self, query_id):
        self._wait()
        url = f"{BASE_URL}/query/{query_id}/results"
        response = requests.get(url, headers=self.headers)
        self.last_request_time = time.time()
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Get results error: {response.status_code} {response.text}")

class DuneAnalyticsEnhanced:
    def __init__(self, api_key=None, demo_mode=False):
        self.api_key = api_key or DUNE_API_KEY
        self.demo_mode = demo_mode
        self.api = DuneAPI()
        self.query_ids = {
            'exchange_flows': os.getenv('DUNE_EXCHANGE_FLOW_QUERY_ID'),
            'whale_activity': os.getenv('DUNE_WHALE_ACTIVITY_QUERY_ID'),
            'defi_liquidations': os.getenv('DUNE_DEFI_LIQUIDATION_QUERY_ID'),
            'stablecoin_flows': os.getenv('DUNE_STABLECOIN_FLOW_QUERY_ID'),
            'dex_volume': os.getenv('DUNE_DEX_VOLUME_QUERY_ID')
        }

    def _demo_signal(self, name):
        # Demo mode: return random signals for testing
        return {
            'type': name,
            'signal': random.choice(['BULLISH', 'BEARISH', 'NEUTRAL']),
            'confidence': round(random.uniform(0.4, 0.9), 2),
            'details': 'Demo mode signal'
        }

    def analyze_exchange_flows(self):
        if self.demo_mode:
            return self._demo_signal('exchange_flows')
        qid = self.query_ids['exchange_flows']
        if not qid:
            return {'type': 'exchange_flows', 'signal': 'NEUTRAL', 'confidence': 0.5, 'details': 'No query ID set'}
        try:
            data = self.api.get_query_results(qid)
            # Example: bullish if inflows > outflows, bearish if outflows > inflows
            inflow = sum(row['value_usd'] for row in data['result']['rows'] if row.get('flow_type') == 'Inflow')
            outflow = sum(row['value_usd'] for row in data['result']['rows'] if row.get('flow_type') == 'Outflow')
            if inflow > outflow:
                signal = 'BULLISH'
                confidence = min(1.0, 0.5 + (inflow - outflow) / (inflow + outflow + 1e-6))
            elif outflow > inflow:
                signal = 'BEARISH'
                confidence = min(1.0, 0.5 + (outflow - inflow) / (inflow + outflow + 1e-6))
            else:
                signal = 'NEUTRAL'
                confidence = 0.5
            return {'type': 'exchange_flows', 'signal': signal, 'confidence': round(confidence, 2), 'details': {'inflow': inflow, 'outflow': outflow}}
        except Exception as e:
            return {'type': 'exchange_flows', 'signal': 'NEUTRAL', 'confidence': 0.5, 'details': str(e)}

    def analyze_whale_activity(self):
        if self.demo_mode:
            return self._demo_signal('whale_activity')
        qid = self.query_ids['whale_activity']
        if not qid:
            return {'type': 'whale_activity', 'signal': 'NEUTRAL', 'confidence': 0.5, 'details': 'No query ID set'}
        try:
            data = self.api.get_query_results(qid)
            whale_trades = [row for row in data['result']['rows'] if row.get('whale_category') in ['Mega-Whale', 'Large Whale', 'Whale']]
            count = len(whale_trades)
            if count > 10:
                signal = 'BULLISH'
                confidence = min(1.0, 0.5 + count / 50)
            elif count < 3:
                signal = 'BEARISH'
                confidence = 0.5
            else:
                signal = 'NEUTRAL'
                confidence = 0.6
            return {'type': 'whale_activity', 'signal': signal, 'confidence': round(confidence, 2), 'details': {'whale_trades': count}}
        except Exception as e:
            return {'type': 'whale_activity', 'signal': 'NEUTRAL', 'confidence': 0.5, 'details': str(e)}

    def analyze_defi_liquidations(self):
        if self.demo_mode:
            return self._demo_signal('defi_liquidations')
        qid = self.query_ids['defi_liquidations']
        if not qid:
            return {'type': 'defi_liquidations', 'signal': 'NEUTRAL', 'confidence': 0.5, 'details': 'No query ID set'}
        try:
            data = self.api.get_query_results(qid)
            total_liquidations = sum(row['liquidated_amount_usd'] for row in data['result']['rows'])
            if total_liquidations > 1_000_000:
                signal = 'RISK_OFF'
                confidence = min(1.0, 0.5 + total_liquidations / 10_000_000)
            else:
                signal = 'NEUTRAL'
                confidence = 0.5
            return {'type': 'defi_liquidations', 'signal': signal, 'confidence': round(confidence, 2), 'details': {'total_liquidations': total_liquidations}}
        except Exception as e:
            return {'type': 'defi_liquidations', 'signal': 'NEUTRAL', 'confidence': 0.5, 'details': str(e)}

    def analyze_stablecoin_flows(self):
        if self.demo_mode:
            return self._demo_signal('stablecoin_flows')
        qid = self.query_ids['stablecoin_flows']
        if not qid:
            return {'type': 'stablecoin_flows', 'signal': 'NEUTRAL', 'confidence': 0.5, 'details': 'No query ID set'}
        try:
            data = self.api.get_query_results(qid)
            to_exchange = sum(row['value_usd'] for row in data['result']['rows'] if row.get('flow_type') == 'To Exchange')
            from_exchange = sum(row['value_usd'] for row in data['result']['rows'] if row.get('flow_type') == 'From Exchange')
            if to_exchange > from_exchange:
                signal = 'BULLISH'
                confidence = min(1.0, 0.5 + (to_exchange - from_exchange) / (to_exchange + from_exchange + 1e-6))
            elif from_exchange > to_exchange:
                signal = 'BEARISH'
                confidence = min(1.0, 0.5 + (from_exchange - to_exchange) / (to_exchange + from_exchange + 1e-6))
            else:
                signal = 'NEUTRAL'
                confidence = 0.5
            return {'type': 'stablecoin_flows', 'signal': signal, 'confidence': round(confidence, 2), 'details': {'to_exchange': to_exchange, 'from_exchange': from_exchange}}
        except Exception as e:
            return {'type': 'stablecoin_flows', 'signal': 'NEUTRAL', 'confidence': 0.5, 'details': str(e)}

    def analyze_dex_volume(self):
        if self.demo_mode:
            return self._demo_signal('dex_volume')
        qid = self.query_ids['dex_volume']
        if not qid:
            return {'type': 'dex_volume', 'signal': 'NEUTRAL', 'confidence': 0.5, 'details': 'No query ID set'}
        try:
            data = self.api.get_query_results(qid)
            high_volume_trades = [row for row in data['result']['rows'] if row.get('volume_category') == 'High Volume']
            count = len(high_volume_trades)
            if count > 20:
                signal = 'BULLISH'
                confidence = min(1.0, 0.5 + count / 100)
            elif count < 5:
                signal = 'BEARISH'
                confidence = 0.5
            else:
                signal = 'NEUTRAL'
                confidence = 0.6
            return {'type': 'dex_volume', 'signal': signal, 'confidence': round(confidence, 2), 'details': {'high_volume_trades': count}}
        except Exception as e:
            return {'type': 'dex_volume', 'signal': 'NEUTRAL', 'confidence': 0.5, 'details': str(e)}

    def get_composite_signal(self):
        signals = {
            'exchange_flows': self.analyze_exchange_flows(),
            'whale_activity': self.analyze_whale_activity(),
            'defi_liquidations': self.analyze_defi_liquidations(),
            'stablecoin_flows': self.analyze_stablecoin_flows(),
            'dex_volume': self.analyze_dex_volume()
        }
        # Weighted composite score
        composite_score = 0.0
        for key, signal in signals.items():
            composite_score += WEIGHTS[key] * signal['confidence']
        # Determine composite signal
        bullish = sum(1 for s in signals.values() if s['signal'] == 'BULLISH')
        bearish = sum(1 for s in signals.values() if s['signal'] == 'BEARISH')
        risk_off = sum(1 for s in signals.values() if s['signal'] == 'RISK_OFF')
        if risk_off > 0:
            composite_signal = 'RISK_OFF'
        elif bullish > bearish:
            composite_signal = 'BULLISH'
        elif bearish > bullish:
            composite_signal = 'BEARISH'
        else:
            composite_signal = 'NEUTRAL'
        return {
            'signals': signals,
            'composite_signal': composite_signal,
            'composite_score': round(composite_score, 2)
        }
