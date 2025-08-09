"""
ML Pipeline for Peer Review System
Handles feature engineering, model training, and scoring
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pickle
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class PeerReviewMLPipeline:
    def __init__(self, db_manager):
        """
        Initialize ML pipeline
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_names = []
        
        # Descriptor to numeric mapping
        self.descriptor_scores = {
            'collaborative': 4.0,
            'neutral': 3.0,
            'withdrawn': 2.0,
            'blocking': 1.0
        }
    
    def engineer_features(self, df):
        """
        Engineer features from raw review data
        
        Args:
            df: DataFrame with review data
            
        Returns:
            DataFrame with engineered features per employee per day
        """
        # Ensure date column is datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Add numeric descriptor score
        df['descriptor_score'] = df['descriptor'].map(self.descriptor_scores)
        
        # Group by reviewee and date for daily aggregation
        daily_features = []
        
        for (reviewee, date), group in df.groupby(['reviewee_id', 'date']):
            features = {
                'employee_id': reviewee,
                'date': date,
                
                # Basic aggregations
                'avg_score': group['score'].mean(),
                'avg_descriptor_score': group['descriptor_score'].mean(),
                'review_count': len(group),
                'score_std': group['score'].std() if len(group) > 1 else 0,
                
                # Descriptor proportions
                'pct_collaborative': (group['descriptor'] == 'collaborative').mean(),
                'pct_withdrawn': (group['descriptor'] == 'withdrawn').mean(),
                'pct_neutral': (group['descriptor'] == 'neutral').mean(),
                'pct_blocking': (group['descriptor'] == 'blocking').mean(),
                
                # Score distribution
                'pct_score_5': (group['score'] == 5).mean(),
                'pct_score_4': (group['score'] == 4).mean(),
                'pct_score_3': (group['score'] == 3).mean(),
                'pct_score_2': (group['score'] == 2).mean(),
                'pct_score_1': (group['score'] == 1).mean(),
                
                # Engagement metrics
                'has_comments': (group['comment'].str.len() > 0).any(),
                'comment_ratio': (group['comment'].str.len() > 0).mean(),
            }
            daily_features.append(features)
        
        features_df = pd.DataFrame(daily_features)
        
        # Add rolling window features
        features_df = self.add_rolling_features(features_df)
        
        return features_df
    
    def add_rolling_features(self, df):
        """Add rolling window features (trends, moving averages)"""
        df = df.sort_values(['employee_id', 'date'])
        
        # Rolling windows: 3, 7, 14 days
        windows = [3, 7, 14]
        
        for window in windows:
            # Rolling averages
            df[f'avg_score_rolling_{window}d'] = df.groupby('employee_id')['avg_score'].transform(
                lambda x: x.rolling(window, min_periods=1).mean()
            )
            
            df[f'pct_collaborative_rolling_{window}d'] = df.groupby('employee_id')['pct_collaborative'].transform(
                lambda x: x.rolling(window, min_periods=1).mean()
            )
            
            df[f'pct_withdrawn_rolling_{window}d'] = df.groupby('employee_id')['pct_withdrawn'].transform(
                lambda x: x.rolling(window, min_periods=1).mean()
            )
            
            # Rolling standard deviations (volatility)
            df[f'score_volatility_{window}d'] = df.groupby('employee_id')['avg_score'].transform(
                lambda x: x.rolling(window, min_periods=1).std()
            )
        
        # Trend features (slope over last 7 and 14 days) - simplified version
        for window in [7, 14]:
            # Simple trend calculation using rolling mean difference
            df[f'score_trend_{window}d'] = df.groupby('employee_id')['avg_score'].transform(
                lambda x: x.diff(window).fillna(0)
            )
            
            df[f'collab_trend_{window}d'] = df.groupby('employee_id')['pct_collaborative'].transform(
                lambda x: x.diff(window).fillna(0)
            )
        
        # Fill NaNs with 0
        df = df.fillna(0)
        
        return df
    
    def _calculate_trend(self, group, column, window):
        """Calculate trend (slope) for a given column over a window"""
        trends = []
        for i in range(len(group)):
            start_idx = max(0, i - window + 1)
            window_data = group.iloc[start_idx:i+1][column]
            
            if len(window_data) >= 2:
                # Simple linear trend (slope)
                x = np.arange(len(window_data))
                slope = np.polyfit(x, window_data, 1)[0]
                trends.append(slope)
            else:
                trends.append(0)
        
        return pd.Series(trends, index=group.index)
    
    def create_composite_score(self, features_df):
        """Create a composite behavioral score"""
        # Weighted combination of key metrics
        weights = {
            'avg_score': 0.3,
            'pct_collaborative': 0.25,
            'pct_withdrawn': -0.15,  # negative weight
            'pct_blocking': -0.2,    # negative weight
            'score_volatility_7d': -0.1  # negative weight (instability is bad)
        }
        
        composite_score = 0
        for feature, weight in weights.items():
            if feature in features_df.columns:
                # Normalize to 0-1 scale
                normalized = (features_df[feature] - features_df[feature].min()) / (
                    features_df[feature].max() - features_df[feature].min() + 1e-8
                )
                composite_score += weight * normalized
        
        # Scale to 1-5 range
        composite_score = 1 + 4 * (composite_score - composite_score.min()) / (
            composite_score.max() - composite_score.min() + 1e-8
        )
        
        return composite_score
    
    def train_models(self, features_df):
        """Train ML models on the features"""
        print("Training ML models...")
        
        # Prepare features for training
        feature_columns = [col for col in features_df.columns 
                          if col not in ['employee_id', 'date']]
        
        X = features_df[feature_columns].fillna(0)
        self.feature_names = feature_columns
        
        # Create composite score as target
        y = self.create_composite_score(features_df)
        features_df['composite_score'] = y
        
        # Train-test split (last 14 days as test)
        test_days = 14
        test_date = features_df['date'].max() - timedelta(days=test_days)
        
        train_mask = features_df['date'] <= test_date
        test_mask = features_df['date'] > test_date
        
        X_train, X_test = X[train_mask], X[test_mask]
        y_train, y_test = y[train_mask], y[test_mask]
        
        # 1. Score Prediction Model (Random Forest)
        self.models['score_predictor'] = RandomForestRegressor(
            n_estimators=100, 
            random_state=42,
            max_depth=10
        )
        self.models['score_predictor'].fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.models['score_predictor'].predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        print(f"Score Predictor - MSE: {mse:.3f}, R²: {r2:.3f}")
        
        # 2. Anomaly Detection Model (Isolation Forest)
        self.scalers['anomaly'] = StandardScaler()
        X_scaled = self.scalers['anomaly'].fit_transform(X)
        
        self.models['anomaly_detector'] = IsolationForest(
            contamination=0.1, 
            random_state=42
        )
        self.models['anomaly_detector'].fit(X_scaled)
        
        # 3. Clustering Model (K-Means for behavior archetypes)
        self.scalers['clustering'] = StandardScaler()
        X_cluster = self.scalers['clustering'].fit_transform(X)
        
        self.models['behavior_clusters'] = KMeans(
            n_clusters=4, 
            random_state=42,
            n_init=10
        )
        self.models['behavior_clusters'].fit(X_cluster)
        
        print("Model training completed!")
        return features_df
    
    def predict_scores(self, features_df):
        """Generate predictions and insights"""
        feature_columns = [col for col in features_df.columns 
                          if col not in ['employee_id', 'date', 'composite_score']]
        
        X = features_df[feature_columns].fillna(0)
        
        predictions = {}
        
        # Score predictions
        if 'score_predictor' in self.models:
            predictions['predicted_score'] = self.models['score_predictor'].predict(X)
        
        # Anomaly detection
        if 'anomaly_detector' in self.models:
            X_scaled = self.scalers['anomaly'].transform(X)
            predictions['anomaly_score'] = self.models['anomaly_detector'].decision_function(X_scaled)
            predictions['is_anomaly'] = self.models['anomaly_detector'].predict(X_scaled) == -1
        
        # Behavior clusters
        if 'behavior_clusters' in self.models:
            X_cluster = self.scalers['clustering'].transform(X)
            predictions['behavior_cluster'] = self.models['behavior_clusters'].predict(X_cluster)
        
        # Add predictions to dataframe
        for key, values in predictions.items():
            features_df[key] = values
        
        return features_df
    
    def get_employee_insights(self, employee_id, days=14):
        """Get insights for a specific employee"""
        # Get recent data
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        df = self.db_manager.get_reviews(start_date=start_date, reviewee_id=employee_id)
        
        if len(df) == 0:
            return {"error": "No recent data found for employee"}
        
        # Engineer features
        features_df = self.engineer_features(df)
        
        # Get predictions
        if self.models:
            features_df = self.predict_scores(features_df)
        
        # Calculate insights
        latest = features_df.iloc[-1]
        
        insights = {
            'employee_id': employee_id,
            'date_range': f"{start_date} to {end_date}",
            'avg_score': latest['avg_score'],
            'composite_score': latest.get('composite_score', 0),
            'collaboration_rate': latest['pct_collaborative'],
            'withdrawn_rate': latest['pct_withdrawn'],
            'score_trend_7d': latest.get('score_trend_7d', 0),
            'is_anomaly': latest.get('is_anomaly', False),
            'behavior_cluster': latest.get('behavior_cluster', 0),
            'total_reviews': features_df['review_count'].sum()
        }
        
        return insights
    
    def save_models(self, models_dir="models"):
        """Save trained models to disk"""
        models_path = Path(models_dir)
        models_path.mkdir(exist_ok=True)
        
        # Save models
        for name, model in self.models.items():
            with open(models_path / f"{name}.pkl", 'wb') as f:
                pickle.dump(model, f)
        
        # Save scalers
        for name, scaler in self.scalers.items():
            with open(models_path / f"scaler_{name}.pkl", 'wb') as f:
                pickle.dump(scaler, f)
        
        # Save feature names
        with open(models_path / "feature_names.pkl", 'wb') as f:
            pickle.dump(self.feature_names, f)
        
        print(f"Models saved to {models_path}")
    
    def load_models(self, models_dir="models"):
        """Load trained models from disk"""
        models_path = Path(models_dir)
        
        if not models_path.exists():
            print("No saved models found")
            return False
        
        try:
            # Load models
            for model_file in models_path.glob("*.pkl"):
                if model_file.stem.startswith("scaler_"):
                    scaler_name = model_file.stem.replace("scaler_", "")
                    with open(model_file, 'rb') as f:
                        self.scalers[scaler_name] = pickle.load(f)
                elif model_file.stem == "feature_names":
                    with open(model_file, 'rb') as f:
                        self.feature_names = pickle.load(f)
                else:
                    with open(model_file, 'rb') as f:
                        self.models[model_file.stem] = pickle.load(f)
            
            print(f"Models loaded from {models_path}")
            return True
            
        except Exception as e:
            print(f"Error loading models: {e}")
            return False

def main():
    """Train models on existing data"""
    from database import DatabaseManager
    
    # Initialize
    db = DatabaseManager()
    pipeline = PeerReviewMLPipeline(db)
    
    # Get data
    df = db.get_reviews()
    
    if len(df) == 0:
        print("No data found. Run data_generator.py first.")
        return
    
    print(f"Training on {len(df)} reviews...")
    
    # Engineer features and train models
    features_df = pipeline.engineer_features(df)
    features_df = pipeline.train_models(features_df)
    
    # Save models
    pipeline.save_models()
    
    # Show sample insights
    employees = db.get_employees()[:3]
    print("\n=== Sample Employee Insights ===")
    for emp in employees:
        insights = pipeline.get_employee_insights(emp)
        print(f"\n{emp}:")
        print(f"  Avg Score: {insights['avg_score']:.2f}")
        print(f"  Collaboration Rate: {insights['collaboration_rate']:.1%}")
        print(f"  7-day Trend: {insights['score_trend_7d']:.3f}")
        print(f"  Anomaly: {insights['is_anomaly']}")

if __name__ == "__main__":
    main()
