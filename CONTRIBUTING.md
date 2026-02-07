# Contributing to Saudi Projects Intelligence Platform

Thank you for considering contributing to this project! 🎉

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)

### Suggesting Features

Feature suggestions are welcome! Please create an issue with:
- Clear description of the feature
- Use case and benefits
- Possible implementation approach (optional)

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Test your changes thoroughly
5. Commit with clear messages (`git commit -m 'Add feature: description'`)
6. Push to your fork (`git push origin feature/your-feature`)
7. Create a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Add docstrings to functions and classes
- Include type hints where appropriate
- Keep functions focused and modular
- Comment complex logic

### Testing

Before submitting:
- Test with demo data
- Run the pipeline end-to-end
- Check the UI works properly
- Verify no errors in logs

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/saudi-projects-intelligence.git
cd saudi-projects-intelligence

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Generate demo data
python utils/demo_data.py

# Run the app
streamlit run app.py
```

## Areas for Contribution

- **Scrapers**: Add new data sources
- **AI Engine**: Improve extraction accuracy
- **UI/UX**: Enhance dashboard design
- **Performance**: Optimize scraping and processing
- **Documentation**: Improve docs and examples
- **Testing**: Add unit and integration tests
- **Localization**: Improve Arabic language support

## Questions?

Feel free to open an issue for any questions or discussions!

---

Thank you for contributing! 🙏
