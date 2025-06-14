import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout, Input, Bidirectional
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta
import joblib
import os

class CryptoPricePredictor:
    """
    Advanced LSTM/GRU model for cryptocurrency price prediction
    Implements ensemble methods and sophisticated preprocessing
    """
    
    def __init__(self, sequence_length: int = 60, 
                 prediction_horizon: int = 1,
                 model_type: str = "ensemble"):
        """
        Initialize the predictor
        
        Args:
            sequence_length: Number of time steps to look back
            prediction_horizon: Number of steps to predict ahead
            model_type: 'lstm', 'gru', 'bidirectional', or 'ensemble'
        """
        self.sequence_length = sequence_length
        self.prediction_horizon = prediction_horizon
        self.model_type = model_type
        self.scalers = {}
        self.models = {}
        self.feature_columns = []
        self.logger = logging.getLogger(__name__)
        
        # Set random seeds for reproducibility
        np.random.seed(42)
        tf.random.set_seed(42)
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare technical indicators and features for model training
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with engineered features
        """
        data = df.copy()
        
        # Technical indicators
        data['sma_20'] = data['close'].rolling(window=20).mean()
        data['sma_50'] = data['close'].rolling(window=50).mean()
        data['ema_12'] = data['close'].ewm(span=12).mean()
        data['ema_26'] = data['close'].ewm(span=26).mean()
        
        # MACD
        data['macd'] = data['ema_12'] - data['ema_26']
        data['macd_signal'] = data['macd'].ewm(span=9).mean()
        data['macd_histogram'] = data['macd'] - data['macd_signal']
        
        # RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        data['bb_middle'] = data['close'].rolling(window=20).mean()
        bb_std = data['close'].rolling(window=20).std()
        data['bb_upper'] = data['bb_middle'] + (bb_std * 2)
        data['bb_lower'] = data['bb_middle'] - (bb_std * 2)
        data['bb_width'] = (data['bb_upper'] - data['bb_lower']) / data['bb_middle']
        data['bb_position'] = (data['close'] - data['bb_lower']) / (data['bb_upper'] - data['bb_lower'])
        
        # Remove rows with NaN values
        data = data.dropna()
        
        # Select feature columns
        self.feature_columns = [
            'close', 'volume', 'sma_20', 'sma_50', 'ema_12', 'ema_26',
            'macd', 'macd_signal', 'macd_histogram', 'rsi',
            'bb_width', 'bb_position'
        ]
        
        return data[self.feature_columns]
    
    def build_ensemble_model(self, input_shape: Tuple, output_shape: int) -> Dict:
        """Build ensemble of different models"""
        models = {
            'lstm': self.build_lstm_model(input_shape, output_shape),
            'gru': self.build_gru_model(input_shape, output_shape),
            'bidirectional': self.build_bidirectional_model(input_shape, output_shape)
        }
        return models
    
    def build_lstm_model(self, input_shape: Tuple, output_shape: int):
        model = Sequential([
            LSTM(64, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(32),
            Dropout(0.2),
            Dense(output_shape)
        ])
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
        return model
    
    def build_gru_model(self, input_shape: Tuple, output_shape: int):
        model = Sequential([
            GRU(64, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            GRU(32),
            Dropout(0.2),
            Dense(output_shape)
        ])
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
        return model
    
    def build_bidirectional_model(self, input_shape: Tuple, output_shape: int):
        model = Sequential([
            Bidirectional(LSTM(64, return_sequences=True), input_shape=input_shape),
            Dropout(0.2),
            Bidirectional(LSTM(32)),
            Dropout(0.2),
            Dense(output_shape)
        ])
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
        return model
    
    def create_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        X, y = [], []
        for i in range(len(data) - self.sequence_length - self.prediction_horizon + 1):
            X.append(data[i:i+self.sequence_length])
            y.append(data[i+self.sequence_length+self.prediction_horizon-1, 0])
        return np.array(X), np.array(y)
    
    def train(self, df: pd.DataFrame, validation_split: float = 0.2, 
              epochs: int = 100, batch_size: int = 32) -> Dict:
        """
        Train the model(s)
        
        Args:
            df: DataFrame with price data
            validation_split: Fraction of data for validation
            epochs: Number of training epochs
            batch_size: Training batch size
            
        Returns:
            Training history and metrics
        """
        # Prepare features
        feature_data = self.prepare_features(df)
        
        # Scale features
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(feature_data)
        self.scalers['features'] = scaler
        
        # Create sequences
        X, y = self.create_sequences(scaled_data)
        
        # Split data
        split_idx = int(len(X) * (1 - validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Callbacks
        callbacks = [
            EarlyStopping(patience=15, restore_best_weights=True),
            ReduceLROnPlateau(factor=0.5, patience=10, min_lr=0.0001)
        ]
        
        training_results = {}
        
        if self.model_type == "ensemble":
            # Train ensemble models
            self.models = self.build_ensemble_model(
                (self.sequence_length, len(self.feature_columns)), 
                self.prediction_horizon
            )
            
            for name, model in self.models.items():
                self.logger.info(f"Training {name} model...")
                history = model.fit(
                    X_train, y_train,
                    validation_data=(X_val, y_val),
                    epochs=epochs,
                    batch_size=batch_size,
                    callbacks=callbacks,
                    verbose=0
                )
                training_results[name] = history.history
        
        return training_results 