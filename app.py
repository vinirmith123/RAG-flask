import os
import streamlit as st
from dotenv import load_dotenv
from utils.pdf_utils import process_pdfs
from utils.vector_utils import create_vector_db, retrieve_and_invoke

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def main():
    st.set_page_config(page_title="PDF Query Application", page_icon="📄")
    st.title("PDF Query Application")

    # File uploader
    pdf_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

    if pdf_files:
        with st.spinner("Processing PDFs..."):
            documents = process_pdfs(pdf_files)
            vectordb = create_vector_db(documents)
            
            query = st.text_input("Ask a question about the PDFs")
            if query:
                response = retrieve_and_invoke(vectordb, query)
                st.subheader("Answer:")
                st.write(response["answer"])
                
                st.subheader("Context:")
                for document in response["context"]:
                    st.write(document.page_content)

if __name__ == "__main__":
    main()
