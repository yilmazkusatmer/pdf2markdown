# MarkPDFDown - Streamlit App

A clean, professional Streamlit application for converting PDF files to Markdown format using AI.

## 🚀 Quick Start

### Local Development
```bash
pip install -r streamlit_requirements.txt
streamlit run streamlit_app.py
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

Set your OpenAI API key in the sidebar or use Streamlit secrets:

```toml
# .streamlit/secrets.toml
openai_api_key = "sk-..."
```

## 📄 License

Licensed under the MIT License. See LICENSE file for details.