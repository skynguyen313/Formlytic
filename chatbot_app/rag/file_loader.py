from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_pymupdf4llm import PyMuPDF4LLMLoader

from chonkie import OpenAIEmbeddings
from chonkie import SDPMChunker

from .standardize import preprocess_text

from django.conf import settings

DEFAULT_CHUNK_SIZE = 1024

class BaseLoader:
    def __init__(self) -> None:
        pass

    def __call__(self, file_path: str, **kwargs):
        pass


class PDFLoader(BaseLoader):
    def __init__(self) -> None:
        super().__init__()
        print("PDFLoader được khởi tạo")

    def __call__(self, file_path: str):
        doc_loaded = self._load_pdf_with_id(file_path)
        print(f"Đã tải xong file PDF, số trang: {len(doc_loaded)}")
        return doc_loaded
    
    
    def _load_pdf_with_id(self, file_path):
        try:
            print(f"Đang cố gắng tải file PDF từ: {file_path}")
            pages = PyMuPDF4LLMLoader(file_path).load()
            print(f"Tải thành công với {len(pages)} trang")
        except Exception as e:
            print(f"Lỗi khi tải file PDF: {str(e)}")
            return []

        documents = [
            Document(
                page_content=preprocess_text(page.page_content),
                metadata={"page": idx + 1, "source": file_path}
            )
            for idx, page in enumerate(pages)
        ]
        print(f"Đã tạo {len(documents)} Documents")
        return documents
    


class TextSplitter:
    def __init__(self, embedding=OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY,
                                            model="text-embedding-3-large")):
        self.chunker = SDPMChunker(embedding_model=embedding,  
                                   threshold=0.5,
                                   chunk_size=DEFAULT_CHUNK_SIZE,
                                   min_sentences=2,
                                   skip_window=2)
    def __call__(self, documents):  
        all_chunks = []
        for doc in documents:
            chunks = self.chunker.chunk(doc.page_content)
            # Chuyển đổi chunks thành Document objects với metadata
            for chunk in chunks:
                all_chunks.append(Document(
                    page_content=chunk.text,
                    metadata=doc.metadata
                ))
        return all_chunks


class Loader:
    def __init__(self) -> None:
        self.file_type = "pdf"
        self.doc_loader = PDFLoader()
        self.doc_splitter = TextSplitter()

    def load(self, file_path: str):
        print(f"Bắt đầu tải và xử lý file: {file_path}")
        doc_loaded = self.doc_loader(file_path)
        print(f"Đang chia nhỏ {len(doc_loaded)} documents đã tải")
        doc_split = self.doc_splitter(doc_loaded)
        print(f"Hoàn thành xử lý, trả về {len(doc_split)} chunks")
        # return doc_loaded
        return doc_split
    
if __name__ == "__main__":
    loader = Loader()
    
    file_path = "/mnt/d/VMU/NCKH/tai_lieu_sktt/Cam nang SKTT cho SV (10) final.pdf"
    
    chunks = loader.load(file_path)
    print(f"Đã tạo {len(chunks)} chunks")
    
    for chunk in chunks:
        print(chunk.page_content)
        print(chunk.metadata)
        print("-"*100)
    with open("/mnt/d/Desktop/output_chunks_sktt.txt", "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write("---- CHUNK START ----\n")
            f.write(chunk.page_content + "\n")
            f.write(f"Metadata: {chunk.metadata}\n")
            f.write("---- CHUNK END ----\n\n")
