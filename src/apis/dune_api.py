"""
Dune Analytics API Integration for CaravanMasterX
On-chain intelligence and blockchain analytics
"""

import requests
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DuneAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.dune.com/api/v1"
        
        logger.info("Dune Analytics API initialized")
        
    def execute_query(self, query_id, parameters=None):
        """Execute a Dune query and return fresh results"""
        try:
            # Step 1: Execute the query
            exec_data = {}
            if parameters:
                exec_data['query_parameters'] = parameters
                
            exec_response = requests.post(
                f"{self.base_url}/query/{query_id}/execute",
                headers={"X-DUNE-API-KEY": self.api_key},
                json=exec_data if exec_data else None
            )
            
            if exec_response.status_code != 200:
                logger.error(f"Failed to execute query {query_id}: {exec_response.text}")
                return None
                
            execution_data = exec_response.json()
            execution_id = execution_data.get("execution_id")
            
            if not execution_id:
                logger.error(f"No execution_id returned for query {query_id}")
                return None
            
            # Step 2: Poll for status
            max_attempts = 30
            for attempt in range(max_attempts):
                status_response = requests.get(
                    f"{self.base_url}/execution/{execution_id}/status",
                    headers={"X-DUNE-API-KEY": self.api_key}
                )
                
                if status_response.status_code != 200:
                    logger.error(f"Failed to get status for execution {execution_id}")
                    return None
                
                status_data = status_response.json()
                state = status_data.get("state")
                
                if state == "QUERY_STATE_COMPLETED":
                    break
                elif state == "QUERY_STATE_FAILED":
                    logger.error(f"Query {query_id} failed: {status_data}")
                    return None
                    
                time.sleep(2)
            else:
                logger.error(f"Query {query_id} timed out after {max_attempts} attempts")
                return None
            
            # Step 3: Fetch results
            results_response = requests.get(
                f"{self.base_url}/execution/{execution_id}/results",
                headers={"X-DUNE-API-KEY": self.api_key}
            )
            
            if results_response.status_code != 200:
                logger.error(f"Failed to get results for execution {execution_id}")
                return None
                
            return results_response.json()
            
        except Exception as e:
            logger.error(f"Error executing query {query_id}: {e}")
            return None
    
    def get_cached_results(self, query_id):
        """Get cached results for faster response"""
        try:
            response = requests.get(
                f"{self.base_url}/query/{query_id}/results",
                headers={"X-DUNE-API-KEY": self.api_key}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get cached results for query {query_id}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting cached results for query {query_id}: {e}")
            return None
    
    def get_exchange_flows(self, asset="ETH"):
        """Get exchange inflow/outflow data for specified asset"""
        # These query IDs would need to be replaced with actual Dune query IDs
        query_mappings = {
            "ETH": "1215383",  # Use test query for now
            "BTC": "1746191",  # Historical blockchain data query
            "SOL": "3256410"   # DeFi trading volume query
        }
        
        query_id = query_mappings.get(asset)
        if not query_id:
            logger.warning(f"No exchange flow query configured for {asset}")
            return None
            
        result = self.execute_query(query_id)
        if result and 'result' in result:
            return {
                'asset': asset,
                'exchange_flows': result['result']['rows'],
                'timestamp': datetime.now().isoformat()
            }
        return None
    
    def test_connection(self):
        """Test Dune API connection with a simple query"""
        # Use a known working query ID for testing
        test_query_id = "1215383"  # This is a test query
        
        try:
            result = self.get_cached_results(test_query_id)
            if result:
                logger.info("✅ Dune API connection test successful")
                return True
            else:
                logger.error("❌ Dune API connection test failed")
                return False
        except Exception as e:
            logger.error(f"❌ Dune API connection test failed: {e}")
            return False
