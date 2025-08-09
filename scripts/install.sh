#!/bin/bash

# PeerPulse Installation Script
# Automated setup for any Unix-like system

set -e

echo "🚀 PeerPulse Installation Starting..."
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Check Python version
echo -e "${BLUE}🐍 Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python version: $python_version"

if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
    echo -e "${RED}❌ Python 3.8+ required. Current version: $python_version${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}⬆️ Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${BLUE}📥 Installing dependencies...${NC}"
pip install -r requirements.txt

# Create necessary directories
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p data models logs

# Generate sample data
echo -e "${BLUE}📊 Generating sample data...${NC}"
python src/enhanced_data_generator.py

# Train ML models
echo -e "${BLUE}🤖 Training ML models...${NC}"
python src/ml_pipeline.py

# Make scripts executable
chmod +x scripts/*.sh

echo ""
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "=========================="
echo ""
echo -e "${YELLOW}🚀 Next steps:${NC}"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the application: streamlit run streamlit_app/enhanced_app.py"
echo "3. Open browser to: http://localhost:8501"
echo ""
echo -e "${YELLOW}📚 Documentation:${NC}"
echo "- README.md: Complete documentation"
echo "- DEPLOYMENT_GUIDE.md: Deployment options"
echo ""
echo -e "${YELLOW}🎯 Quick start command:${NC}"
echo -e "${BLUE}source venv/bin/activate && streamlit run streamlit_app/enhanced_app.py${NC}"
echo ""
echo -e "${GREEN}🎉 Welcome to PeerPulse!${NC}"
