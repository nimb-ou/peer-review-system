#!/bin/bash

# Peer Review System Setup Script
# Automates the complete setup process

set -e  # Exit on any error

echo "🚀 Peer Review System Setup"
echo "=========================="

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "🐍 Python version: $python_version"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run setup script
echo "⚙️ Running setup..."
python scripts/setup.py

# Make scripts executable
chmod +x scripts/*.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Run: streamlit run streamlit_app/app.py"
echo "2. Open: http://localhost:8501"
echo ""
echo "📚 Or check the README.md for more options"
