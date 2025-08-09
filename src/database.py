"""
Database setup and management for Peer Review System
Handles SQLite schema creation, migrations, and basic operations
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, date

class DatabaseManager:
    def __init__(self, db_path="data/reviews.db"):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create reviews table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reviewer_id TEXT NOT NULL,
                reviewee_id TEXT NOT NULL,
                date DATE NOT NULL,
                descriptor TEXT NOT NULL,
                score INTEGER CHECK (score >= 1 AND score <= 5),
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(reviewer_id, reviewee_id, date)
            )
        """)
        
        # Create employees table (for metadata)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                name TEXT,
                department TEXT,
                role TEXT,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_date ON reviews(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_reviewee ON reviews(reviewee_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_reviewer ON reviews(reviewer_id)")
        
        conn.commit()
        conn.close()
        print(f"Database initialized at {self.db_path}")
    
    def add_review(self, reviewer_id: str, reviewee_id: str, review_date: date, 
                   descriptor: str, score: int, comment: str = "") -> bool:
        """
        Add a new review to the database
        
        Returns:
            bool: True if successful, False if duplicate or error
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO reviews 
                (reviewer_id, reviewee_id, date, descriptor, score, comment)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (reviewer_id, reviewee_id, review_date, descriptor, score, comment))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error adding review: {e}")
            return False
    
    def get_reviews(self, start_date: Optional[date] = None, 
                   end_date: Optional[date] = None,
                   reviewee_id: Optional[str] = None) -> pd.DataFrame:
        """
        Get reviews with optional filtering
        
        Args:
            start_date: Filter reviews after this date
            end_date: Filter reviews before this date
            reviewee_id: Filter reviews for specific reviewee
            
        Returns:
            DataFrame with review data
        """
        conn = self.get_connection()
        
        query = "SELECT * FROM reviews WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        if reviewee_id:
            query += " AND reviewee_id = ?"
            params.append(reviewee_id)
        
        query += " ORDER BY date DESC, reviewee_id"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        return df
    
    def get_employees(self) -> List[str]:
        """Get list of all unique employee IDs"""
        conn = self.get_connection()
        
        # Try employees table first, fall back to reviews table
        try:
            df = pd.read_sql_query("SELECT id FROM employees WHERE active = 1", conn)
            if len(df) > 0:
                employees = df['id'].tolist()
            else:
                raise Exception("No employees in employees table")
        except:
            # Fall back to getting unique IDs from reviews
            df = pd.read_sql_query("""
                SELECT DISTINCT reviewee_id as id FROM reviews
                UNION
                SELECT DISTINCT reviewer_id as id FROM reviews
            """, conn)
            employees = sorted(df['id'].tolist())
        
        conn.close()
        return employees
    
    def add_employee(self, employee_id: str, name: str = "", 
                    department: str = "", role: str = "") -> bool:
        """Add employee to employees table"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO employees (id, name, department, role)
                VALUES (?, ?, ?, ?)
            """, (employee_id, name, department, role))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error adding employee: {e}")
            return False
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics about the database"""
        conn = self.get_connection()
        
        stats = {}
        
        # Total reviews
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM reviews")
        stats['total_reviews'] = cursor.fetchone()[0]
        
        # Date range
        cursor.execute("SELECT MIN(date), MAX(date) FROM reviews")
        date_range = cursor.fetchone()
        stats['date_range'] = date_range
        
        # Unique employees
        cursor.execute("""
            SELECT COUNT(DISTINCT reviewee_id) FROM reviews
        """)
        stats['unique_employees'] = cursor.fetchone()[0]
        
        # Average reviews per day
        cursor.execute("""
            SELECT COUNT(DISTINCT date) FROM reviews
        """)
        unique_days = cursor.fetchone()[0]
        if unique_days > 0:
            stats['avg_reviews_per_day'] = stats['total_reviews'] / unique_days
        else:
            stats['avg_reviews_per_day'] = 0
        
        conn.close()
        return stats
    
    def export_to_csv(self, filename: str = None) -> str:
        """Export all reviews to CSV"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reviews_export_{timestamp}.csv"
        
        df = self.get_reviews()
        filepath = self.db_path.parent / filename
        df.to_csv(filepath, index=False)
        print(f"Exported {len(df)} reviews to {filepath}")
        return str(filepath)

def main():
    """Initialize database and print summary"""
    db = DatabaseManager()
    stats = db.get_summary_stats()
    employees = db.get_employees()
    
    print("=== Database Summary ===")
    print(f"Total reviews: {stats['total_reviews']}")
    print(f"Date range: {stats['date_range'][0]} to {stats['date_range'][1]}")
    print(f"Unique employees: {stats['unique_employees']}")
    print(f"Average reviews per day: {stats['avg_reviews_per_day']:.1f}")
    print(f"Employees: {employees[:5]}..." if len(employees) > 5 else f"Employees: {employees}")

if __name__ == "__main__":
    main()
