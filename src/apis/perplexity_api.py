"""
Perplexity API Integration for CaravanMaster
Real-time market intelligence and analysis
"""

import requests
import logging
from datetime import datetime
from typing import Dict, Optional
import os
import re

logger = logging.getLogger(__name__)

class PerplexityAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.model = os.getenv("PERPLEXITY_MODEL", "sonar-reasoning-pro")
        self.temperature = float(os.getenv("PERPLEXITY_TEMPERATURE", 0.2))
        self.max_tokens = int(os.getenv("PERPLEXITY_MAX_TOKENS", 1000))
        
        logger.info("🧠 Perplexity API initialized for market intelligence")
        
    async def generate_market_analysis(self, symbols: list, market_data: dict) -> dict:
        """Generate comprehensive market analysis using Perplexity AI"""
        try:
            # Construct market analysis prompt
            prompt = self._build_market_analysis_prompt(symbols, market_data)
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional cryptocurrency trading analyst providing institutional-grade market intelligence."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = self._parse_market_analysis(result)
                return analysis
            else:
                logger.error(f"Perplexity API error: {response.status_code}")
                return {"error": "API request failed"}
                
        except Exception as e:
            logger.error(f"Error generating market analysis: {e}")
            return {"error": str(e)}
    
    def _build_market_analysis_prompt(self, symbols: list, market_data: dict) -> str:
        """Build comprehensive market analysis prompt with explicit summary request for reasoning models."""
        prompt = f"""
        Analyze current cryptocurrency market conditions for trading decisions:
        
        ASSETS: {', '.join(symbols)}
        CURRENT PRICES:
        """
        
        for symbol in symbols:
            if symbol in market_data:
                data = market_data[symbol]
                prompt += f"""
        {symbol}: ${data.get('price', 'N/A')} (24h: {data.get('change_24h', 'N/A')}%)
        """
        
        prompt += """
        
        Provide analysis for:
        1. Market sentiment and trend direction
        2. Key support/resistance levels
        3. Risk factors and opportunities
        4. Optimal entry zones for long/short positions
        5. Recommended leverage and position sizing
        
        After your reasoning, provide a concise summary of actionable trading recommendations for each asset.
        Format as structured trading intelligence with specific price levels and percentages.
        """
        
        return prompt
    
    def _parse_market_analysis(self, response: dict) -> dict:
        """Parse Perplexity response into structured analysis, extracting summary if reasoning model used. If a JSON object is present after reasoning, extract and return it."""
        try:
            content = response['choices'][0]['message']['content']
            json_obj = self._extract_json_from_reasoning(content)
            if json_obj:
                return json_obj
            summary = self._extract_summary_from_reasoning(content)
            return {
                'timestamp': datetime.now().isoformat(),
                'raw_analysis': content,
                'summary': summary,
                'sentiment': self._extract_sentiment(content),
                'key_insights': self._extract_key_insights(content),
                'trading_recommendations': self._extract_recommendations(content)
            }
        except Exception as e:
            logger.error(f"Error parsing analysis: {e}")
            return {"error": "Analysis parsing failed"}
    
    def _extract_sentiment(self, content: str) -> str:
        """Extract market sentiment from analysis"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['bullish', 'upward', 'positive', 'buy']):
            return 'Bullish'
        elif any(word in content_lower for word in ['bearish', 'downward', 'negative', 'sell']):
            return 'Bearish'
        else:
            return 'Neutral'
    
    def _extract_key_insights(self, content: str) -> list:
        """Extract key trading insights from analysis"""
        # Simplified extraction - would use more sophisticated NLP
        insights = []
        lines = content.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['support', 'resistance', 'trend', 'level']):
                insights.append(line.strip())
        
        return insights[:5]  # Return top 5 insights
    
    def _extract_recommendations(self, content: str) -> dict:
        """Extract specific trading recommendations"""
        return {
            'action': 'ANALYZE',
            'confidence': 0.75,
            'timeframe': '1-24 hours',
            'risk_level': 'Medium'
        }

    def _extract_summary_from_reasoning(self, content: str) -> str:
        """Extract a concise summary or actionable recommendations from reasoning model output."""
        lines = content.split('\n')
        summary_lines = [line for line in lines if line.lower().startswith(('in summary', 'recommendation', 'summary', 'actionable'))]
        if summary_lines:
            return '\n'.join(summary_lines)
        # Fallback: last paragraph
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        return paragraphs[-1] if paragraphs else content

    def _extract_json_from_reasoning(self, content: str):
        """Extract the first valid JSON object from the reasoning model output."""
        match = re.search(r'({.*})', content, re.DOTALL)
        if match:
            json_str = match.group(1)
            try:
                import json
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        return None
