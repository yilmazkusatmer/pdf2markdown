import os
import logging
import PyPDF2
from typing import List, Dict

logger = logging.getLogger(__name__)

class PDFWorker:
    """
    A class for handling PDF files using PyPDF2
    """
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.reader = PyPDF2.PdfReader(pdf_path)
        self.total_pages = len(self.reader.pages) 

    def get_total_pages(self) -> int:
        """
        Get the total number of pages in the PDF

        Returns:
            int: Total number of pages
        """
        return self.total_pages

    def extract_pages(self, start_page: int, end_page: int, output_dir: str = ".", output_name: str = None) -> str:
        """
        Extract PDF content from specified page range
        
        Args:
            start_page (int): Starting page number (1-based)
            end_page (int): Ending page number (1-based)
            output_dir (str): Output directory path
            output_name (str): Custom output filename (optional)
            
        Returns:
            str: Generated PDF file path, returns empty string if failed
        """
        try:
            # 转换页码为0-based索引
            start = max(0, start_page - 1)
            end = min(self.total_pages - 1, end_page - 1)
            
            if start > end:
                start, end = end, start  # 自动修正页码顺序
                
            writer = PyPDF2.PdfWriter()
            
            # 添加指定页面的内容
            for page_num in range(start, end + 1):
                writer.add_page(self.reader.pages[page_num])
            
            # 生成输出文件名
            if not output_name:
                base_name = os.path.basename(self.pdf_path).rsplit('.', 1)[0]
                output_name = f"{base_name}_pages_{start_page}-{end_page}.pdf"
            
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, output_name)
            
            # 写入文件
            with open(output_path, 'wb') as out_file:
                writer.write(out_file)
                
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to extract pages: {str(e)}")
            return ""

    def convert_to_images(self, output_dir: str = ".", dpi: int = 300, fmt: str = 'jpg') -> List[str]:
        """
        Convert each PDF page to high-quality images using PyMuPDF
        
        Args:
            output_dir (str): Output directory path
            dpi (int): Output image resolution (default 300)
            fmt (str): Image format (supports jpg/png, default jpg)
            
        Returns:
            List[str]: List of generated image paths
        """
        try:
            import fitz  # PyMuPDF
            os.makedirs(output_dir, exist_ok=True)
            img_paths = []

            doc = fitz.open(self.pdf_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=dpi)
                output_path = os.path.join(output_dir, f"page_{page_num+1:04d}.{fmt}")
                pix.save(output_path)
                img_paths.append(output_path)
            
            return img_paths
            
        except Exception as e:
            logger.error(f"Failed to convert PDF to images: {str(e)}")
            return []