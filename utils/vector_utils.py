from langchain_community.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

def create_vector_db(documents):
    """Create and persist a Chroma vector store."""
    vectordb = Chroma.from_documents(documents=documents, embedding=embedding)
    return vectordb

def retrieve_and_invoke(vectordb, query):
    """Retrieve documents from Chroma vector store and use RAG chain."""
    from langchain.chains import create_retrieval_chain
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain_core.prompts import ChatPromptTemplate

    retriever = vectordb.as_retriever(search_kwargs={"k": 5})

    # Initialize LLM and prompt template for RAG
    from langchain_openai import ChatOpenAI
    from langchain import hub

    llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
    prompt = hub.pull("rlm/rag-prompt")

    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        "{context}"
    )

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, prompt_template)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    response = rag_chain.invoke({"input": query})
    return response
