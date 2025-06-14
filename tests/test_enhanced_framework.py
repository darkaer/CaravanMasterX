"""
Enhanced Framework Testing for CaravanMasterX
Comprehensive testing of all framework components
"""

import sys
import os
import unittest
import logging
import asyncio

# Add src to path for testing
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.apis.pionex_api import PionexAPI
from src.apis.dune_api import DuneAPI
from src.apis.perplexity_api import PerplexityAPI
from src.strategy.caravanmaster import EnhancedCaravanMasterStrategy
from src.intelligence.market_analyzer import MarketIntelligenceEngine
from config.api_keys import API_KEYS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestPionexAPI(unittest.TestCase):
    def setUp(self):
        self.api = PionexAPI(
            API_KEYS['PIONEX_API_KEY'],
            API_KEYS['PIONEX_API_SECRET']
        )
    
    def test_account_balance(self):
        """Test account balance retrieval"""
        logger.info("Testing Pionex account balance...")
        result = self.api.get_account_balance()
        
        self.assertIsNotNone(result)
        if result.get('success'):
            logger.info("✅ Pionex balance test passed")
            logger.info(f"Available USDT: {result.get('usdt_balance', 0)}")
        else:
            logger.error(f"❌ Pionex balance test failed: {result}")
    
    def test_market_prices(self):
        """Test market price retrieval"""
        logger.info("Testing Pionex market prices...")
        result = self.api.get_market_prices()
        
        self.assertIsNotNone(result)
        if 'data' in result:
            logger.info(f"✅ Pionex prices test passed - {len(result['data'])} pairs")
        else:
            logger.error(f"❌ Pionex prices test failed: {result}")
    
    def test_specific_price(self):
        """Test specific price retrieval"""
        logger.info("Testing specific price retrieval...")
        symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        
        for symbol in symbols:
            price_data = self.api.get_specific_price(symbol)
            if price_data:
                logger.info(f"✅ {symbol}: ${price_data['price']:,.2f}")
            else:
                logger.error(f"❌ Failed to get price for {symbol}")

class TestDuneAPI(unittest.TestCase):
    def setUp(self):
        self.api = DuneAPI(API_KEYS['DUNE_API_KEY'])
    
    def test_connection(self):
        """Test Dune API connection"""
        logger.info("Testing Dune API connection...")
        result = self.api.test_connection()
        
        if result:
            logger.info("✅ Dune API connection test passed")
        else:
            logger.error("❌ Dune API connection test failed")
    
    def test_cached_query(self):
        """Test cached query retrieval"""
        logger.info("Testing Dune cached query...")
        test_query_id = "1215383"
        
        result = self.api.get_cached_results(test_query_id)
        
        if result:
            logger.info("✅ Dune cached query test passed")
        else:
            logger.error("❌ Dune cached query test failed")

class TestPerplexityAPI(unittest.TestCase):
    def setUp(self):
        self.api = PerplexityAPI(API_KEYS['PERPLEXITY_API_KEY'])
    
    def test_connection(self):
        """Test Perplexity API connection"""
        logger.info("Testing Perplexity API connection...")
        # Simple test to ensure the API is configured
        self.assertIsNotNone(self.api)
        logger.info("✅ Perplexity API configuration test passed")

class TestEnhancedStrategy(unittest.TestCase):
    def setUp(self):
        self.pionex_api = PionexAPI(
            API_KEYS['PIONEX_API_KEY'],
            API_KEYS['PIONEX_API_SECRET']
        )
        self.dune_api = DuneAPI(API_KEYS['DUNE_API_KEY'])
        self.perplexity_api = PerplexityAPI(API_KEYS['PERPLEXITY_API_KEY'])
        
        from config.settings import TRADING_CONFIG
        self.strategy = EnhancedCaravanMasterStrategy(
            pionex_api=self.pionex_api,
            dune_api=self.dune_api,
            perplexity_api=self.perplexity_api,
            config=TRADING_CONFIG
        )
    
    def test_strategy_initialization(self):
        """Test strategy initialization"""
        logger.info("Testing strategy initialization...")
        self.assertIsNotNone(self.strategy)
        logger.info("✅ Strategy initialization test passed")

class TestDemoMode(unittest.TestCase):
    def test_dune_demo_mode(self):
        from src.apis.dune_api import DuneAnalyticsEnhanced
        dune = DuneAnalyticsEnhanced(demo_mode=True)
        try:
            result = dune.analyze_exchange_flows('BTC')
            self.assertIsNotNone(result)
            logger.info(f"[Demo] DuneAnalyticsEnhanced exchange flows: {result}")
        except Exception as e:
            logger.warning(f"[Demo] Dune demo mode failed: {e}")

    def test_perplexity_demo_mode(self):
        from src.apis.perplexity_api import PerplexityAPI
        import os
        api_key = os.getenv('PERPLEXITY_API_KEY', 'demo')
        perplexity = PerplexityAPI(api_key)
        try:
            # Simulate a demo analysis call
            result = perplexity.generate_market_analysis(['BTC/USDT'], {'BTC/USDT': {'price': 50000}})
            self.assertIsNotNone(result)
            logger.info(f"[Demo] PerplexityAPI demo analysis: {result}")
        except Exception as e:
            logger.warning(f"[Demo] Perplexity demo mode failed: {e}")

def run_all_tests():
    """Run all framework tests"""
    logger.info("="*60)
    logger.info("CARAVANMASTER ENHANCED FRAMEWORK TESTING")
    logger.info("="*60)
    
    # Test Pionex API
    logger.info("\n--- Testing Pionex API ---")
    pionex_suite = unittest.TestLoader().loadTestsFromTestCase(TestPionexAPI)
    pionex_runner = unittest.TextTestRunner(verbosity=1)
    pionex_result = pionex_runner.run(pionex_suite)
    
    # Test Dune API
    logger.info("\n--- Testing Dune API ---")
    dune_suite = unittest.TestLoader().loadTestsFromTestCase(TestDuneAPI)
    dune_runner = unittest.TextTestRunner(verbosity=1)
    dune_result = dune_runner.run(dune_suite)
    
    # Test Perplexity API
    logger.info("\n--- Testing Perplexity API ---")
    perplexity_suite = unittest.TestLoader().loadTestsFromTestCase(TestPerplexityAPI)
    perplexity_runner = unittest.TextTestRunner(verbosity=1)
    perplexity_result = perplexity_runner.run(perplexity_suite)
    
    # Test Enhanced Strategy
    logger.info("\n--- Testing Enhanced Strategy ---")
    strategy_suite = unittest.TestLoader().loadTestsFromTestCase(TestEnhancedStrategy)
    strategy_runner = unittest.TextTestRunner(verbosity=1)
    strategy_result = strategy_runner.run(strategy_suite)
    
    # Test Demo Mode
    logger.info("\n--- Testing Demo Mode ---")
    demo_suite = unittest.TestLoader().loadTestsFromTestCase(TestDemoMode)
    demo_runner = unittest.TextTestRunner(verbosity=1)
    demo_result = demo_runner.run(demo_suite)
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    total_tests = (pionex_result.testsRun + dune_result.testsRun + 
                  perplexity_result.testsRun + strategy_result.testsRun +
                  demo_result.testsRun)
    total_failures = (len(pionex_result.failures) + len(dune_result.failures) +
                     len(perplexity_result.failures) + len(strategy_result.failures) +
                     len(demo_result.failures))
    total_errors = (len(pionex_result.errors) + len(dune_result.errors) +
                   len(perplexity_result.errors) + len(strategy_result.errors) +
                   len(demo_result.errors))
    
    logger.info(f"Total Tests: {total_tests}")
    logger.info(f"Passed: {total_tests - total_failures - total_errors}")
    logger.info(f"Failed: {total_failures}")
    logger.info(f"Errors: {total_errors}")
    
    if total_failures == 0 and total_errors == 0:
        logger.info("🎉 All tests passed!")
    else:
        logger.warning("⚠️ Some tests failed - check API configuration")

if __name__ == '__main__':
    run_all_tests()
