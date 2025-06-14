import os
from .dune_api import DuneAPI

class DuneIntegration:
    def __init__(self):
        self.api = DuneAPI(api_key=os.getenv('DUNE_API_KEY'))
        self.query_ids = {
            'exchange_flow': os.getenv('DUNE_EXCHANGE_FLOW_QUERY_ID'),
            'whale_activity': os.getenv('DUNE_WHALE_ACTIVITY_QUERY_ID'),
            'liquidations': os.getenv('DUNE_DEFI_LIQUIDATION_QUERY_ID'),
            'stablecoin_flows': os.getenv('DUNE_STABLECOIN_FLOW_QUERY_ID'),
            'dex_volume': os.getenv('DUNE_DEX_VOLUME_QUERY_ID')
        }

    def fetch_all(self):
        results = {}
        for key, qid in self.query_ids.items():
            if qid:
                try:
                    results[key] = self.api.execute_query(qid)
                except Exception as e:
                    print(f"Error fetching {key}: {e}")
            else:
                print(f"Query ID for {key} not set.")
        return results 