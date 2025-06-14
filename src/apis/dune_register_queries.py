from dune_api import DuneAPI

EXCHANGE_FLOW_SQL = """
SELECT
  block_time,
  from_address,
  to_address,
  value_eth,
  value_usd,
  CASE
    WHEN to_address IN (SELECT address FROM exchanges) THEN 'Inflow'
    WHEN from_address IN (SELECT address FROM exchanges) THEN 'Outflow'
    ELSE 'Wallet Transfer'
  END AS flow_type
FROM ethereum.transactions
WHERE
  (to_address IN (SELECT address FROM exchanges) OR from_address IN (SELECT address FROM exchanges))
  AND block_time > now() - interval '24 hours'
  AND value_eth > 1;
"""

WHALE_ACTIVITY_SQL = """
SELECT
  block_time,
  from_address,
  to_address,
  value_eth,
  value_usd,
  CASE
    WHEN value_usd > 50000000 THEN 'Mega-Whale'
    WHEN value_usd > 10000000 THEN 'Large Whale'
    WHEN value_usd > 1000000 THEN 'Whale'
    ELSE 'Small'
  END AS whale_category
FROM ethereum.transactions
WHERE
  value_usd > 1000000
  AND block_time > now() - interval '4 hours';
"""

DEFI_LIQUIDATIONS_SQL = """
SELECT
  protocol,
  liquidator,
  liquidated_amount_usd,
  collateral_amount_usd,
  block_time
FROM defi_liquidations
WHERE
  protocol IN ('AaveV2', 'AaveV3', 'CompoundV2')
  AND block_time > now() - interval '6 hours';
"""

STABLECOIN_FLOWS_SQL = """
SELECT
  block_time,
  from_address,
  to_address,
  token_symbol,
  value_eth,
  value_usd,
  CASE
    WHEN to_address IN (SELECT address FROM exchanges) THEN 'To Exchange'
    WHEN from_address IN (SELECT address FROM exchanges) THEN 'From Exchange'
    ELSE 'Wallet Transfer'
  END AS flow_type
FROM erc20_transfers
WHERE
  token_symbol IN ('USDT', 'USDC')
  AND value_usd > 100000
  AND block_time > now() - interval '12 hours';
"""

DEX_VOLUME_SQL = """
SELECT
  trade_time,
  pair,
  volume_usd,
  trade_amount_eth,
  trader_address,
  CASE
    WHEN volume_usd > 10000 THEN 'High Volume'
    ELSE 'Normal'
  END AS volume_category
FROM dex_trades
WHERE
  trade_time > now() - interval '6 hours'
  AND volume_usd > 1000;
"""

def main():
    dune = DuneAPI()
    queries = {
        'exchange_flow': EXCHANGE_FLOW_SQL,
        'whale_activity': WHALE_ACTIVITY_SQL,
        'liquidations': DEFI_LIQUIDATIONS_SQL,
        'stablecoin_flows': STABLECOIN_FLOWS_SQL,
        'dex_volume': DEX_VOLUME_SQL
    }
    for name, sql in queries.items():
        try:
            qid = dune.create_query(sql)
            print(f"{name} query ID: {qid}")
        except Exception as e:
            print(f"Error creating {name} query: {e}")

if __name__ == "__main__":
    main() 