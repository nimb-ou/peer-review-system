"""
Enhanced Synthetic Data Generator for Peer Review System V2
Creates more realistic employee review patterns with proper names and departments
"""

import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
import random
from pathlib import Path

class EnhancedDataGenerator:
    def __init__(self, n_employees=25, n_days=90, seed=42):
        """
        Enhanced data generator with realistic patterns
        
        Args:
            n_employees: Number of employees (realistic team size)
            n_days: Number of days of historical data
            seed: Random seed for reproducibility
        """
        np.random.seed(seed)
        random.seed(seed)
        
        self.n_employees = n_employees
        self.n_days = n_days
        
        # More realistic descriptors with better distribution
        self.descriptors = {
            'collaborative': 0.25,    # Reduced from 38%
            'neutral': 0.45,          # Most common state
            'withdrawn': 0.20,        # Moderate
            'blocking': 0.10          # Uncommon but important
        }
        
        # Generate realistic employee profiles
        self.employees = self._generate_realistic_employees()
        self.employee_profiles = self._generate_employee_profiles()
        
    def _generate_realistic_employees(self):
        """Generate realistic employee data with names and departments"""
        first_names = [
            'Alex', 'Morgan', 'Jordan', 'Taylor', 'Casey', 'Riley', 'Avery', 'Quinn',
            'Blake', 'Sage', 'River', 'Dakota', 'Rowan', 'Phoenix', 'Skyler', 'Cameron',
            'Drew', 'Emery', 'Finley', 'Harley', 'Jamie', 'Kendall', 'Logan', 'Peyton',
            'Reese', 'Sidney', 'Tatum', 'Val', 'Winter', 'Zion'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
            'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
            'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
            'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson'
        ]
        
        departments = ['Engineering', 'Product', 'Design', 'Marketing', 'Sales', 'Operations']
        roles = {
            'Engineering': ['Software Engineer', 'Senior Engineer', 'Tech Lead', 'Engineering Manager'],
            'Product': ['Product Manager', 'Senior PM', 'Product Owner', 'Product Director'],
            'Design': ['UX Designer', 'UI Designer', 'Design Lead', 'Product Designer'],
            'Marketing': ['Marketing Manager', 'Content Manager', 'Growth Manager', 'Marketing Director'],
            'Sales': ['Sales Rep', 'Account Manager', 'Sales Manager', 'Sales Director'],
            'Operations': ['Operations Manager', 'Business Analyst', 'Operations Lead', 'COO']
        }
        
        employees = []
        used_names = set()
        
        for i in range(self.n_employees):
            # Generate unique names
            while True:
                first = random.choice(first_names)
                last = random.choice(last_names)
                full_name = f"{first} {last}"
                if full_name not in used_names:
                    used_names.add(full_name)
                    break
            
            # Assign department and role
            dept = random.choice(departments)
            role = random.choice(roles[dept])
            
            employees.append({
                'id': f"emp_{i+1:02d}",
                'name': full_name,
                'first_name': first,
                'last_name': last,
                'department': dept,
                'role': role,
                'email': f"{first.lower()}.{last.lower()}@company.com"
            })
        
        return employees
    
    def _generate_employee_profiles(self):
        """Generate realistic personality profiles"""
        profiles = {}
        
        for emp in self.employees:
            emp_id = emp['id']
            dept = emp['department']
            
            # Department-based tendencies
            dept_modifiers = {
                'Engineering': {'collaborative': 0.3, 'withdrawn': 0.25, 'neutral': 0.4},
                'Product': {'collaborative': 0.35, 'withdrawn': 0.15, 'neutral': 0.45},
                'Design': {'collaborative': 0.4, 'withdrawn': 0.2, 'neutral': 0.35},
                'Marketing': {'collaborative': 0.45, 'withdrawn': 0.1, 'neutral': 0.4},
                'Sales': {'collaborative': 0.5, 'withdrawn': 0.05, 'neutral': 0.4},
                'Operations': {'collaborative': 0.35, 'withdrawn': 0.15, 'neutral': 0.45}
            }
            
            base_probs = dept_modifiers[dept]
            
            # Add individual variation
            collaborative_bias = np.clip(
                base_probs['collaborative'] + np.random.normal(0, 0.1), 0.1, 0.7
            )
            withdrawn_bias = np.clip(
                base_probs['withdrawn'] + np.random.normal(0, 0.08), 0.05, 0.4
            )
            
            # Performance level affects behavior patterns
            performance_level = np.random.choice(['high', 'medium', 'low'], p=[0.3, 0.5, 0.2])
            
            if performance_level == 'high':
                collaborative_bias *= 1.2
                withdrawn_bias *= 0.8
            elif performance_level == 'low':
                collaborative_bias *= 0.8
                withdrawn_bias *= 1.3
            
            profiles[emp_id] = {
                'collaborative_bias': collaborative_bias,
                'withdrawn_bias': withdrawn_bias,
                'blocking_bias': np.random.beta(1, 5) * 0.15,  # Most people rarely block
                'stability': np.random.uniform(0.75, 0.95),  # How consistent they are
                'trend_direction': np.random.choice([-1, 0, 1], p=[0.15, 0.7, 0.15]),
                'performance_level': performance_level,
                'department': dept,
                'seasonal_variation': np.random.uniform(0.05, 0.2)  # Stress/workload cycles
            }
        
        return profiles
    
    def _get_realistic_review_probability(self, reviewer, reviewee, day_idx):
        """Calculate probability of a review happening (more realistic)"""
        reviewer_dept = next(emp['department'] for emp in self.employees if emp['id'] == reviewer)
        reviewee_dept = next(emp['department'] for emp in self.employees if emp['id'] == reviewee)
        
        # Base probability - people don't review everyone every day
        base_prob = 0.15  # Much lower than 85% in v1
        
        # Same department increases probability
        if reviewer_dept == reviewee_dept:
            base_prob *= 2.5
        
        # Cross-department collaboration patterns
        collab_matrix = {
            ('Engineering', 'Product'): 1.8,
            ('Product', 'Design'): 2.0,
            ('Marketing', 'Sales'): 1.6,
            ('Operations', 'Engineering'): 1.4,
        }
        
        for (dept1, dept2), multiplier in collab_matrix.items():
            if (reviewer_dept, reviewee_dept) in [(dept1, dept2), (dept2, dept1)]:
                base_prob *= multiplier
                break
        
        # Day of week effects (less reviews on Fridays/Mondays)
        day_of_week = day_idx % 7
        if day_of_week in [0, 4]:  # Monday, Friday
            base_prob *= 0.7
        elif day_of_week in [2, 3]:  # Wednesday, Thursday
            base_prob *= 1.2
        
        # Recent interaction history (people review more after working together)
        # Simplified: add some randomness for interaction patterns
        if np.random.random() < 0.3:  # 30% chance of recent interaction
            base_prob *= 1.5
        
        return min(base_prob, 0.8)  # Cap at 80%
    
    def _get_descriptor_probabilities(self, employee_id, day_idx):
        """Enhanced descriptor probabilities with more realism"""
        profile = self.employee_profiles[employee_id]
        
        # Time-based trends (performance improvement/decline)
        trend_factor = profile['trend_direction'] * (day_idx / self.n_days) * 0.2
        
        # Seasonal variation (project deadlines, holidays, etc.)
        seasonal_factor = np.sin(2 * np.pi * day_idx / 30) * profile['seasonal_variation']
        
        # Weekly stress patterns (Monday stress, Friday relief)
        day_of_week = day_idx % 7
        weekly_stress = 0
        if day_of_week == 0:  # Monday
            weekly_stress = 0.1
        elif day_of_week == 4:  # Friday
            weekly_stress = -0.05
        
        # Individual noise
        noise = np.random.normal(0, 1 - profile['stability']) * 0.08
        
        # Calculate probabilities
        total_modifier = trend_factor + seasonal_factor + weekly_stress + noise
        
        collab_prob = np.clip(
            profile['collaborative_bias'] + total_modifier, 0.05, 0.6
        )
        withdrawn_prob = np.clip(
            profile['withdrawn_bias'] - total_modifier * 0.5, 0.02, 0.4
        )
        blocking_prob = np.clip(
            profile['blocking_bias'] + max(0, total_modifier * 0.3), 0.01, 0.2
        )
        
        # Ensure neutral gets reasonable share
        neutral_prob = max(0.2, 1 - collab_prob - withdrawn_prob - blocking_prob)
        
        # Normalize
        total = collab_prob + withdrawn_prob + blocking_prob + neutral_prob
        
        return {
            'collaborative': collab_prob / total,
            'withdrawn': withdrawn_prob / total,
            'neutral': neutral_prob / total,
            'blocking': blocking_prob / total
        }
    
    def _generate_realistic_score(self, descriptor, reviewer_id, reviewee_id):
        """Generate more realistic scores based on context"""
        base_scores = {
            'collaborative': np.random.normal(4.1, 0.7),
            'neutral': np.random.normal(3.2, 0.5),
            'withdrawn': np.random.normal(2.8, 0.6),
            'blocking': np.random.normal(2.1, 0.8)
        }
        
        score = base_scores[descriptor]
        
        # Reviewer bias (some people are harder/easier graders)
        reviewer_profile = self.employee_profiles[reviewer_id]
        reviewer_bias = np.random.normal(0, 0.3)  # Individual variation
        
        # Department differences (engineering might be more critical)
        dept = reviewer_profile['department']
        if dept == 'Engineering':
            reviewer_bias -= 0.2
        elif dept in ['Sales', 'Marketing']:
            reviewer_bias += 0.1
        
        score += reviewer_bias
        
        # Add realistic rounding (people prefer whole numbers)
        if np.random.random() < 0.7:  # 70% chance to round
            score = round(score)
        
        return int(np.clip(score, 1, 5))
    
    def _generate_realistic_comment(self, descriptor, score):
        """Generate contextual comments"""
        if np.random.random() < 0.85:  # 85% no comment (realistic)
            return ""
        
        comment_templates = {
            'collaborative': [
                "Great teamwork on the project",
                "Always willing to help others",
                "Led the standup really well",
                "Shared knowledge effectively",
                "Great pair programming session"
            ],
            'neutral': [
                "Standard day, nothing notable",
                "Completed assigned tasks",
                "Participated in meetings as expected",
                "On track with deliverables"
            ],
            'withdrawn': [
                "Seemed quiet in meetings",
                "Less engaged than usual",
                "Might be overwhelmed with workload",
                "Could use some support"
            ],
            'blocking': [
                "Disagreed without offering alternatives",
                "Delayed team decision making",
                "Needs to be more collaborative",
                "Communication could improve"
            ]
        }
        
        # Adjust comment probability based on score
        if score <= 2 or score >= 5:
            # Extreme scores more likely to have comments
            if np.random.random() < 0.6:
                return np.random.choice(comment_templates[descriptor])
        
        return np.random.choice(comment_templates[descriptor])
    
    def generate_realistic_data(self):
        """Generate enhanced realistic review data"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.n_days - 1)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        rows = []
        
        for day_idx, date in enumerate(dates):
            # Skip weekends (more realistic)
            if date.weekday() >= 5:
                continue
                
            for reviewer in [emp['id'] for emp in self.employees]:
                for reviewee in [emp['id'] for emp in self.employees]:
                    if reviewer == reviewee:
                        continue
                    
                    # Realistic review probability
                    review_prob = self._get_realistic_review_probability(
                        reviewer, reviewee, day_idx
                    )
                    
                    if np.random.random() > review_prob:
                        continue
                    
                    # Get realistic descriptor probabilities
                    probs = self._get_descriptor_probabilities(reviewee, day_idx)
                    
                    # Choose descriptor
                    descriptor = np.random.choice(
                        list(probs.keys()),
                        p=list(probs.values())
                    )
                    
                    # Generate realistic score
                    score = self._generate_realistic_score(descriptor, reviewer, reviewee)
                    
                    # Generate comment
                    comment = self._generate_realistic_comment(descriptor, score)
                    
                    rows.append({
                        'reviewer_id': reviewer,
                        'reviewee_id': reviewee,
                        'date': date.date(),
                        'descriptor': descriptor,
                        'score': score,
                        'comment': comment
                    })
        
        return pd.DataFrame(rows)
    
    def save_employee_data(self, db_path="data/reviews.db"):
        """Save employee information to database"""
        conn = sqlite3.connect(db_path)
        
        # Create employees dataframe
        employees_df = pd.DataFrame(self.employees)
        employees_df.to_sql('employees', conn, if_exists='replace', index=False)
        
        conn.close()
        print(f"Saved {len(self.employees)} employees to database")
    
    def save_enhanced_data(self, db_path="data/reviews.db"):
        """Generate and save enhanced data"""
        # Generate reviews
        df = self.generate_realistic_data()
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(exist_ok=True)
        
        # Save to SQLite
        conn = sqlite3.connect(db_path)
        
        # Save reviews
        df.to_sql('reviews', conn, if_exists='replace', index=False)
        
        # Save employee data
        employees_df = pd.DataFrame(self.employees)
        employees_df.to_sql('employees', conn, if_exists='replace', index=False)
        
        conn.close()
        
        print(f"Generated {len(df)} enhanced reviews for {len(self.employees)} employees")
        return df

def main():
    """Generate enhanced realistic data"""
    print("🚀 Generating Enhanced Peer Review Data V2...")
    
    generator = EnhancedDataGenerator(n_employees=25, n_days=90)
    
    # Generate and save enhanced data
    df = generator.save_enhanced_data()
    
    # Print enhanced statistics
    print("\n" + "="*50)
    print("📊 ENHANCED DATA SUMMARY")
    print("="*50)
    print(f"Total reviews: {len(df)}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Employees: {len(generator.employees)}")
    print(f"Average reviews per day: {len(df) / df['date'].nunique():.1f}")
    
    print("\n🎭 Descriptor distribution:")
    print(df['descriptor'].value_counts(normalize=True).round(3))
    
    print("\n⭐ Score distribution:")
    print(df['score'].value_counts().sort_index())
    
    print("\n🏢 Department distribution:")
    dept_counts = pd.Series([emp['department'] for emp in generator.employees]).value_counts()
    print(dept_counts)
    
    print("\n💬 Comment rate:")
    comment_rate = (df['comment'].str.len() > 0).mean()
    print(f"{comment_rate:.1%} of reviews have comments")
    
    print("\n✨ Sample employees:")
    for emp in generator.employees[:5]:
        print(f"  {emp['name']} ({emp['role']}, {emp['department']})")

if __name__ == "__main__":
    main()
