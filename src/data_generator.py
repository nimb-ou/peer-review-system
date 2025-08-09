"""
Synthetic Data Generator for Peer Review System
Generates realistic employee review data with patterns and trends
"""

import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
import random
from pathlib import Path

class SyntheticDataGenerator:
    def __init__(self, n_employees=20, n_days=60, seed=42):
        """
        Initialize synthetic data generator
        
        Args:
            n_employees: Number of employees to simulate
            n_days: Number of days of historical data
            seed: Random seed for reproducibility
        """
        np.random.seed(seed)
        random.seed(seed)
        
        self.n_employees = n_employees
        self.n_days = n_days
        self.employees = [f"emp_{i:02d}" for i in range(1, n_employees + 1)]
        
        # Psychometric descriptors with base probabilities
        self.descriptors = {
            'collaborative': 0.4,
            'withdrawn': 0.15,
            'neutral': 0.35,
            'blocking': 0.1
        }
        
        # Employee personality profiles (affects descriptor probabilities)
        self.employee_profiles = self._generate_employee_profiles()
        
    def _generate_employee_profiles(self):
        """Generate base personality profiles for each employee"""
        profiles = {}
        for emp in self.employees:
            # Each employee has different base tendencies
            collaborative_bias = np.random.beta(2, 2)  # 0 to 1
            withdrawn_bias = np.random.beta(1.5, 3)    # skewed toward lower
            blocking_bias = np.random.beta(1, 4)       # very skewed toward lower
            
            profiles[emp] = {
                'collaborative_bias': collaborative_bias,
                'withdrawn_bias': withdrawn_bias,
                'blocking_bias': blocking_bias,
                'stability': np.random.uniform(0.7, 0.95),  # how consistent they are
                'trend_direction': np.random.choice([-1, 0, 1], p=[0.2, 0.6, 0.2])  # declining, stable, improving
            }
        return profiles
    
    def _get_descriptor_probabilities(self, employee, day_idx):
        """Get descriptor probabilities for an employee on a given day"""
        profile = self.employee_profiles[employee]
        
        # Add time-based trends
        trend_factor = profile['trend_direction'] * (day_idx / self.n_days) * 0.3
        
        # Add some noise and stability
        noise = np.random.normal(0, 1 - profile['stability']) * 0.1
        
        # Calculate probabilities
        collab_prob = np.clip(profile['collaborative_bias'] + trend_factor + noise, 0.1, 0.8)
        withdrawn_prob = np.clip(profile['withdrawn_bias'] - trend_factor/2 + noise, 0.05, 0.4)
        blocking_prob = np.clip(profile['blocking_bias'] - trend_factor/3 + noise, 0.02, 0.3)
        neutral_prob = max(0.1, 1 - collab_prob - withdrawn_prob - blocking_prob)
        
        # Normalize to ensure sum = 1 and all probabilities are positive
        total = collab_prob + withdrawn_prob + blocking_prob + neutral_prob
        return {
            'collaborative': collab_prob / total,
            'withdrawn': withdrawn_prob / total,
            'neutral': neutral_prob / total,
            'blocking': blocking_prob / total
        }
    
    def _generate_score(self, descriptor, base_noise=0.5):
        """Generate a 1-5 score based on descriptor"""
        score_mapping = {
            'collaborative': 4.2,
            'neutral': 3.5,
            'withdrawn': 2.8,
            'blocking': 2.1
        }
        
        base_score = score_mapping[descriptor]
        noise = np.random.normal(0, base_noise)
        score = base_score + noise
        
        return int(np.clip(score, 1, 5))
    
    def generate_data(self):
        """Generate synthetic review data"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.n_days - 1)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        rows = []
        
        for day_idx, date in enumerate(dates):
            for reviewer in self.employees:
                for reviewee in self.employees:
                    if reviewer == reviewee:
                        continue
                    
                    # Skip some reviews randomly (not everyone reviews everyone every day)
                    if np.random.random() < 0.15:  # 15% chance to skip
                        continue
                    
                    # Get probabilities for this reviewee on this day
                    probs = self._get_descriptor_probabilities(reviewee, day_idx)
                    
                    # Choose descriptor based on probabilities
                    descriptor = np.random.choice(
                        list(probs.keys()),
                        p=list(probs.values())
                    )
                    
                    # Generate score
                    score = self._generate_score(descriptor)
                    
                    # Generate optional comment (10% chance)
                    comment = ""
                    if np.random.random() < 0.1:
                        comments = [
                            "Great collaboration today",
                            "Seemed stressed",
                            "Very helpful in meetings",
                            "Could be more engaged",
                            "Leading by example",
                            "Communication could improve"
                        ]
                        comment = np.random.choice(comments)
                    
                    rows.append({
                        'reviewer_id': reviewer,
                        'reviewee_id': reviewee,
                        'date': date.date(),
                        'descriptor': descriptor,
                        'score': score,
                        'comment': comment
                    })
        
        return pd.DataFrame(rows)
    
    def save_to_csv(self, filename="synthetic_reviews.csv"):
        """Generate and save data to CSV"""
        df = self.generate_data()
        filepath = Path("data") / filename
        filepath.parent.mkdir(exist_ok=True)
        df.to_csv(filepath, index=False)
        print(f"Generated {len(df)} reviews and saved to {filepath}")
        return df
    
    def save_to_sqlite(self, db_path="data/reviews.db"):
        """Generate and save data to SQLite database"""
        df = self.generate_data()
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(exist_ok=True)
        
        # Save to SQLite
        conn = sqlite3.connect(db_path)
        df.to_sql('reviews', conn, if_exists='replace', index=False)
        conn.close()
        
        print(f"Generated {len(df)} reviews and saved to {db_path}")
        return df

def main():
    """Generate synthetic data and save to both CSV and SQLite"""
    generator = SyntheticDataGenerator(n_employees=20, n_days=60)
    
    # Generate and save data
    print("Generating synthetic peer review data...")
    df_csv = generator.save_to_csv()
    df_sqlite = generator.save_to_sqlite()
    
    # Print summary statistics
    print("\n=== Data Summary ===")
    print(f"Total reviews: {len(df_csv)}")
    print(f"Date range: {df_csv['date'].min()} to {df_csv['date'].max()}")
    print(f"Employees: {len(df_csv['reviewee_id'].unique())}")
    print("\nDescriptor distribution:")
    print(df_csv['descriptor'].value_counts())
    print("\nScore distribution:")
    print(df_csv['score'].value_counts().sort_index())

if __name__ == "__main__":
    main()
