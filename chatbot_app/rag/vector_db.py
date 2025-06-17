import os
from typing import List
from langchain.retrievers import EnsembleRetriever
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.documents import Document
from django.conf import settings

vector_db_path = "./chatbot_app/indexes"

class VectorDB:
    def __init__(self,
                 vector_db=FAISS,
                 embedding=OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY,
                                            model="text-embedding-3-large")):
        self.vector_db = vector_db
        self.embedding = embedding
        self.db = self._load_or_initialize_db()

    def _initialize_index(self):
        empty_content = " "
        documents = [Document(
            page_content=empty_content,
            metadata={"id": "empty", "page": 1, "source": "empty.pdf"}
        )]
        db = self.vector_db.from_documents(documents=documents, embedding=self.embedding)
        db.save_local(vector_db_path)
        return db

    def _load_or_initialize_db(self):
        """Load existing index or initialize if not found."""
        os.makedirs(vector_db_path, exist_ok=True)

        index_faiss = os.path.join(vector_db_path, "index.faiss")
        index_pkl = os.path.join(vector_db_path, "index.pkl")

        if os.path.exists(index_faiss) and os.path.exists(index_pkl):
            try:
                db = self.vector_db.load_local(vector_db_path,
                                               embeddings=self.embedding,
                                               allow_dangerous_deserialization=True)
            except Exception as e:
                db = self._initialize_index()
        else:
            db = self._initialize_index()

        return db


    def add_data(self, new_documents):
        if not new_documents:
            return False
        self.db.add_documents(documents=new_documents)
        self.db.save_local(vector_db_path)
        return True

    def get_retriever(self,
                      search_type: str = "similarity",
                      search_kwargs: dict = {"k": 5},
                      weights: List[float] = [0.6, 0.4]):
    
        faiss_retriever = self.db.as_retriever(search_type=search_type,
                                         search_kwargs=search_kwargs)
        dense_retriever = self.db.as_retriever(search_type="mmr", search_kwargs=search_kwargs)
        ensemble_retriever = EnsembleRetriever(retrievers=[faiss_retriever, dense_retriever], weights=weights)
        return ensemble_retriever
