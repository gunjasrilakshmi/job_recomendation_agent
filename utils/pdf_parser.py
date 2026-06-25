"""
PDF Parser Utility
Extracts text content from uploaded PDF resume files.
"""

import pdfplumber
import io


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extract text content from an uploaded PDF file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Extracted text as a string
        
    Raises:
        Exception: If PDF parsing fails
    """
    text_parts = []
    try:
        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)  # Reset file pointer for potential re-reads
        
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                    
        if not text_parts:
            raise Exception(
                "No text could be extracted from the PDF. "
                "The file may be image-based or corrupted."
            )
            
    except Exception as e:
        if "No text could be extracted" in str(e):
            raise
        raise Exception(f"Error reading PDF file: {str(e)}")
    
    return "\n\n".join(text_parts).strip()
