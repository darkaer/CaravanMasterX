import asyncio
import aiohttp
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import time
import logging
from datetime import datetime
import json

@dataclass
class DuneQuery:
    """Dune Analytics query configuration"""
    query_id: int
    name: str
    description: str
    parameters: Dict[str, Any] = None
    cache_duration: int = 300  # 5 minutes default cache

@dataclass
class DuneResponse:
    """Dune Analytics API response"""
    data: pd.DataFrame
    execution_id: str
    query_id: int
    execution_time: float
    row_count: int
    timestamp: datetime

class DuneAPIClient:
    """
    Enhanced Dune Analytics API client for CaravanMasterX
    Optimized for Analyst tier account with proper rate limiting and caching
    """
    
    def __init__(self, api_key: str, max_requests_per_minute: int = 40):
        """
        Initialize Dune API client
        
        Args:
            api_key: Dune Analytics API key
            max_requests_per_minute: Rate limit (40 for Analyst tier)
        """
        self.api_key = api_key
        self.base_url = "https://api.dune.com/api/v1"
        self.max_requests_per_minute = max_requests_per_minute
        self.request_times = []
        self.cache = {}
        self.logger = logging.getLogger(__name__)
        
        # Headers for API requests
        self.headers = {
            "X-Dune-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    async def execute_query(self, query: DuneQuery, 
                           use_cache: bool = True) -> DuneResponse:
        """
        Execute a Dune Analytics query with caching and rate limiting
        
        Args:
            query: DuneQuery object with query configuration
            use_cache: Whether to use cached results
            
        Returns:
            DuneResponse with query results
        """
        # Check cache first
        if use_cache and self._is_cached(query):
            self.logger.info(f"Using cached result for query {query.query_id}")
            return self.cache[self._get_cache_key(query)]
        
        # Rate limiting
        await self._rate_limit()
        
        start_time = time.time()
        
        try:
            # Execute query
            execution_id = await self._start_execution(query)
            
            # Wait for completion
            result_data = await self._wait_for_completion(execution_id)
            
            # Process results
            df = pd.DataFrame(result_data.get('rows', []))
            execution_time = time.time() - start_time
            
            response = DuneResponse(
                data=df,
                execution_id=execution_id,
                query_id=query.query_id,
                execution_time=execution_time,
                row_count=len(df),
                timestamp=datetime.now()
            )
            
            # Cache the result
            if use_cache:
                self._cache_result(query, response)
            
            self.logger.info(f"Query {query.query_id} completed in {execution_time:.2f}s with {len(df)} rows")
            return response
            
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            raise
    
    async def get_whale_transactions(self, min_value_usd: float = 1000000,
                                   hours_back: int = 24) -> pd.DataFrame:
        """
        Get large cryptocurrency transactions (whale tracking)
        
        Args:
            min_value_usd: Minimum transaction value in USD
            hours_back: Hours to look back
            
        Returns:
            DataFrame with whale transactions
        """
        whale_query = DuneQuery(
            query_id=12345,  # Replace with actual whale tracking query ID
            name="Whale Transactions",
            description="Track large cryptocurrency transactions",
            parameters={
                "min_value": min_value_usd,
                "hours_back": hours_back
            }
        )
        
        response = await self.execute_query(whale_query)
        return response.data
    
    async def get_mvrv_data(self, assets: List[str] = None) -> pd.DataFrame:
        """
        Get Market Value to Realized Value (MVRV) data
        
        Args:
            assets: List of assets to get MVRV data for
            
        Returns:
            DataFrame with MVRV ratios
        """
        if assets is None:
            assets = ['bitcoin', 'ethereum']
        
        mvrv_query = DuneQuery(
            query_id=23456,  # Replace with actual MVRV query ID
            name="MVRV Analysis",
            description="Market Value to Realized Value ratios",
            parameters={"assets": assets}
        )
        
        response = await self.execute_query(mvrv_query)
        return response.data
    
    def _get_cache_key(self, query: DuneQuery) -> str:
        key = f"{query.query_id}:{json.dumps(query.parameters, sort_keys=True) if query.parameters else ''}"
        return key
    
    def _is_cached(self, query: DuneQuery) -> bool:
        key = self._get_cache_key(query)
        if key in self.cache:
            cached_response = self.cache[key]
            age = (datetime.now() - cached_response.timestamp).total_seconds()
            return age < query.cache_duration
        return False
    
    def _cache_result(self, query: DuneQuery, response: DuneResponse):
        key = self._get_cache_key(query)
        self.cache[key] = response
    
    async def _rate_limit(self):
        now = time.time()
        self.request_times = [t for t in self.request_times if now - t < 60]
        if len(self.request_times) >= self.max_requests_per_minute:
            sleep_time = 60 - (now - self.request_times[0])
            self.logger.info(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
            await asyncio.sleep(sleep_time)
        self.request_times.append(time.time())
    
    async def _start_execution(self, query: DuneQuery) -> str:
        url = f"{self.base_url}/query/{query.query_id}/execute"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=query.parameters or {}) as resp:
                if resp.status != 200:
                    raise Exception(f"Failed to start query execution: {resp.status} {await resp.text()}")
                data = await resp.json()
                return data.get('execution_id')
    
    async def _wait_for_completion(self, execution_id: str, timeout: int = 120) -> Dict:
        url = f"{self.base_url}/execution/{execution_id}/results"
        start = time.time()
        async with aiohttp.ClientSession() as session:
            while True:
                async with session.get(url, headers=self.headers) as resp:
                    if resp.status != 200:
                        raise Exception(f"Failed to get query results: {resp.status} {await resp.text()}")
                    data = await resp.json()
                    if data.get('state') == 'QUERY_STATE_COMPLETED':
                        return data['result']
                    elif data.get('state') in ['QUERY_STATE_FAILED', 'QUERY_STATE_CANCELLED']:
                        raise Exception(f"Query execution failed: {data.get('state')}")
                    if time.time() - start > timeout:
                        raise TimeoutError("Query execution timed out")
                    await asyncio.sleep(2) 