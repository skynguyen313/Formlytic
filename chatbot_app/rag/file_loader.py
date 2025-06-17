from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200



class BaseLoader:
    def __init__(self) -> None:
        pass

    def __call__(self, file_path: str, id_file_filter: str, **kwargs):
        pass


class PDFLoader(BaseLoader):
    def __init__(self) -> None:
        super().__init__()

    def __call__(self, file_path: str, id_file_filter: str, **kwargs):
        doc_loaded = self._load_pdf_with_id(file_path, id_file_filter)
        return doc_loaded
    
    
    def _load_pdf_with_id(self, file_path, id_file_filter):
        try:
            pages = PyPDFLoader(file_path).load()
        except Exception as e:
            return []

        documents = [
            Document(
                page_content=page.page_content,
                metadata={"id": id_file_filter, "page": idx + 1, "source": file_path}
            )
            for idx, page in enumerate(pages)
        ]
        return documents
    


class TextSplitter:
    def __init__(self,
                 separators: List[str] = ["\n\n", "\n", " ", ""],
                 chunk_size: int = DEFAULT_CHUNK_SIZE,
                 chunk_overlap: int = DEFAULT_CHUNK_OVERLAP) -> None:
        self.splitter = RecursiveCharacterTextSplitter(separators=separators,
                                                       chunk_size=chunk_size,
                                                       chunk_overlap=chunk_overlap)

    def __call__(self, documents):
        return self.splitter.split_documents(documents)


class Loader:
    def __init__(self,
                 split_kwargs: dict = {"chunk_size": DEFAULT_CHUNK_SIZE,
                                        "chunk_overlap": DEFAULT_CHUNK_OVERLAP}
                 ) -> None:
        self.file_type = "pdf"
        self.doc_loader = PDFLoader()
        self.doc_splitter = TextSplitter(**split_kwargs)

    def load(self, file_path: str, id_file_filter: str):
        doc_loaded = self.doc_loader(file_path, id_file_filter)
        doc_split = self.doc_splitter(doc_loaded)
        return doc_split
