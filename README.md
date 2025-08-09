# Peer Review System 👥

A lightweight, AI-powered peer review system for tracking daily team dynamics and generating actionable insights.

## 🎯 Overview

This system enables teams to:
- Submit daily psychometric-style peer reviews (1-minute per person)
- Track behavioral trends and performance patterns
- Generate ML-powered insights and anomaly detection
- Receive LLM-generated recommendations for managers and peers
- Visualize team dynamics through interactive dashboards

## 🚀 Quick Start

### Prerequisites

- **macOS with Apple Silicon (M1/M2/M4)** - Optimized for your MacBook Air M4
- **Python 3.11+**
- **Git**

### 1. Setup Environment

```bash
# Install miniforge (recommended for Apple Silicon)
# Download from: https://github.com/conda-forge/miniforge

# Create and activate environment
conda create -n peerrev python=3.11
conda activate peerrev

# Clone and setup project
git clone <your-repo-url>
cd peer-review-system
pip install -r requirements.txt
```

### 2. Generate Initial Data

```bash
# Generate 60 days of synthetic review data for 20 employees
python src/data_generator.py
```

### 3. Train ML Models

```bash
# Train behavioral prediction and anomaly detection models
python src/ml_pipeline.py
```

### 4. Run the Web App

```bash
# Start Streamlit application
streamlit run streamlit_app/app.py
```

The app will open at `http://localhost:8501`

## 📱 App Features

### 📝 Submit Review
- Daily 30-second peer feedback
- 4 behavioral descriptors: Collaborative, Neutral, Withdrawn, Blocking
- Optional 1-5 score and comments
- Duplicate prevention (one review per person per day)

### 📊 Dashboard
- Team performance overview
- Score trends and behavioral distribution
- Employee summary table with rankings
- Interactive visualizations

### 👤 Individual Analysis
- Personal performance metrics
- Anomaly detection alerts
- Score trends and behavior patterns
- AI-generated insights and recommendations

### 🔧 Admin Panel
- Database statistics
- Synthetic data generation
- Model training interface
- LLM configuration

## 🤖 AI Features

### Machine Learning Pipeline
- **Feature Engineering**: Rolling averages, trends, volatility metrics
- **Composite Scoring**: Weighted behavioral score (1-5 scale)
- **Anomaly Detection**: Isolation Forest for unusual patterns
- **Clustering**: Behavioral archetype identification
- **Trend Analysis**: 7-day and 14-day performance slopes

### LLM Integration
- **OpenAI GPT-3.5/4** or **Google Gemini** support
- Context-aware insight generation
- Manager and peer action recommendations
- Professional, growth-focused feedback
- Fallback to rule-based insights without API

## 📊 Data Model

### Reviews Table
```sql
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    reviewer_id TEXT,
    reviewee_id TEXT,
    date DATE,
    descriptor TEXT,  -- collaborative/neutral/withdrawn/blocking
    score INTEGER,    -- 1-5 scale
    comment TEXT,
    created_at TIMESTAMP
);
```

### Behavioral Descriptors
- **Collaborative** (4.0): Actively working with others, helpful, engaging
- **Neutral** (3.0): Standard engagement, meeting expectations
- **Withdrawn** (2.0): Less engaged than usual, quieter, distracted
- **Blocking** (1.0): Creating friction, obstacles, or conflicts

## 🔒 Privacy & Ethics

### Built-in Safeguards
- **Anonymous Option**: Can configure for anonymous reviews
- **Data Retention**: Clear retention policies (configurable)
- **Informed Consent**: Employees opt-in with clear data usage
- **No Punitive Use**: Designed for growth, not performance management
- **Local Data**: SQLite default (no cloud dependency)

### Recommendations
- Use for team development, not individual performance reviews
- Regular data audits and employee feedback
- Manager training on constructive use of insights
- Clear communication about data usage and benefits

## 🚀 Deployment Options

### Option 1: Streamlit Cloud (Easiest)
```bash
# Push to GitHub, then:
# 1. Connect GitHub repo to Streamlit Cloud
# 2. Deploy directly from GitHub
# 3. Free tier available
```

### Option 2: Local Network
```bash
# Run on local network
streamlit run streamlit_app/app.py --server.address 0.0.0.0
```

### Option 3: Cloud Platforms
- **Render**: Free tier, easy Python deployment
- **Railway**: Git-based deployment
- **Heroku**: Traditional PaaS option
- **HuggingFace Spaces**: Free ML-focused hosting

## 🛠️ Development

### Project Structure
```
peer-review-system/
├── src/                    # Core Python modules
│   ├── data_generator.py   # Synthetic data generation
│   ├── database.py         # SQLite database management
│   ├── ml_pipeline.py      # ML training and predictions
│   └── llm_integration.py  # LLM API integration
├── streamlit_app/          # Web application
│   └── app.py             # Main Streamlit app
├── data/                   # SQLite database and exports
├── models/                 # Trained ML models
├── scripts/               # Utility scripts
├── deployment/            # Deployment configurations
└── requirements.txt       # Python dependencies
```

### Adding New Features

1. **New Descriptors**: Modify `descriptor_scores` in `ml_pipeline.py`
2. **Additional Metrics**: Extend `engineer_features()` method
3. **Custom Models**: Add to `train_models()` in ML pipeline
4. **UI Changes**: Edit Streamlit pages in `app.py`

### Database Management
```python
from src.database import DatabaseManager

db = DatabaseManager()
db.add_review("emp_01", "emp_02", "2024-01-15", "collaborative", 4, "Great teamwork")
reviews = db.get_reviews(start_date="2024-01-01")
```

## 🔧 Configuration

### Environment Variables
```bash
# Optional LLM API keys
export OPENAI_API_KEY="your-openai-key"
export GEMINI_API_KEY="your-gemini-key"

# Database path (optional)
export DATABASE_PATH="custom/path/reviews.db"
```

### Model Configuration
- Adjust `n_employees` and `n_days` in data generator
- Modify ML model parameters in `ml_pipeline.py`
- Customize LLM prompts in `llm_integration.py`

## 📈 Sample Workflow

### Daily Use (2 minutes per person)
1. **Morning**: Submit reviews for yesterday's interactions
2. **Weekly**: Check individual dashboard for trends
3. **Monthly**: Review team dashboard and insights

### Manager Workflow
1. **Weekly**: Review team dashboard and anomalies
2. **Bi-weekly**: Check individual insights for team members
3. **Monthly**: Use LLM recommendations for 1-on-1s

## 🐛 Troubleshooting

### Common Issues

**"No data found"**
```bash
python src/data_generator.py  # Generate synthetic data
```

**"Models not trained"**
```bash
python src/ml_pipeline.py     # Train models
```

**"LLM insights not working"**
- Check API keys in Admin → Settings
- Verify internet connection
- Fallback insights still available

**Database errors**
- Delete `data/reviews.db` and regenerate
- Check file permissions

### Performance Optimization
- For large teams (50+), consider PostgreSQL
- Use API rate limiting for LLM calls
- Implement caching for dashboard queries

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Submit pull request with clear description

## 📄 License

MIT License - see LICENSE file for details

## 🙋‍♂️ Support

- **Issues**: GitHub Issues for bug reports
- **Features**: GitHub Discussions for feature requests
- **Security**: Email for security concerns

---

**Ready to transform your team dynamics?** 🚀

Start with synthetic data, customize for your team, and begin generating actionable insights in minutes!
