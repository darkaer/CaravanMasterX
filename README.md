## Phase 2: Testing and Validation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.template` to `.env` and fill in your API keys and settings. For demo mode, you can leave API keys as 'demo' or blank.

### 3. Run All Tests (including Demo Mode)
```bash
python -m unittest tests/test_enhanced_framework.py
```

- Demo mode tests will run even if API keys are not set, providing safe validation of Dune and Perplexity integrations.
- For live API validation, ensure your `.env` contains valid API keys.

### 4. Troubleshooting
- If any test fails, check your `.env` configuration and logs in the `logs/` directory.
- For institutional-grade analytics, ensure all dependencies are installed and your API quotas are sufficient.

## Usage Example: EnhancedCaravanMasterX

```python
from src.strategy.enhanced_caravanmasterx import EnhancedCaravanMasterX
from config.api_keys import API_KEYS
import pandas as pd

config = {
    'dune_api_key': API_KEYS['DUNE_API_KEY'],
    'base_risk_per_trade': 0.01,
    'max_portfolio_risk': 0.30,
    'max_total_exposure': 0.90,
    'ml_sequence_length': 60,
    'ml_prediction_horizon': 1,
    'ml_model_type': 'ensemble',
    'assets': ['BTC-USD', 'ETH-USD', 'SOL-USD']
}
orchestrator = EnhancedCaravanMasterX(config)

# Mock price data for demonstration
price_data = {
    'BTC-USD': pd.DataFrame({'close': [70000, 70500, 71000, 71500, 72000], 'volume': [100, 110, 120, 130, 140]}),
    'ETH-USD': pd.DataFrame({'close': [3500, 3550, 3600, 3650, 3700], 'volume': [200, 210, 220, 230, 240]}),
    'SOL-USD': pd.DataFrame({'close': [150, 152, 154, 156, 158], 'volume': [300, 310, 320, 330, 340]})
}

import asyncio
signals = asyncio.run(orchestrator.generate_trading_signals(price_data))
for sig in signals:
    print(sig)
```

- The `config` dictionary controls all major parameters.
- Pass real or mock price data as a dictionary of DataFrames.
- The orchestrator will generate enhanced trading signals using all integrated modules. 