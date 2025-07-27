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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import markpdfdown core functionality
from markpdfdown_core import MarkPDFDownProcessor, ProcessingError

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
        model_config = configure_model_settings()
    
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
    """Configure OpenAI API settings in sidebar"""
    # Check for API key from environment (for local development)
    env_api_key = os.getenv('OPENAI_API_KEY')
    
    # API Key input with fallback to environment
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=env_api_key if env_api_key else "",
        placeholder="sk-... (or set OPENAI_API_KEY in .env)",
        help="Enter your OpenAI API key for processing. For local development, you can also set OPENAI_API_KEY in a .env file."
    )
    
    # Save to session state
    if api_key:
        st.session_state.openai_api_key = api_key
        # Use default OpenAI API base
        st.session_state.openai_api_base = "https://api.openai.com/v1/"
        if env_api_key and api_key == env_api_key:
            st.success("✅ API Key loaded from .env file")
        else:
            st.success("✅ API Key configured")
    else:
        if env_api_key:
            st.info("💡 API Key found in .env - refresh to load")
        else:
            st.warning("⚠️ Please enter your OpenAI API key or set OPENAI_API_KEY in .env")

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

def configure_model_settings() -> dict:
    """Configure AI model settings"""
    # Check for default model from environment
    env_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    # Find index of environment model in options
    model_options = ["gpt-4o-mini", "gpt-4o", "gpt-4-vision-preview"]
    try:
        default_index = model_options.index(env_model)
    except ValueError:
        default_index = 0  # fallback to gpt-4o-mini
    
    model = st.selectbox(
        "AI Model",
        options=model_options,
        index=default_index,
        help="Select the AI model for processing. Default can be set with OPENAI_MODEL in .env"
    )
    
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="Controls randomness in AI responses"
    )
    
    max_tokens = st.slider(
        "Max Tokens",
        min_value=1000,
        max_value=8192,
        value=8192,
        step=256,
        help="Maximum tokens for AI response"
    )
    
    return {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

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
        
        processor = MarkPDFDownProcessor(
            api_key=st.session_state.openai_api_key,
            api_base=getattr(st.session_state, 'openai_api_base', 'https://api.openai.com/v1/'),
            model=model_config["model"]
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
            temperature=model_config["temperature"],
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