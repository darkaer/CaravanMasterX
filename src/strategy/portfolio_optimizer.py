import numpy as np
import pandas as pd
from scipy.optimize import minimize
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class OptimizationResult:
    """Portfolio optimization results"""
    weights: np.ndarray
    expected_return: float
    volatility: float
    sharpe_ratio: float
    timestamp: datetime

class PortfolioOptimizer:
    """
    Enhanced Portfolio Optimization for CaravanMasterX
    Implements Modern Portfolio Theory with crypto-specific adjustments
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate
        self.logger = logging.getLogger(__name__)
        
    def calculate_efficient_frontier(self, returns: pd.DataFrame, 
                                   target_returns: np.ndarray) -> List[OptimizationResult]:
        """
        Calculate efficient frontier for cryptocurrency portfolio
        
        Args:
            returns: DataFrame with asset returns
            target_returns: Array of target return levels
            
        Returns:
            List of optimization results for each target return
        """
        results = []
        
        # Calculate expected returns and covariance matrix
        mean_returns = returns.mean() * 252  # Annualized
        cov_matrix = returns.cov() * 252     # Annualized
        
        for target_return in target_returns:
            try:
                result = self._optimize_portfolio(
                    mean_returns, cov_matrix, target_return
                )
                results.append(result)
            except Exception as e:
                self.logger.warning(f"Optimization failed for target return {target_return}: {e}")
                
        return results
    
    def maximize_sharpe_ratio(self, returns: pd.DataFrame) -> OptimizationResult:
        """
        Find portfolio with maximum Sharpe ratio
        
        Args:
            returns: DataFrame with asset returns
            
        Returns:
            Optimization result with maximum Sharpe ratio
        """
        mean_returns = returns.mean() * 252
        cov_matrix = returns.cov() * 252
        n_assets = len(mean_returns)
        
        # Objective function: negative Sharpe ratio
        def negative_sharpe(weights):
            portfolio_return = np.sum(weights * mean_returns)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe = (portfolio_return - self.risk_free_rate) / portfolio_vol
            return -sharpe
        
        # Constraints and bounds
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Initial guess (equal weights)
        initial_guess = np.array([1/n_assets] * n_assets)
        
        # Optimize
        result = minimize(negative_sharpe, initial_guess, 
                         method='SLSQP', bounds=bounds, constraints=constraints)
        
        if result.success:
            weights = result.x
            portfolio_return = np.sum(weights * mean_returns)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol
            
            return OptimizationResult(
                weights=weights,
                expected_return=portfolio_return,
                volatility=portfolio_vol,
                sharpe_ratio=sharpe_ratio,
                timestamp=datetime.now()
            )
        else:
            raise ValueError("Optimization failed")
    
    def dynamic_rebalancing(self, current_weights: np.ndarray, 
                           target_weights: np.ndarray,
                           volatility_adjustment: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate rebalancing adjustments based on volatility
        
        Args:
            current_weights: Current portfolio weights
            target_weights: Target portfolio weights
            volatility_adjustment: Volatility-based adjustment factor
            
        Returns:
            Adjusted weights for rebalancing, trade amounts
        """
        # Apply volatility adjustment to target weights
        adjusted_targets = target_weights * volatility_adjustment
        
        # Normalize to ensure weights sum to 1
        adjusted_targets = adjusted_targets / np.sum(adjusted_targets)
        
        # Calculate rebalancing trades
        trade_amounts = adjusted_targets - current_weights
        
        return adjusted_targets, trade_amounts

    def _optimize_portfolio(self, mean_returns, cov_matrix, target_return) -> OptimizationResult:
        n_assets = len(mean_returns)
        
        # Objective: minimize volatility for a given target return
        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        
        # Constraints: sum(weights) == 1, expected return == target_return
        constraints = (
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'eq', 'fun': lambda x: np.sum(x * mean_returns) - target_return}
        )
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_guess = np.array([1/n_assets] * n_assets)
        
        result = minimize(portfolio_volatility, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if result.success:
            weights = result.x
            portfolio_return = np.sum(weights * mean_returns)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol
            return OptimizationResult(
                weights=weights,
                expected_return=portfolio_return,
                volatility=portfolio_vol,
                sharpe_ratio=sharpe_ratio,
                timestamp=datetime.now()
            )
        else:
            raise ValueError("Efficient frontier optimization failed") 