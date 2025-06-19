import os
from typing import List
from langchain.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_core.retrievers import BaseRetriever
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.documents import Document
from django.conf import settings

from rerankers import Reranker

vector_db_path = os.path.join(settings.BASE_DIR, "chatbot_app", "indexes")


class VectorDB:
    def __init__(self,
                 vector_db=FAISS,
                 embedding=OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY,
                                            model="text-embedding-3-large")):
        self.vector_db = vector_db
        self.embedding = embedding
        self.db = self._load_or_initialize_db()
        self.reranker = Reranker('gpt-4o', model_type="rankllm", api_key = settings.OPENAI_API_KEY)

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
        
        batch_size = 5
        total_docs = len(new_documents)
        
        for i in range(0, total_docs, batch_size):
            batch = new_documents[i:i + batch_size]
            try:
                self.db.add_documents(documents=batch)
                print(f"[DEBUG] Đã thêm batch {i//batch_size + 1}: {len(batch)} documents")
            except Exception as e:
                print(f"[ERROR] Lỗi khi thêm batch {i//batch_size + 1}: {e}")
                return False
        
        # Save sau khi thêm tất cả batch
        self.db.save_local(vector_db_path)
        print(f"[DEBUG] Hoàn thành thêm {total_docs} documents vào vector store")
        return True

    def get_retriever(self,
                      search_kwargs: dict = {"k": 5},
                      weights: List[float] = [0.8, 0.2]):
    
        faiss_retriever = self.db.as_retriever(
            search_type="similarity",
            search_kwargs=search_kwargs
        )
        
        mmr_retriever = self.db.as_retriever(
            search_type="mmr",
            search_kwargs=search_kwargs
        )
        
        ensemble_retriever = EnsembleRetriever(
            retrievers=[faiss_retriever, mmr_retriever],
            weights=weights
        )
        return ensemble_retriever
    
    def get_compressed_retriever(self, search_kwargs: dict = {"k": 8}):
        # Tạo base retriever
        base_retriever = self.get_context_enriched_retriever()
        
        # Tạo compressor từ reranker
        compressor = self.reranker.as_langchain_compressor(k=4)
        
        # Tạo compressed retriever
        compressed_retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=base_retriever
        )
        return compressed_retriever
    
    def context_enriched_search(self, query: str, k: int = 5, context_size: int = 1):
        """
        Tìm kiếm với context enriched - đơn giản
        
        Args:
            query: Câu hỏi tìm kiếm
            k: Số chunks chính cần lấy
            context_size: Số chunks lân cận mỗi bên
        """
        # Tìm kiếm cơ bản trước
        retriever = self.get_retriever(search_kwargs={"k": k})
        docs = retriever.invoke(query)
        
        if not docs:
            return []
        
        enriched_docs = []
        
        for doc in docs:
            # Lấy thông tin chunk hiện tại
            chunk_index = doc.metadata.get('chunk_index', 0)
            source = doc.metadata.get('source', '')
            
            # Tìm các chunks lân cận
            context_docs = self._get_neighbor_chunks(source, chunk_index, context_size)
            
            if context_docs:
                # Tạo enriched content từ các chunks lân cận
                enriched_content = self._combine_chunks(context_docs, chunk_index)
                
                # Tạo document mới với enriched content
                enriched_doc = Document(
                    page_content=enriched_content,
                    metadata={
                        **doc.metadata,
                        "enriched": True,
                        "context_chunks": len(context_docs)
                    }
                )
                enriched_docs.append(enriched_doc)
            else:
                # Nếu không tìm thấy neighbors, giữ nguyên
                enriched_docs.append(doc)
        
        return enriched_docs
    
    def _get_neighbor_chunks(self, source: str, chunk_index: int, context_size: int):
        """Tìm các chunks lân cận"""        
        # Query để tìm chunks cùng source (trick đơn giản)
        try:
            # Tìm kiếm với source name
            source_docs = self.db.similarity_search(f"source:{source}", k=50)
            
            # Filter theo source thật sự và sort theo chunk_index
            same_source_docs = []
            for doc in source_docs:
                if doc.metadata.get('source') == source:
                    same_source_docs.append(doc)
            
            # Sort theo chunk_index
            same_source_docs.sort(key=lambda x: x.metadata.get('chunk_index', 0))
            
            # Tìm vị trí của chunk hiện tại
            current_pos = -1
            for i, doc in enumerate(same_source_docs):
                if doc.metadata.get('chunk_index') == chunk_index:
                    current_pos = i
                    break
            
            if current_pos >= 0:
                # Lấy context chunks
                start = max(0, current_pos - context_size)
                end = min(len(same_source_docs), current_pos + context_size + 1)
                return same_source_docs[start:end]
                
        except Exception as e:
            print(f"[DEBUG] Lỗi khi tìm neighbor chunks: {e}")
            
        return []
    
    def _combine_chunks(self, chunks: List[Document], main_chunk_index: int):
        """Kết hợp các chunks thành content enriched"""
        combined_parts = []
        
        for chunk in chunks:
            current_index = chunk.metadata.get('chunk_index', 0)
            
            if current_index == main_chunk_index:
                # Chunk chính
                combined_parts.append(f"[NỘI DUNG CHÍNH]:\n{chunk.page_content}")
            elif current_index < main_chunk_index:
                # Context trước
                combined_parts.append(f"[CONTEXT TRƯỚC]:\n{chunk.page_content}")
            else:
                # Context sau
                combined_parts.append(f"[CONTEXT SAU]:\n{chunk.page_content}")
        
        return "\n\n".join(combined_parts)
    
    def get_context_enriched_retriever(self, k: int = 5, context_size: int = 1):
        """Tạo retriever với context enriched đơn giản"""
        
        # Capture vector_db trong closure
        vector_db_instance = self
        
        class SimpleContextRetriever(BaseRetriever):
            """Context Enriched Retriever"""
            
            def _get_relevant_documents(
                self, 
                query: str, 
                *, 
                run_manager: CallbackManagerForRetrieverRun = None
            ) -> List[Document]:
                return vector_db_instance.context_enriched_search(query, k, context_size)
        
        return SimpleContextRetriever()

if __name__ == "__main__":
    from llm_model import get_openai_llm
    from file_loader import Loader
    llm = get_openai_llm()
    pdf_file = "/mnt/d/VMU/NCKH/tai_lieu_sktt/Cam nang SKTT cho SV (10) final.pdf"
    vector_db = VectorDB()
    
    # add data
    # loader = Loader()
    # chunks= loader.load(pdf_file, "test")
    # vector_db.add_data(chunks)

    input = "Một dấu hiệu thể chất của rối loạn lo âu là gì?"
    print(input)
    compressed_retriever = vector_db.get_compressed_retriever()
    reranked_docs = compressed_retriever.invoke(input)
    vector_db.pretty_print_docs_langchain(reranked_docs)