from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PDFMinerLoader, UnstructuredHTMLLoader
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

class VectorStoreManager:
    def __init__(self, persist_directory="./vectorstore"):
        self.persist_directory = persist_directory
        self.embeddings = GoogleGenerativeAIEmbeddings(model="embedding-001", google_api_key="YOUR_API_KEY")
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )

    def load_and_split(self, filepath):
        extension = os.path.splitext(filepath)[1].lower()
        if extension == ".txt":
            loader = TextLoader(filepath)
        elif extension == ".pdf":
            loader = PDFMinerLoader(filepath)
        elif extension == ".html" or extension == ".htm":
            loader = UnstructuredHTMLLoader(filepath)
        else:
            raise ValueError(f"Unsupported file type: {extension}")
        documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        return splitter.split_documents(documents)

    def add_document(self, filepath):
        docs = self.load_and_split(filepath)
        self.vectorstore.add_documents(docs)

    def get_vectorstore(self):
        return self.vectorstore