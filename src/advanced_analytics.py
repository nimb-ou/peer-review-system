"""
Advanced Analytics for Peer Review System V2
Team-level insights, network analysis, and advanced ML features
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import networkx as nx
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class AdvancedAnalytics:
    def __init__(self, db_manager):
        """
        Initialize advanced analytics
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager
    
    def analyze_team_network(self, days=30):
        """
        Analyze team collaboration network
        
        Returns:
            dict: Network metrics and insights
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        reviews_df = self.db_manager.get_reviews(start_date, end_date)
        
        if reviews_df.empty:
            return {"error": "No data available for network analysis"}
        
        # Create collaboration network
        G = nx.DiGraph()
        
        # Add edges based on reviews (weighted by frequency and score)
        collaboration_data = reviews_df.groupby(['reviewer_id', 'reviewee_id']).agg({
            'score': ['mean', 'count'],
            'descriptor': lambda x: (x == 'collaborative').mean()
        }).reset_index()
        
        collaboration_data.columns = ['reviewer', 'reviewee', 'avg_score', 'review_count', 'collab_rate']
        
        for _, row in collaboration_data.iterrows():
            # Weight combines frequency, score, and collaboration rate
            weight = (row['review_count'] * row['avg_score'] * (1 + row['collab_rate'])) / 20
            G.add_edge(row['reviewer'], row['reviewee'], weight=weight)
        
        # Calculate network metrics
        try:
            # Centrality measures
            betweenness = nx.betweenness_centrality(G, weight='weight')
            closeness = nx.closeness_centrality(G, distance='weight')
            eigenvector = nx.eigenvector_centrality(G, weight='weight', max_iter=1000)
            
            # Identify key players
            network_insights = {
                'total_nodes': len(G.nodes()),
                'total_edges': len(G.edges()),
                'density': nx.density(G),
                'top_connectors': sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5],
                'most_central': sorted(closeness.items(), key=lambda x: x[1], reverse=True)[:5],
                'most_influential': sorted(eigenvector.items(), key=lambda x: x[1], reverse=True)[:5],
            }
            
            # Detect communities/cliques
            undirected_G = G.to_undirected()
            try:
                communities = list(nx.community.greedy_modularity_communities(undirected_G))
                network_insights['communities'] = [list(community) for community in communities]
            except:
                network_insights['communities'] = []
            
            return network_insights
            
        except Exception as e:
            return {"error": f"Network analysis failed: {str(e)}"}
    
    def detect_team_dynamics(self, days=30):
        """
        Detect team-level behavioral patterns and dynamics
        
        Returns:
            dict: Team dynamics insights
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        reviews_df = self.db_manager.get_reviews(start_date, end_date)
        
        if reviews_df.empty:
            return {"error": "No data available for team dynamics analysis"}
        
        # Daily team metrics
        daily_metrics = reviews_df.groupby('date').agg({
            'score': ['mean', 'std'],
            'descriptor': [
                lambda x: (x == 'collaborative').mean(),
                lambda x: (x == 'withdrawn').mean(),
                lambda x: (x == 'blocking').mean()
            ]
        }).reset_index()
        
        daily_metrics.columns = ['date', 'avg_score', 'score_variance', 'collab_rate', 'withdrawn_rate', 'blocking_rate']
        
        # Trend analysis
        days_numeric = np.arange(len(daily_metrics))
        
        score_trend = stats.linregress(days_numeric, daily_metrics['avg_score']).slope
        collab_trend = stats.linregress(days_numeric, daily_metrics['collab_rate']).slope
        variance_trend = stats.linregress(days_numeric, daily_metrics['score_variance']).slope
        
        # Detect significant events (outliers)
        z_scores = np.abs(stats.zscore(daily_metrics['avg_score']))
        outlier_dates = daily_metrics[z_scores > 2]['date'].tolist()
        
        # Team cohesion metric (inverse of score variance)
        avg_cohesion = 1 / (daily_metrics['score_variance'].mean() + 0.1)
        
        # Communication patterns
        review_frequency = len(reviews_df) / len(reviews_df['date'].unique())
        
        dynamics = {
            'score_trend': score_trend,
            'collaboration_trend': collab_trend,
            'team_cohesion': avg_cohesion,
            'variance_trend': variance_trend,
            'review_frequency': review_frequency,
            'outlier_dates': [str(date) for date in outlier_dates],
            'team_health_score': self._calculate_team_health(daily_metrics)
        }
        
        return dynamics
    
    def _calculate_team_health(self, daily_metrics):
        """Calculate overall team health score (0-100)"""
        # Components of team health
        avg_score = daily_metrics['avg_score'].mean()
        collab_rate = daily_metrics['collab_rate'].mean()
        consistency = 1 / (daily_metrics['score_variance'].mean() + 0.1)
        low_blocking = 1 - daily_metrics['blocking_rate'].mean()
        
        # Weighted combination
        health_score = (
            (avg_score / 5) * 0.3 +  # 30% performance
            collab_rate * 0.3 +       # 30% collaboration
            (consistency / 5) * 0.2 + # 20% consistency
            low_blocking * 0.2        # 20% low conflict
        ) * 100
        
        return min(100, max(0, health_score))
    
    def identify_at_risk_employees(self, days=14):
        """
        Identify employees who may need support
        
        Returns:
            list: Employees with risk factors
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        reviews_df = self.db_manager.get_reviews(start_date, end_date)
        employees = self.db_manager.get_employees()
        
        at_risk = []
        
        for emp in employees:
            emp_reviews = reviews_df[reviews_df['reviewee_id'] == emp]
            
            if emp_reviews.empty:
                at_risk.append({
                    'employee_id': emp,
                    'risk_factors': ['No recent reviews'],
                    'risk_level': 'medium'
                })
                continue
            
            risk_factors = []
            risk_level = 'low'
            
            # Low scores
            avg_score = emp_reviews['score'].mean()
            if avg_score < 2.5:
                risk_factors.append(f'Low average score ({avg_score:.1f})')
                risk_level = 'high'
            
            # High withdrawn rate
            withdrawn_rate = (emp_reviews['descriptor'] == 'withdrawn').mean()
            if withdrawn_rate > 0.4:
                risk_factors.append(f'High withdrawn behavior ({withdrawn_rate:.1%})')
                risk_level = 'high' if risk_level != 'high' else 'high'
            
            # Declining trend
            if len(emp_reviews) >= 5:
                recent_scores = emp_reviews.sort_values('date')['score'].tail(5)
                if len(recent_scores) >= 3:
                    trend = stats.linregress(range(len(recent_scores)), recent_scores).slope
                    if trend < -0.3:
                        risk_factors.append(f'Declining performance trend')
                        risk_level = 'medium' if risk_level == 'low' else risk_level
            
            # High blocking rate
            blocking_rate = (emp_reviews['descriptor'] == 'blocking').mean()
            if blocking_rate > 0.2:
                risk_factors.append(f'High blocking behavior ({blocking_rate:.1%})')
                risk_level = 'medium' if risk_level == 'low' else risk_level
            
            # Isolation (few reviews)
            if len(emp_reviews) < len(employees) * 0.3:  # Less than 30% of possible reviews
                risk_factors.append('Limited peer interaction')
                risk_level = 'medium' if risk_level == 'low' else risk_level
            
            if risk_factors:
                at_risk.append({
                    'employee_id': emp,
                    'risk_factors': risk_factors,
                    'risk_level': risk_level,
                    'avg_score': avg_score,
                    'review_count': len(emp_reviews)
                })
        
        # Sort by risk level
        risk_order = {'high': 3, 'medium': 2, 'low': 1}
        at_risk.sort(key=lambda x: risk_order.get(x['risk_level'], 0), reverse=True)
        
        return at_risk
    
    def generate_team_recommendations(self, days=30):
        """
        Generate actionable recommendations for team improvement
        
        Returns:
            dict: Categorized recommendations
        """
        # Get various analyses
        network_analysis = self.analyze_team_network(days)
        team_dynamics = self.detect_team_dynamics(days)
        at_risk = self.identify_at_risk_employees(14)
        
        recommendations = {
            'immediate_actions': [],
            'process_improvements': [],
            'long_term_strategies': []
        }
        
        # Network-based recommendations
        if 'top_connectors' in network_analysis:
            top_connector = network_analysis['top_connectors'][0][0] if network_analysis['top_connectors'] else None
            if top_connector:
                recommendations['process_improvements'].append(
                    f"Leverage {top_connector} as a team connector for knowledge sharing"
                )
        
        if network_analysis.get('density', 0) < 0.3:
            recommendations['long_term_strategies'].append(
                "Increase cross-team collaboration through structured pairing or rotation"
            )
        
        # Team dynamics recommendations
        if team_dynamics.get('collaboration_trend', 0) < 0:
            recommendations['immediate_actions'].append(
                "Address declining collaboration - consider team building activities"
            )
        
        team_health = team_dynamics.get('team_health_score', 50)
        if team_health < 60:
            recommendations['immediate_actions'].append(
                f"Team health score is low ({team_health:.0f}/100) - needs management attention"
            )
        
        if team_dynamics.get('variance_trend', 0) > 0.05:
            recommendations['process_improvements'].append(
                "Increasing score variance suggests inconsistent performance - standardize processes"
            )
        
        # At-risk employee recommendations
        high_risk_count = len([emp for emp in at_risk if emp['risk_level'] == 'high'])
        if high_risk_count > 0:
            recommendations['immediate_actions'].append(
                f"{high_risk_count} employees need immediate support and intervention"
            )
        
        medium_risk_count = len([emp for emp in at_risk if emp['risk_level'] == 'medium'])
        if medium_risk_count > 2:
            recommendations['process_improvements'].append(
                f"{medium_risk_count} employees showing early warning signs - implement check-ins"
            )
        
        # General recommendations based on patterns
        if len(recommendations['immediate_actions']) == 0:
            recommendations['immediate_actions'].append("Team is performing well - maintain current practices")
        
        return recommendations
    
    def calculate_roi_metrics(self, days=30):
        """
        Calculate ROI and impact metrics for the peer review system
        
        Returns:
            dict: ROI and impact metrics
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        reviews_df = self.db_manager.get_reviews(start_date, end_date)
        total_employees = len(self.db_manager.get_employees())
        
        if reviews_df.empty:
            return {"error": "No data for ROI calculation"}
        
        # Engagement metrics
        active_reviewers = len(reviews_df['reviewer_id'].unique())
        active_reviewees = len(reviews_df['reviewee_id'].unique())
        engagement_rate = active_reviewers / total_employees
        
        # Time investment
        avg_reviews_per_person = len(reviews_df) / active_reviewers if active_reviewers > 0 else 0
        estimated_time_per_review = 0.5  # 30 seconds
        total_time_hours = len(reviews_df) * estimated_time_per_review / 60
        
        # Quality metrics
        avg_score = reviews_df['score'].mean()
        score_improvement = self._calculate_score_improvement(reviews_df)
        
        # Collaboration impact
        collab_rate = (reviews_df['descriptor'] == 'collaborative').mean()
        
        roi_metrics = {
            'engagement_rate': engagement_rate,
            'total_reviews': len(reviews_df),
            'time_investment_hours': total_time_hours,
            'avg_score': avg_score,
            'score_improvement': score_improvement,
            'collaboration_rate': collab_rate,
            'cost_per_review': 0.25,  # Estimated cost (time * hourly rate)
            'estimated_productivity_gain': collab_rate * 0.15  # 15% productivity boost from collaboration
        }
        
        return roi_metrics
    
    def _calculate_score_improvement(self, reviews_df):
        """Calculate score improvement over time"""
        if len(reviews_df) < 10:
            return 0
        
        reviews_df = reviews_df.sort_values('date')
        mid_point = len(reviews_df) // 2
        
        first_half_avg = reviews_df.iloc[:mid_point]['score'].mean()
        second_half_avg = reviews_df.iloc[mid_point:]['score'].mean()
        
        return second_half_avg - first_half_avg

def main():
    """Test advanced analytics"""
    from database import DatabaseManager
    
    db = DatabaseManager()
    analytics = AdvancedAnalytics(db)
    
    print("🔬 Advanced Analytics Test")
    print("=" * 40)
    
    # Test network analysis
    print("\n📊 Network Analysis:")
    network = analytics.analyze_team_network(30)
    if 'error' not in network:
        print(f"Network density: {network['density']:.3f}")
        print(f"Top connector: {network['top_connectors'][0][0] if network['top_connectors'] else 'None'}")
    
    # Test team dynamics
    print("\n🎭 Team Dynamics:")
    dynamics = analytics.detect_team_dynamics(30)
    if 'error' not in dynamics:
        print(f"Team health score: {dynamics['team_health_score']:.1f}/100")
        print(f"Collaboration trend: {dynamics['collaboration_trend']:.3f}")
    
    # Test at-risk detection
    print("\n⚠️ At-Risk Employees:")
    at_risk = analytics.identify_at_risk_employees(14)
    print(f"Found {len(at_risk)} employees with risk factors")
    for emp in at_risk[:3]:
        print(f"  {emp['employee_id']}: {emp['risk_level']} risk - {emp['risk_factors']}")

if __name__ == "__main__":
    main()
