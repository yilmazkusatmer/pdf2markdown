# pdf2markdown - Streamlit App

A clean, professional Streamlit application for converting PDF files to Markdown format using AI.

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Option 1: Set API key in .env file (recommended for development)
cp .env.example .env
# Edit .env and add your OpenAI API key

# Option 2: Use the web interface to enter your API key
# Run the app
streamlit run app.py
```

### Streamlit Cloud Deployment
1. Upload this repository to GitHub
2. Connect to Streamlit Cloud
3. Deploy with main file: `streamlit_app.py`

## 📋 Requirements

- Python 3.8+
- OpenAI API key for AI processing
- Dependencies listed in `streamlit_requirements.txt`

## 🎯 Features

- **PDF Upload**: Drag and drop PDF files
- **AI Conversion**: Uses OpenAI models for accurate conversion
- **Markdown Preview**: Live preview with syntax highlighting
- **Download**: Export converted Markdown files
- **Clean UI**: Vertical layout optimized for conversion workflow

## 🔧 Configuration

**User-Provided API Keys**: Each user enters their own OpenAI API key through the sidebar interface. No API keys are stored or provided by the application.

### For Users:
1. Get your OpenAI API key from: https://platform.openai.com/api-keys
2. Enter it in the sidebar when using the app
3. Your key is only stored in your browser session

## 📄 License

Licensed under the MIT License. See LICENSE file for details.