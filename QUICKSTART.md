# Quick Start Guide

## 🌐 Using Streamlit Cloud (Easiest!)

**No installation needed! Try it now:**

### ⚡ 2-Step Quick Start

1. **Open the app**: https://ksa-projects-2026.streamlit.app
2. **Click the blue button** in the left sidebar: `📊 Generate 15 Demo Projects`
3. ✅ Done! Explore the dashboard

### 🎯 What to Do After Generating Data

- **📊 Dashboard Tab**: View KPIs, charts, and recent projects
- **🔍 Smart Search**: Search by project name, owner, or contractor
- **🎨 Filters**: Filter by region, category, status (in sidebar)
- **📈 Analytics**: View distribution charts

### 🔍 Advanced: Live Web Scraping

Want real projects from Saudi websites?
- Click: `🔍 Run Live Scraper` in sidebar
- Watch projects appear in real-time
- **Note**: Takes 2-5 minutes (connects to actual websites)

💡 **Tip**: For instant results, always use demo data!

---

## 🚀 Get Started in 5 Minutes

### Step 1: Install Python
Make sure you have Python 3.9+ installed:
```bash
python --version
```

### Step 2: Clone & Setup
```bash
# Clone
git clone https://github.com/yourusername/saudi-projects-intelligence.git
cd saudi-projects-intelligence

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure (Optional)
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# nano .env  # or use any text editor
```

> **Note**: The platform works without OpenAI API key, but AI features will use rule-based extraction instead.

### Step 4: Generate Demo Data
```bash
python main.py demo
```

This creates 15 sample projects so you can explore the dashboard immediately.

### Step 5: Launch Dashboard
```bash
python main.py web
```

Or directly:
```bash
streamlit run app.py
```

### Step 6: Open Browser
Navigate to: `http://localhost:8501`

---

## 🎯 What to Do Next

### Explore the Dashboard
- View KPI metrics (total projects, regions, etc.)
- Use filters to find specific projects
- Search by keywords
- View charts and visualizations

### Run the Data Pipeline
1. Click "▶️ Run Pipeline" in the sidebar
2. Wait for scraping and AI processing
3. View results in the dashboard

### Export Data
- Click "📥 Export to Excel" to download projects

---

## 🔧 CLI Commands

```bash
# Launch web dashboard
python main.py web

# Run data pipeline
python main.py pipeline

# Generate demo data
python main.py demo

# Show statistics
python main.py stats
```

---

## 📚 Learn More

- Read the full [README.md](README.md) for detailed documentation
- Check [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- Review code structure and architecture

---

## ❓ Common Issues

**Issue**: `ModuleNotFoundError`
**Fix**: Make sure you activated the virtual environment and installed requirements

**Issue**: Dashboard won't load
**Fix**: Check if port 8501 is available, or use `streamlit run app.py --server.port 8502`

**Issue**: Scraping returns no results
**Fix**: Some websites may block scrapers. Check logs in `logs/app.log`

---

## 🎉 You're Ready!

Start discovering Saudi Arabia's active projects with AI-powered intelligence!
