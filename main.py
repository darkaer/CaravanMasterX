#!/usr/bin/env python3
"""
CaravanMaster Enhanced Trading Framework
Integrating Perplexity API for market intelligence
"""

import sys
import os
import logging
import asyncio
from datetime import datetime
import json
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from apis.pionex_api import PionexAPI
from apis.dune_api import DuneAPI
from apis.perplexity_api import PerplexityAPI
from strategy.caravanmaster import EnhancedCaravanMasterStrategy
from intelligence.market_analyzer import MarketIntelligenceEngine
from config.settings import TRADING_CONFIG
from config.api_keys import API_KEYS

load_dotenv()

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/caravanmaster_enhanced_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class EnhancedCaravanMasterBot:
    def __init__(self):
        logger.info("🚀 Initializing Enhanced CaravanMaster Trading Framework v3.0")
        
        # Initialize APIs
        self.pionex_api = PionexAPI(
            api_key=API_KEYS['PIONEX_API_KEY'],
            api_secret=API_KEYS['PIONEX_API_SECRET']
        )
        
        self.dune_api = DuneAPI()
        
        self.perplexity_api = PerplexityAPI(
            api_key=API_KEYS['PERPLEXITY_API_KEY']
        )
        
        # Initialize market intelligence engine
        self.market_intelligence = MarketIntelligenceEngine(
            perplexity_api=self.perplexity_api,
            pionex_api=self.pionex_api
        )
        
        # Initialize enhanced strategy
        self.strategy = EnhancedCaravanMasterStrategy(
            pionex_api=self.pionex_api,
            dune_api=self.dune_api,
            perplexity_api=self.perplexity_api,
            config=TRADING_CONFIG
        )
        
        logger.info("✅ Enhanced CaravanMaster initialization complete")
        
    async def run_enhanced_analysis(self):
        """Execute complete enhanced analysis with Perplexity intelligence"""
        try:
            logger.info("🔍 Starting Enhanced CaravanMaster Analysis")
            
            # Get current portfolio status
            portfolio = await self.strategy.get_enhanced_portfolio_status()
            
            # Generate market intelligence using Perplexity
            market_intelligence = await self.market_intelligence.generate_market_analysis()
            
            # Execute enhanced four-tier analysis
            analysis = await self.strategy.execute_enhanced_four_tier_analysis(
                market_intelligence=market_intelligence
            )
            
            # Generate precision trading signals
            signals = await self.strategy.generate_precision_signals(analysis)
            
            # Display enhanced results
            self.display_enhanced_results(portfolio, market_intelligence, signals)
            
            return {
                'portfolio': portfolio,
                'market_intelligence': market_intelligence,
                'analysis': analysis,
                'signals': signals
            }
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced analysis: {e}")
            raise
    
    def display_enhanced_results(self, portfolio, intelligence, signals):
        """Display enhanced trading results with institutional formatting"""
        print("\n" + "="*80)
        print("🎯 CARAVANMASTER ENHANCED STRATEGY REPORT")
        print("="*80)
        
        # Portfolio Status
        if portfolio:
            print(f"💰 Available Balance: {portfolio.get('usdt_balance', 'N/A')} USDT")
            print(f"📊 Portfolio Health: {portfolio.get('portfolio_health', 'Unknown')}")
            
        # Market Intelligence Summary
        if intelligence:
            print(f"\n🧠 AI Market Intelligence:")
            print(f"   • Market Sentiment: {intelligence.get('sentiment', 'Neutral')}")
            print(f"   • Key Insights: {intelligence.get('key_insights', 'Processing...')}")
            
        # Enhanced Trading Signals
        if signals:
            print(f"\n🎯 Enhanced Trading Signals:")
            for signal in signals:
                print(f"   • {signal['symbol']}: {signal['action']}")
                print(f"     Entry: ${signal.get('entry_price', 'N/A')}")
                print(f"     TP: ${signal.get('take_profit', 'N/A')}")
                print(f"     SL: ${signal.get('stop_loss', 'N/A')}")
                print(f"     Leverage: {signal.get('leverage', 'N/A')}x")
                print(f"     Confidence: {signal.get('confidence', 0):.1%}")
        
        print("="*80)

if __name__ == "__main__":
    async def main():
        bot = EnhancedCaravanMasterBot()
        await bot.run_enhanced_analysis()
    
    asyncio.run(main())
