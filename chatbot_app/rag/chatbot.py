from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from .llm_model import get_openai_llm
from .vector_db import VectorDB
from .contextual_retriever import ContextualRetriever
from .qa_chain import QuestionAnsweringChain
from .state_manager import StateManager
from .intent_classifier import IntentClassifier
from .data_manager import DataManager
from .standardize import preprocess_text

class Chatbot:
    def __init__(self):
        self.llm_4o = get_openai_llm()
        self.llm_4o_mini = get_openai_llm(model_name="gpt-4o-mini")
       
        self.vector_db = VectorDB() 
        self.retriever = self.vector_db.get_compressed_retriever(search_kwargs={"k": 6})
        self.contextual_retriever = ContextualRetriever(self.llm_4o, self.retriever).get_history_aware_retriever()
        self.db_manager = DataManager(self.llm_4o_mini)
        self.qa_chain = QuestionAnsweringChain(self.llm_4o).create_qa_chain()
        
        self.rag_chain = create_retrieval_chain(self.contextual_retriever, self.qa_chain)
        
        self.intent_classifier = IntentClassifier(self.llm_4o)
        
        # Khởi tạo bộ nhớ
        self.memory = MemorySaver()


    def reset(self):
        """Reset all components of the chatbot."""
        self.llm_4o = get_openai_llm()
        self.llm_4o_mini = get_openai_llm(model_name="gpt-4o-mini")
        self.vector_db = VectorDB()
        self.retriever = self.vector_db.get_compressed_retriever()
        self.contextual_retriever = ContextualRetriever(self.llm_4o, self.retriever).get_history_aware_retriever()
        self.db_manager = DataManager(self.llm_4o_mini)
        self.qa_chain = QuestionAnsweringChain(self.llm_4o).create_qa_chain()
        
        # Rebuild retrieval-augmented generation (RAG) chain
        self.rag_chain = create_retrieval_chain(self.contextual_retriever, self.qa_chain)
        
        self.intent_classifier = IntentClassifier(self.llm_4o)
        # Re-initialize memory saver
        self.memory = MemorySaver()


    def classify_intent(self, state: StateManager):
        question = state["input"]
        
        intent = self.intent_classifier.classify(question)
        state["current_intent"] = intent
        
        return state

    def call_model(self, state: StateManager):
        question = state["input"]
        current_intent = state.get("current_intent", "1")   
        
        is_sktt = state.get("is_sktt", False)
        
        if is_sktt:
            response = self.call_sktt_model(state)
            return response
        else:
            if current_intent == "0":
                response = self.rag_chain.invoke(state)
                
                return {
                    "chat_history": [
                        HumanMessage(state["input"]),
                        AIMessage(response["answer"]),
                    ],
                    "context": response["context"],
                    "answer": response["answer"],
                    "current_intent": current_intent,
                }
                
            relevant_docs = self.retriever.invoke(question)
            state["context"] = "\n".join([doc.page_content for doc in relevant_docs])

            response = self.rag_chain.invoke(state)        
            
            return {
                "chat_history": [
                    HumanMessage(state["input"]),
                    AIMessage(response["answer"]),
                ],
                "context": response["context"],
                "answer": response["answer"],
                "current_intent": current_intent,
            }

    def call_sktt_model(self, state: StateManager):
         
        template = """
        # DIRECTIVE
Mục tiêu duy nhất của bạn là cung cấp các câu trả lời chính xác và hữu ích cho các câu hỏi của người dùng *chỉ* liên quan đến sức khỏe tinh thân người dùng. Bạn phải sử dụng thông tin ngữ cảnh được cung cấp bên dưới để tạo ra câu trả lời của mình.
# PERSONA DEFINITION
Bạn là một trợ lý hỗ trợ giải đáp thắc mắc của người dùng. Nhiệm vụ của bạn là:
- Đưa ra câu trả lời mang tính hướng dẫn.
- Dựa vào kết quả của các bài khảo sát tâm lý để đưa ra các khuyến nghị tư vấn tâm lý cho người dùng.
# CORE
# BEHAVIORAL PROTOCOLS
- **Bảo mật thông tin:** Bạn sẽ được cung cấp một `ngữ cảnh` chứa thông tin truy vấn liên quan và kết quả bài đánh giá tâm lý. Bạn phải xem đây là nguồn thông tin duy nhất và tích hợp vào câu trả lời một cách tự nhiên. Không được tiết lộ rằng bạn đang sử dụng thông tin từ ngữ cảnh được cung cấp.
- **Tuân thủ phạm vi:** Bạn hãy phân tích ngữ cảnh để biết lĩnh vực mà mình tư vấn. Nếu câu hỏi nằm ngoài lĩnh vực đó, bạn phải từ chối trả lời và nhẹ nhàng nhắc lại chức năng chuyên biệt của mình (ví dụ: "Tôi chưa tìm thấy thông tin bạn muốn hỏi, xin hãy cung cấp chi tiết hơn.").
- **Cách xử lý khi không chắc chắn:** Nếu ngữ cảnh không chứa thông tin rõ ràng hoặc câu hỏi mơ hồ, bạn phải yêu cầu người dùng làm rõ.
# MEMORY
Lịch sử trò chuyện:
{chat_history}
# KNOWLEDGE BASE
Ngữ cảnh:
{context}
Kết quả các bài đánh giá tâm lý (nếu có): 
{answer_query}
# CURRENT QUERY
Người dùng: Hãy phân tích kết quả bài đánh giá tâm lý của tôi dựa trên context
# RESPONSE
Trợ lý:
""".strip()
        
        state["context"] = """1. Mức độ nhẹ – vừa
Nội dung tư vấn: Kết quả rối loạn mức độ nhẹ hoặc vừa không đồng nghĩa với bệnh tâm thần mà là cảnh báo tình trạng cảm xúc bị ảnh hưởng. 
-	Những việc nên làm:
+ Tập cường hoạt động thể chất: chọn môn thể thao yêu thích (đi bộ, đạp xe, yoga….), tập tối thiểu 5 ngày/tuần, mỗi lần tập 45-60 phút.
+ Tập thở sâu
+ Tăng tương tác với người thân, bạn, đồng nghiệp, không giữ tâm lý tiêu cực một mình
+ Nghe nhạc, thư giãn
+ Quản lý thời gian, giảm tải công việc
-	Những việc không nên làm: 
+ Uống rượu, bia
+ Sử dụng chất kích thích
+ Sử dụng thiết bị điện tử vào ban đêm
Khuyến nghị: Theo dõi lại sau 2–4 tuần. Nếu triệu chứng không cải thiện, chuyển sang nhóm tư vấn sâu hoặc y tế chuyên khoa.
2. Mức độ nặng – rất nặng
- Cần liên hệ với Bác sĩ tâm thần hoặc chuyên gia tư vấn tâm lý để được tư vấn, điều trị kịp thời."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", template),
        ])
        
        prompt = prompt.format(
            chat_history=state["chat_history"],
            context=state["context"],
            answer_query=state["result"]
        )
        
        response = self.llm_4o.invoke(prompt)

# Lấy nội dung câu trả lời từ đối tượng AIMessage
        ai_answer_content = response.content

        # Lấy lịch sử trò chuyện cũ từ state
        previous_chat_history = state.get("chat_history", [])

        # Tạo lịch sử trò chuyện mới bằng cách nối tin nhắn cũ với tin nhắn mới
        new_chat_history = previous_chat_history + [
            HumanMessage(content=state["input"]),
            AIMessage(content=ai_answer_content),
        ]

        print(state)
        # Trả về state đã được cập nhật
        return {
            "chat_history": new_chat_history,
            "context": state["context"],  # Lấy lại context từ state, không phải từ response
            "answer": ai_answer_content  # Trả về nội dung câu trả lời
        }
        

    def setup_workflow(self):
        self.workflow = StateGraph(state_schema=StateManager)

        self.workflow.add_sequence([
            self.db_manager.get_data, 
            self.db_manager.generate_answer
        ])

        self.workflow.add_node("classify_intent", self.classify_intent)
        self.workflow.add_node("model", self.call_model)  

        self.workflow.add_edge(START, "classify_intent")
        self.workflow.add_edge("classify_intent", "get_data")
        self.workflow.add_edge("get_data", "generate_answer")
        self.workflow.add_edge("generate_answer", "model")  

        self.app = self.workflow.compile(checkpointer=self.memory)
        return self.app

    def ask(self, question: str, config: dict, user_id: int, is_sktt:bool = False, result: dict = None):
        
        clean_question = preprocess_text(question)
        
        state = {
            "input": clean_question,
            "context": "",
            "result_query": "" ,
            "answer_query": "",
            "answer": "",
            "current_intent": "",
            "is_sktt": is_sktt,
            "user_id": user_id,
            "result": result,
        }
        print("is_sktt:", state["is_sktt"])
        
        result = self.app.invoke(state, config=config)

        return result["current_intent"], result["answer"]
  