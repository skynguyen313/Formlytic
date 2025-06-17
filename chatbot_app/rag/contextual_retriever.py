from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever

context_prompt = """Cho trước lịch sử hội thoại và câu hỏi gần nhất của người dùng,
để có thể tham chiếu ngữ cảnh cho lịch sử hội thoại, hãy tạo ra một câu hỏi độc lập
để có thể hiểu được mà không cần lịch sử cuộc hội thoại. Không được trả lời câu hỏi,
chỉ cần sửa lại câu hỏi nếu cần và nếu không thì để lại như cũ.
"""

class ContextualRetriever:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", context_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])

    def get_history_aware_retriever(self):
        return create_history_aware_retriever(self.llm, self.retriever, self.prompt_template)