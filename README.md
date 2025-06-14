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