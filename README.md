# pdf2markdown - Streamlit App

A clean, professional Streamlit application for converting PDF files to Markdown format using AI. Supports both **OpenAI** (cloud) and **Ollama** (local) for maximum flexibility.

## 🚀 Quick Start

### Option 1: OpenAI (Cloud)
```bash
# Install dependencies
pip install -r requirements.txt

# Set up OpenAI configuration
cp .env.example .env
# Edit .env and add your OpenAI API key

# Run the app
streamlit run app.py
```

### Option 2: Ollama (Local & Private)
```bash
# Install dependencies
pip install -r requirements.txt

# Install and start Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llava:latest  # Recommended for PDF processing
# Alternative: ollama pull llava:7b

# Configure environment (optional)
cp .env.example .env
# Edit .env: set OLLAMA_BASE_URL and OLLAMA_MODEL

# Run the app
streamlit run app.py
# Select "Ollama (Local)" in the AI Provider dropdown
```

### Streamlit Cloud Deployment
1. Upload this repository to GitHub
2. Connect to Streamlit Cloud
3. Deploy with main file: `app.py`

## 🤖 AI Provider Options

| Provider | Type | Privacy | Cost | Setup Complexity |
|----------|------|---------|------|------------------|
| **OpenAI** | Cloud | Low | Pay per use | Easy |
| **Ollama** | Local | High | Free | Medium |

## 📋 Requirements

- Python 3.9+
- **For OpenAI**: API key from https://platform.openai.com/api-keys
- **For Ollama**: Local Ollama installation
- Dependencies listed in `requirements.txt`

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