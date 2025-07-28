"""
pdf2markdown Streamlit Application

A professional Streamlit interface for converting PDF files to Markdown format
using multimodal large language models.
"""

import streamlit as st
import tempfile
import os
import time
import base64
from typing import Optional, Tuple
import logging
from dotenv import load_dotenv
import os
import requests
import json

# Load environment variables
current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, '.env')
load_dotenv(dotenv_path, override=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the core processing class
from pdf2markdown_core import PdfToMarkdownProcessor, ProcessingError

def get_ollama_models():
    """
    Dynamically fetch available Ollama models from local instance
    """
    try:
        # Try to connect to Ollama API
        ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        response = requests.get(f"{ollama_base_url.rstrip('/v1')}/api/tags", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            models = []
            if 'models' in data:
                for model in data['models']:
                    model_name = model.get('name', '')
                    if model_name:
                        models.append(model_name)
                
                # Sort models for better UX
                models.sort()
                
                if models:
                    return models
                    
    except Exception as e:
        logger.warning(f"Could not fetch Ollama models: {e}")
        
    # Fallback to common models if API call fails (vision-capable models first)
    fallback_models = [
        "minicpm-v:latest",  # Best for text accuracy
        "llava:latest",
        "llava:7b", 
        "gemma3:4b",
        "gemma3:12b", 
        "gemma3:27b",
        "mistral:latest",
        "qwen2.5:latest",
        "llama3.1:latest",
        "codellama:latest"
    ]
    
    return fallback_models

def configure_model_settings():
    """Configure model settings based on selected AI provider"""
    provider = st.session_state.get('ai_provider', 'openai')
    
    if provider == "openai":
        # OpenAI models
        openai_models = [
            "gpt-4o-mini",
            "gpt-4o"
        ]
        
        env_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        default_index = 0
        if env_model in openai_models:
            default_index = openai_models.index(env_model)
        
        model = st.selectbox(
            "🤖 Model",
            options=openai_models,
            index=default_index,
            help="Choose the OpenAI model for processing"
        )
        
    else:
        # Ollama models - fetch dynamically
        with st.spinner("🔍 Fetching available Ollama models..."):
            ollama_models = get_ollama_models()
        
        if not ollama_models:
            st.warning("⚠️ No Ollama models found. Please ensure Ollama is running and has models installed.")
            st.info("💡 For PDF processing, install a vision-capable model:")
            st.markdown("**🔥 Recommended for best text accuracy:**")
            st.code("ollama pull minicpm-v:latest", language="bash")
            st.info("⏱️ minicpm-v: Slower but more accurate")
            st.markdown("**Alternative vision models (faster):**")
            st.code("ollama pull llava:latest", language="bash")
            st.code("ollama pull llava:7b", language="bash") 
            model = "llava:latest"  # better fallback for vision
        else:
            env_model = os.getenv('OLLAMA_MODEL', ollama_models[0] if ollama_models else 'mistral:latest')
            default_index = 0
            
            # Try to find the environment model in the list
            if env_model in ollama_models:
                default_index = ollama_models.index(env_model)
            
            model = st.selectbox(
                "🤖 Model", 
                options=ollama_models,
                index=default_index,
                help="Choose your locally installed Ollama model"
            )
            
            # Show model info
            if ollama_models:
                st.info(f"📊 Found {len(ollama_models)} available models")
                
                # Check if selected model supports vision
                vision_models = ['llava', 'gemma3', 'qwen2-vl', 'minicpm-v', 'bakllava', 'moondream']
                is_vision_model = any(vm in model.lower() for vm in vision_models)
                
                if not is_vision_model:
                    st.warning("⚠️ Selected model may not support vision! PDF processing might fail.")
                    st.info("💡 **Best model**: minicpm-v:latest | **Alternative**: llava:latest, llava:7b")
                else:
                    st.success("✅ Vision-capable model selected")
                    # Extra encouragement for minicpm-v models
                    if 'minicpm-v' in model.lower():
                        st.info("🔥 **minicpm-v models have excellent text accuracy for PDF processing!**")
                        st.warning("⏱️ **Note:** minicpm-v is slower but more accurate than llava models")
                    elif 'llava' in model.lower():
                        st.info("✅ **llava models are good for PDF processing**")
                
                # Option to add custom model
                custom_model = st.text_input(
                    "Or enter custom model name:",
                    placeholder="e.g., llava:latest",
                    help="Enter a model name if it's not in the list above (preferably vision-capable)"
                )
                
                if custom_model.strip():
                    model = custom_model.strip()
    
    # Store in session state
    st.session_state.selected_model = model
    return model

def main():
    """Main Streamlit application function"""
    st.set_page_config(
        page_title="pdf2markdown - PDF to Markdown Converter",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        border-bottom: 2px solid #f0f2f6;
        margin-bottom: 2rem;
    }
    .config-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .processing-status {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>📄 pdf2markdown</h1>
        <p>Convert PDF documents to clean Markdown format using AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        configure_api_settings()
        
        # Processing options
        st.subheader("Processing Options")
        page_range = configure_page_options()
        
        st.subheader("Model Settings")
        selected_model = configure_model_settings()
        
        # Additional model parameters
        
        max_tokens = st.slider(
            "Max Tokens",
            min_value=1000,
            max_value=8192,
            value=8192,
            step=256,
            help="Maximum tokens for AI response"
        )
        
        # Create model config dictionary for compatibility
        model_config = {
            "model": selected_model,
            "max_tokens": max_tokens
        }
    
    # Main content area - vertical layout
    st.header("📤 Upload PDF")
    uploaded_file, processing_ready = handle_file_upload()
    
    if uploaded_file and processing_ready:
        if st.button("🚀 Convert to Markdown", type="primary", use_container_width=True):
            process_pdf_file(uploaded_file, page_range, model_config)
    
    # Markdown output section
    st.header("📝 Markdown Output")
    display_markdown_output()

def configure_api_settings():
    """Configure LLM API settings in sidebar"""
    # Provider selection
    provider = st.selectbox(
        "🤖 AI Provider",
        options=["OpenAI", "Ollama (Local)"],
        index=0,
        help="Choose between OpenAI (cloud) or Ollama (local) for AI processing"
    )
    
    provider_key = "openai" if provider.startswith("OpenAI") else "ollama"
    st.session_state.ai_provider = provider_key
    
    if provider_key == "openai":
        # OpenAI Configuration
        env_api_key = os.getenv('OPENAI_API_KEY')
        
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=env_api_key if env_api_key else "",
            placeholder="sk-... (or set OPENAI_API_KEY in .env)",
            help="Enter your OpenAI API key for processing. For local development, you can also set OPENAI_API_KEY in a .env file."
        )
        
        st.session_state.openai_api_base = "https://api.openai.com/v1/"
        
        if api_key:
            st.session_state.openai_api_key = api_key
            if env_api_key and api_key == env_api_key:
                st.success("✅ OpenAI API Key loaded from .env file")
            else:
                st.success("✅ OpenAI API Key configured")
        else:
            if env_api_key:
                st.info("💡 API Key found in .env - refresh to load")
            else:
                st.warning("⚠️ Please enter your OpenAI API key")
                
    else:
        # Ollama Configuration
        ollama_base_url = st.text_input(
            "Ollama Base URL",
            value=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434/v1'),
            placeholder="http://localhost:11434/v1",
            help="Base URL for your local Ollama instance"
        )
        
        st.session_state.openai_api_key = "ollama"
        st.session_state.openai_api_base = ollama_base_url
        st.success("✅ Ollama configured for local AI processing")
        st.info("💡 Make sure Ollama is running locally and your model is available")
        
        # Info about Ollama quality
        st.info("💡 **For best results:** Use OpenAI GPT-4 Vision or minicpm-v:latest (Ollama)")
        st.warning("⚠️ **Note:** Some Ollama models may be less accurate than OpenAI")

def configure_page_options() -> Tuple[int, int]:
    """Configure page range options"""
    col1, col2 = st.columns(2)
    
    with col1:
        start_page = st.number_input(
            "Start Page",
            min_value=1,
            value=1,
            help="First page to process"
        )
    
    with col2:
        end_page = st.number_input(
            "End Page",
            min_value=0,
            value=0,
            help="Last page to process (0 = all pages)"
        )
    
    return start_page, end_page

def handle_file_upload() -> Tuple[Optional[any], bool]:
    """Handle PDF file upload"""
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload a PDF file to convert to Markdown"
    )
    
    if uploaded_file is not None:
        # Display file info
        st.info(f"📄 **File:** {uploaded_file.name}")
        st.info(f"📊 **Size:** {uploaded_file.size / 1024:.1f} KB")
        
        # Check if API key is configured
        processing_ready = hasattr(st.session_state, 'openai_api_key') and st.session_state.openai_api_key
        
        if not processing_ready:
            st.warning("⚠️ Please configure your OpenAI API key in the sidebar first")
        
        return uploaded_file, processing_ready
    
    return None, False

def process_pdf_file(uploaded_file, page_range: Tuple[int, int], model_config: dict):
    """Process the uploaded PDF file"""
    start_page, end_page = page_range
    
    try:
        # Create progress indicators
        progress_bar = st.progress(0)
        status_container = st.empty()
        
        # Initialize processor
        status_container.markdown(
            '<div class="processing-status info">🔄 Initializing PDF processor...</div>',
            unsafe_allow_html=True
        )
        progress_bar.progress(10)
        
        provider = getattr(st.session_state, 'ai_provider', 'openai')
        processor = PdfToMarkdownProcessor(
            api_key=st.session_state.openai_api_key,
            api_base=getattr(st.session_state, 'openai_api_base', 'https://api.openai.com/v1/'),
            model=model_config["model"],
            provider=provider
        )
        
        # Save uploaded file temporarily
        status_container.markdown(
            '<div class="processing-status info">💾 Saving uploaded file...</div>',
            unsafe_allow_html=True
        )
        progress_bar.progress(20)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        # Process the PDF
        status_container.markdown(
            '<div class="processing-status info">🔄 Converting PDF to Markdown...</div>',
            unsafe_allow_html=True
        )
        progress_bar.progress(40)
        
        markdown_result = processor.convert_pdf_to_markdown(
            pdf_path=tmp_path,
            start_page=start_page,
            end_page=end_page,
            max_tokens=model_config["max_tokens"]
        )
        
        progress_bar.progress(100)
        
        # Clean up temporary file
        os.unlink(tmp_path)
        
        # Save result to session state
        st.session_state.markdown_result = markdown_result
        st.session_state.original_filename = uploaded_file.name
        
        status_container.markdown(
            '<div class="processing-status success">✅ Conversion completed successfully!</div>',
            unsafe_allow_html=True
        )
        
        # Auto-refresh to show result
        st.rerun()
        
    except ProcessingError as e:
        status_container.markdown(
            f'<div class="processing-status error">❌ Processing failed: {str(e)}</div>',
            unsafe_allow_html=True
        )
        logger.error(f"Processing error: {e}")
    
    except Exception as e:
        status_container.markdown(
            f'<div class="processing-status error">❌ Unexpected error: {str(e)}</div>',
            unsafe_allow_html=True
        )
        logger.error(f"Unexpected error: {e}")

def display_markdown_output():
    """Display the generated Markdown output"""
    if hasattr(st.session_state, 'markdown_result') and st.session_state.markdown_result:
        markdown_content = st.session_state.markdown_result
        
        # Display tabs for different views
        tab1, tab2 = st.tabs(["📖 Preview", "📝 Raw Markdown"])
        
        with tab1:
            st.markdown(markdown_content)
        
        with tab2:
            st.code(markdown_content, language="markdown")
        
        # Download button
        create_download_button(markdown_content)
    
    else:
        st.info("👆 Upload and process a PDF file to see the Markdown output here")

def create_download_button(markdown_content: str):
    """Create download button for the Markdown content"""
    # Generate filename
    if hasattr(st.session_state, 'original_filename'):
        base_name = os.path.splitext(st.session_state.original_filename)[0]
        filename = f"{base_name}_converted.md"
    else:
        filename = f"converted_{int(time.time())}.md"
    
    # Create download button
    st.download_button(
        label="💾 Download Markdown",
        data=markdown_content,
        file_name=filename,
        mime="text/markdown",
        use_container_width=True,
        type="secondary"
    )

if __name__ == "__main__":
    main()