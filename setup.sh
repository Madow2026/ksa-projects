#!/bin/bash
# Setup script for Saudi Projects Intelligence Platform (Linux/Mac)

echo "====================================="
echo "Saudi Projects Intelligence Platform"
echo "Setup Script for Linux/Mac"
echo "====================================="
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

echo "[1/5] Python found: $(python3 --version)"
echo ""

# Create virtual environment
echo "[2/5] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    echo "Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "[3/5] Activating virtual environment..."
source venv/bin/activate
echo ""

# Install dependencies
echo "[4/5] Installing dependencies (this may take a few minutes)..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi
echo "Dependencies installed successfully"
echo ""

# Setup environment file
echo "[5/5] Setting up environment..."
if [ -f ".env" ]; then
    echo ".env file already exists, skipping..."
else
    cp .env.example .env
    echo ".env file created from template"
    echo "Please edit .env and add your OpenAI API key if available"
fi
echo ""

echo "====================================="
echo "Setup Complete!"
echo "====================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your OpenAI API key (optional)"
echo "2. Generate demo data: python main.py demo"
echo "3. Launch dashboard: python main.py web"
echo ""
echo "Or run: streamlit run app.py"
echo ""
