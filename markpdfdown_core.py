"""
pdf2markdown Core Functionality

Refactored core functions from the original markpdfdown for Streamlit integration.
This module provides a clean interface for PDF to Markdown conversion.
"""

import os
import logging
import tempfile
import shutil
from typing import List, Optional
from dotenv import load_dotenv

# Import original core modules
from core.LLMClient import LLMClient
from core.FileWorker import create_worker
from core.Util import remove_markdown_warp

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class ProcessingError(Exception):
    """Custom exception for processing errors"""
    pass


class MarkPDFDownProcessor:
    """
    Main processor class for converting PDFs to Markdown using AI.
    
    This class encapsulates the core functionality of markpdfdown
    in a clean interface suitable for Streamlit integration.
    """
    
    def __init__(
        self,
        api_key: str,
        api_base: str = "https://api.openai.com/v1/",
        model: str = "gpt-4o-mini"
    ):
        """
        Initialize the pdf2markdown processor.
        
        Args:
            api_key: OpenAI API key
            api_base: OpenAI API base URL
            model: Model name to use for processing
        """
        self.api_key = api_key
        self.api_base = api_base
        self.model = model
        
        # Validate API key
        if not api_key:
            raise ProcessingError("OpenAI API key is required")
        
        # Initialize LLM client
        try:
            self.llm_client = LLMClient(
                base_url=api_base,
                api_key=api_key,
                model=model
            )
        except Exception as e:
            raise ProcessingError(f"Failed to initialize LLM client: {str(e)}")
    
    def convert_pdf_to_markdown(
        self,
        pdf_path: str,
        start_page: int = 1,
        end_page: int = 0,
        temperature: float = 0.3,
        max_tokens: int = 8192,
        dpi: int = 300
    ) -> str:
        """
        Convert a PDF file to Markdown format.
        
        Args:
            pdf_path: Path to the PDF file
            start_page: Starting page number (1-indexed)
            end_page: Ending page number (0 = all pages)
            temperature: Temperature for AI generation
            max_tokens: Maximum tokens for AI response
            dpi: DPI for image conversion
            
        Returns:
            str: Generated Markdown content
            
        Raises:
            ProcessingError: If processing fails
        """
        if not os.path.exists(pdf_path):
            raise ProcessingError(f"PDF file not found: {pdf_path}")
        
        # Create temporary output directory
        output_dir = tempfile.mkdtemp(prefix="pdf2markdown_")
        
        try:
            # Copy PDF to output directory for processing
            temp_pdf_path = os.path.join(output_dir, os.path.basename(pdf_path))
            shutil.copy2(pdf_path, temp_pdf_path)
            
            # Create file worker
            logger.info(f"Processing PDF: {pdf_path}")
            worker = create_worker(temp_pdf_path, start_page, end_page)
            
            # Convert PDF to images
            logger.info("Converting PDF pages to images...")
            img_paths = worker.convert_to_images(dpi=dpi)
            
            if not img_paths:
                raise ProcessingError("Failed to convert PDF to images")
            
            logger.info(f"Generated {len(img_paths)} images")
            
            # Convert each image to markdown
            markdown_content = ""
            
            for i, img_path in enumerate(sorted(img_paths), 1):
                logger.info(f"Converting image {i}/{len(img_paths)} to Markdown")
                
                try:
                    content = self._convert_image_to_markdown(
                        img_path=img_path,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    
                    if content:
                        markdown_content += content
                        if i < len(img_paths):  # Don't add newlines after the last page
                            markdown_content += "\n\n"
                
                except Exception as e:
                    logger.warning(f"Failed to convert image {img_path}: {str(e)}")
                    continue
            
            if not markdown_content.strip():
                raise ProcessingError("No content was generated from the PDF")
            
            logger.info("PDF conversion completed successfully")
            return markdown_content.strip()
            
        except Exception as e:
            if isinstance(e, ProcessingError):
                raise
            else:
                raise ProcessingError(f"Processing failed: {str(e)}")
        
        finally:
            # Clean up temporary directory
            try:
                shutil.rmtree(output_dir)
            except Exception as e:
                logger.warning(f"Failed to clean up temporary directory: {e}")
    
    def convert_image_to_markdown(
        self,
        image_path: str,
        temperature: float = 0.3,
        max_tokens: int = 8192
    ) -> str:
        """
        Convert a single image to Markdown format.
        
        Args:
            image_path: Path to the image file
            temperature: Temperature for AI generation
            max_tokens: Maximum tokens for AI response
            
        Returns:
            str: Generated Markdown content
            
        Raises:
            ProcessingError: If processing fails
        """
        if not os.path.exists(image_path):
            raise ProcessingError(f"Image file not found: {image_path}")
        
        try:
            return self._convert_image_to_markdown(
                img_path=image_path,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as e:
            raise ProcessingError(f"Image conversion failed: {str(e)}")
    
    def _convert_image_to_markdown(
        self,
        img_path: str,
        temperature: float = 0.3,
        max_tokens: int = 8192,
        retry_times: int = 3
    ) -> str:
        """
        Internal method to convert an image to Markdown using AI.
        
        Args:
            img_path: Path to the image
            temperature: Temperature for generation
            max_tokens: Maximum tokens
            retry_times: Number of retry attempts
            
        Returns:
            str: Generated Markdown content
        """
        system_prompt = """
You are a helpful assistant that can convert images to Markdown format. You are given an image, and you need to convert it to Markdown format. Please output the Markdown content only, without any other text.
"""
        
        user_prompt = """
Below is the image of one page of a document, please read the content in the image and transcribe it into plain Markdown format. Please note:

IMPORTANT RULES:
1. DO NOT generate any image references like ![alt](url) or <img> tags
2. If you see images, charts, or diagrams, describe them in text format instead
3. Convert tables to proper Markdown table format with | symbols
4. Identify heading levels, text styles, and formatting
5. Mathematical formulas should be transcribed using LaTeX syntax ($ for inline, $$ for block)
6. For images/charts, use descriptive text like: "**Chart Description:** [describe what you see]"
7. Please output the Markdown content only, without any other text

Output Example:
```markdown
# Document Title

Regular paragraph text here.

**Chart Description:** Bar chart showing sales data from 2020-2023, with increasing trend.

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |

Mathematical formula: $E = mc^2$
```
"""
        
        # Attempt conversion with retry logic
        for attempt in range(retry_times):
            try:
                response = self.llm_client.completion(
                    user_message=user_prompt,
                    system_prompt=system_prompt,
                    image_paths=[img_path],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                
                if response:
                    # Remove markdown code block wrappers if present
                    cleaned_response = remove_markdown_warp(response, "markdown")
                    return cleaned_response
                else:
                    logger.warning(f"Empty response for image {img_path}, attempt {attempt + 1}")
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for image {img_path}: {str(e)}")
                if attempt == retry_times - 1:
                    raise ProcessingError(f"Failed to convert image after {retry_times} attempts")
        
        # This should never be reached due to the logic above, but just in case
        raise ProcessingError(f"Failed to convert image after {retry_times} attempts")

    def validate_api_connection(self) -> bool:
        """
        Validate the API connection by making a simple test call.
        
        Returns:
            bool: True if connection is valid, False otherwise
        """
        try:
            # Make a simple test call
            test_response = self.llm_client.completion(
                user_message="Hello, this is a test message.",
                system_prompt="You are a helpful assistant. Respond with 'Test successful'.",
                temperature=0.0,
                max_tokens=10
            )
            
            return "test successful" in test_response.lower()
            
        except Exception as e:
            logger.error(f"API validation failed: {str(e)}")
            return False

    @staticmethod
    def get_supported_formats() -> List[str]:
        """
        Get list of supported file formats.
        
        Returns:
            List[str]: List of supported file extensions
        """
        return ['.pdf', '.jpg', '.jpeg', '.png', '.bmp']

    @staticmethod
    def estimate_processing_time(file_size_mb: float, num_pages: int = None) -> int:
        """
        Estimate processing time for a file.
        
        Args:
            file_size_mb: File size in megabytes
            num_pages: Number of pages (if known)
            
        Returns:
            int: Estimated processing time in seconds
        """
        # Base time estimation: ~30 seconds per page for AI processing
        if num_pages:
            base_time = num_pages * 30
        else:
            # Estimate pages based on file size (rough estimate: 1MB per 10 pages)
            estimated_pages = max(1, int(file_size_mb / 0.1))
            base_time = estimated_pages * 30
        
        # Add overhead for PDF processing
        overhead = max(10, file_size_mb * 2)
        
        return int(base_time + overhead)