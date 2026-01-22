#!/bin/bash

# CFT Trend Radar Newsletter - Setup Script
# Automated setup for the newsletter system

set -e

echo "================================================"
echo "CFT Trend Radar Newsletter - Setup"
echo "================================================"
echo ""

# Check Python version
echo "[1/6] Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
echo ""
echo "[2/6] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "[3/6] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "[4/6] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env from example
echo ""
echo "[5/6] Setting up configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env file from template"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your credentials:"
    echo "   - ANTHROPIC_API_KEY or OPENAI_API_KEY"
    echo "   - SMTP credentials"
    echo "   - Email recipients"
else
    echo ".env file already exists"
fi

# Create data directory
echo ""
echo "[6/6] Creating data directory..."
mkdir -p data
echo "Data directory created"

# Final instructions
echo ""
echo "================================================"
echo "✓ Setup completed successfully!"
echo "================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env with your credentials:"
echo "   nano .env"
echo ""
echo "2. Test email configuration:"
echo "   python main.py test-email --test-recipient your_email@example.com"
echo ""
echo "3. Generate a preview:"
echo "   python main.py preview"
echo ""
echo "4. Send first newsletter:"
echo "   python main.py send"
echo ""
echo "5. Start automated scheduling:"
echo "   python main.py schedule"
echo ""
echo "For more details, see:"
echo "  - README.md (full documentation)"
echo "  - QUICK_START.md (quick guide)"
echo ""
