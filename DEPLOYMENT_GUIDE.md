# 🚀 PeerPulse - Deployment Guide

## 📦 Package Contents

This package contains a complete AI-powered peer review system with:

- ✅ **Enhanced Data Generator** with realistic employee profiles
- ✅ **Advanced ML Pipeline** with anomaly detection and team insights
- ✅ **Professional Streamlit UI** with role-based navigation
- ✅ **Network Analysis** and team collaboration mapping
- ✅ **LLM Integration** for AI-powered recommendations
- ✅ **Complete Documentation** and setup scripts

## 🎯 Quick Start (Any System)

### Option 1: One-Command Setup
```bash
# Extract and setup
tar -xzf peer-review-system-v2.0.tar.gz
cd peer-review-system
./scripts/run_setup.sh
```

### Option 2: Manual Setup
```bash
# Extract package
tar -xzf peer-review-system-v2.0.tar.gz
cd peer-review-system

# Install dependencies
pip install -r requirements.txt

# Initialize system
python scripts/setup.py

# Run enhanced app
streamlit run streamlit_app/enhanced_app.py
```

## 🐳 Docker Deployment

### Quick Docker Run
```bash
cd peer-review-system
docker-compose up
```

### Manual Docker Build
```bash
docker build -f deployment/Dockerfile -t peerpulse .
docker run -p 8501:8501 peerpulse
```

## ☁️ Cloud Deployment Options

### 1. Streamlit Community Cloud (Free)
1. Upload to GitHub repository
2. Connect at [share.streamlit.io](https://share.streamlit.io)
3. Deploy with one click

### 2. Render (Free Tier)
1. Upload to GitHub
2. Connect to Render
3. Auto-deploy from main branch

### 3. Railway (Free Tier)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway link
railway up
```

### 4. Heroku
```bash
# Install Heroku CLI, then:
heroku create your-app-name
git push heroku main
```

## 🖥️ Local Network Deployment

### Run on Local Network
```bash
streamlit run streamlit_app/enhanced_app.py --server.address 0.0.0.0 --server.port 8501
```
Access from any device on your network at: `http://[YOUR-IP]:8501`

### Find Your IP
```bash
# macOS/Linux
ifconfig | grep "inet "

# Windows
ipconfig
```

## ⚙️ Configuration Options

### Environment Variables
```bash
# LLM API Keys (optional)
export OPENAI_API_KEY="your-openai-key"
export GEMINI_API_KEY="your-gemini-key"

# Database path (optional)
export DATABASE_PATH="custom/path/reviews.db"
```

### Custom Configuration
Edit these files for customization:
- `src/enhanced_data_generator.py` - Employee profiles and departments
- `src/ml_pipeline.py` - ML model parameters
- `streamlit_app/enhanced_app.py` - UI customization

## 📊 Data Management

### Generate New Sample Data
```bash
python src/enhanced_data_generator.py
```

### Export Data
```bash
python -c "
from src.database import DatabaseManager
db = DatabaseManager()
db.export_to_csv('backup.csv')
"
```

### Reset System
```bash
rm data/reviews.db models/*.pkl
python scripts/setup.py
```

## 🔒 Security & Privacy

### Production Recommendations
1. **Database**: Use PostgreSQL instead of SQLite
2. **Authentication**: Add user login system
3. **HTTPS**: Use reverse proxy (nginx) with SSL
4. **Data**: Enable encryption at rest
5. **API Keys**: Use environment variables, not code

### Privacy Controls
- Anonymous review options available in UI
- Data retention settings in admin panel
- Employee data can be pseudonymized

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
streamlit run streamlit_app/enhanced_app.py --server.port 8502
```

**Missing dependencies:**
```bash
pip install -r requirements.txt
```

**No data found:**
```bash
python src/enhanced_data_generator.py
python src/ml_pipeline.py
```

**Models not trained:**
```bash
python src/ml_pipeline.py
```

**Database errors:**
```bash
rm data/reviews.db
python scripts/setup.py
```

### Performance Optimization

**For Large Teams (50+ employees):**
```python
# Edit src/enhanced_data_generator.py
generator = EnhancedDataGenerator(n_employees=100, n_days=180)
```

**For Better Performance:**
- Use PostgreSQL database
- Add Redis caching
- Deploy on dedicated server

## 📱 Mobile Access

The web app is mobile-responsive and works on:
- 📱 iOS Safari
- 🤖 Android Chrome
- 💻 Desktop browsers
- 📱 iPad/tablets

## 📈 Scaling Guide

### Small Team (5-25 people)
- ✅ SQLite database (included)
- ✅ Single server deployment
- ✅ Basic features

### Medium Team (25-100 people)
- 🔄 PostgreSQL database
- 🔄 Load balancer
- 🔄 Background job queue

### Large Organization (100+ people)
- 🔄 Microservices architecture
- 🔄 Kubernetes deployment
- 🔄 Data warehouse integration

## 🆘 Support

### Self-Help
1. Check this deployment guide
2. Review `README.md` for detailed documentation
3. Check `scripts/setup.py` for initialization

### Issue Resolution
1. Check terminal output for error messages
2. Verify all dependencies are installed
3. Ensure correct Python version (3.11+)
4. Try resetting the database

## 📦 Package Information

**Version:** 2.0  
**Size:** ~50MB (including sample data)  
**Requirements:** Python 3.11+, 2GB RAM, 1GB disk  
**License:** MIT  

## 🎉 Ready to Deploy!

Your peer review system is production-ready with:
- 25 realistic employees across 6 departments
- 8,964 sample reviews with behavioral patterns
- Trained ML models for insights and predictions
- Professional UI with role-based access
- Advanced analytics and team health monitoring

**Choose your deployment method above and get started in minutes!** 🚀
