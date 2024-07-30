import os
from langchain_community.document_loaders import PyPDFLoader

def process_pdfs(file_paths):
    """Process uploaded PDF files into text chunks."""
    documents = []
    for file_path in file_paths:
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()
        documents.extend(pages)
        os.remove(file_path)  # Remove the file after processing

    return documents
