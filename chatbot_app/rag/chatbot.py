from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langchain.chains import create_retrieval_chain
from .llm_model import get_openai_llm
from .vector_db import VectorDB
from .contextual_retriever import ContextualRetriever
from .qa_chain import QuestionAnsweringChain
from .state_manager import StateManager
from .entity_manager import EntityManager
from .intent_classifier import IntentClassifier
from .data_manager import DataManager


class Chatbot:
    def __init__(self):
        self.llm = get_openai_llm()
       
        self.vector_db = VectorDB() 
        self.retriever = self.vector_db.get_retriever()
        self.contextual_retriever = ContextualRetriever(self.llm, self.retriever).get_history_aware_retriever()
        self.db_manager = DataManager(self.llm)
        self.qa_chain = QuestionAnsweringChain(self.llm).create_qa_chain()
        
        # Tạo retrieval-augmented generation (RAG) chain
        self.rag_chain = create_retrieval_chain(self.contextual_retriever, self.qa_chain)
        
        # Khởi tạo bộ nhớ
        self.memory = MemorySaver()

        self.intent_classifier = IntentClassifier(self.llm)
        self.entity_manager = EntityManager(self.llm)

    def reset(self):
        """Reset all components of the chatbot."""
        self.llm = get_openai_llm()
        self.vector_db = VectorDB()
        self.retriever = self.vector_db.get_retriever()
        self.contextual_retriever = ContextualRetriever(self.llm, self.retriever).get_history_aware_retriever()
        self.db_manager = DataManager(self.llm)
        self.qa_chain = QuestionAnsweringChain(self.llm).create_qa_chain()
        
        # Rebuild retrieval-augmented generation (RAG) chain
        self.rag_chain = create_retrieval_chain(self.contextual_retriever, self.qa_chain)
        
        # Re-initialize memory saver
        self.memory = MemorySaver()

        self.intent_classifier = IntentClassifier(self.llm)
        self.entity_manager = EntityManager(self.llm)

    def classify_intent(self, state: StateManager):
        question = state["input"]
        
        intent = self.intent_classifier.classify(question)
        state["current_intent"] = intent
        
        return state

    def manage_entities(self, state: StateManager):
        thread_id = state.get("thread_id", "default")
        chat_history = state.get("chat_history", [])

        if not chat_history:
            chat_history.append(HumanMessage(state["input"]))

        messages = []
        for msg in chat_history:
            msg_type = "human" if isinstance(msg, HumanMessage) else "ai"
            messages.append({"type": msg_type, "content": msg.content})

        new_entities = self.entity_manager.extract_entities(messages)
        
        # Ưu tiên student_id từ state nếu có
        if state.get("student_id"):
            new_entities["student_id"] = state["student_id"]

        self.entity_manager.update_entities(thread_id, new_entities)
        entities = self.entity_manager.get_entities(thread_id)
        state["entities"] = entities
 
        return state

    
    def call_model(self, state: StateManager):
        question = state["input"]
        id_file_filter = state["id_file_filter"]
        current_intent = state.get("current_intent", "CÔNG TÁC SINH VIÊN")
        thread_id = state.get("thread_id", "default")
        
        entities = state.get("entities", {})
        
        enriched_question = self.entity_manager.enrich_question(question, thread_id)
        
        answer_query = state["answer_query"]

        # Xử lý đặc biệt cho intent THÔNG TIN SINH VIÊN
        if current_intent == "THÔNG TIN SINH VIÊN":
            self.qa_chain = QuestionAnsweringChain(
                self.llm, 
                current_intent, 
                answer_query,
                entities=entities
            ).create_qa_chain()
            
            # Gọi trực tiếp qa_chain mà không cần retriever
            response = self.qa_chain.invoke({
                "input": enriched_question,
                "chat_history": state.get("chat_history", []),
                "context": "",  # Context trống vì không cần tài liệu
                "answer_query": answer_query,
                "entities": entities
            })
            
            return {
                "chat_history": [
                    HumanMessage(state["input"]),
                    AIMessage(response),
                ],
                "context": "",
                "answer": response,
                "current_intent": current_intent,
                "entities": entities,
            }

        # Xử lý các intent khác như bình thường
        relevant_docs = self.retriever.invoke(enriched_question)

        if id_file_filter:
            relevant_docs = [doc for doc in relevant_docs if doc.metadata.get("id", "") == id_file_filter]

        if not relevant_docs:
            relevant_docs = [doc for doc in self.retriever.invoke(question) if doc.metadata.get("id", "") == 'K']

        if relevant_docs:
            temp_retriever = VectorDB().get_retriever()
            self.contextual_retriever = ContextualRetriever(self.llm, temp_retriever).get_history_aware_retriever()
            self.qa_chain = QuestionAnsweringChain(
                self.llm, 
                current_intent, 
                answer_query,
                entities=entities
            ).create_qa_chain()

            self.rag_chain = create_retrieval_chain(self.contextual_retriever, self.qa_chain)
        else:
            entity_info = "\n".join([f"{k}: {v}" for k, v in entities.items()]) if entities else ""
            prompt = f"""
            Tôi không tìm thấy thông tin phù hợp cho câu hỏi của bạn. 

            Thông tin người dùng:
            {entity_info}

            Câu hỏi: {question}

            Với thông tin hiện có, hãy trả lời câu hỏi một cách lịch sự và đề nghị người dùng cung cấp thêm thông tin nếu cần.
            """
            fallback_response = self.llm.invoke(prompt).content

            return {
                "chat_history": [
                    HumanMessage(state["input"]),
                    AIMessage(fallback_response),
                ],
                "context": "",
                "answer": fallback_response,
                "current_intent": current_intent,
                "entities": entities,
            }

        state_with_entities = {**state, "entities": entities}
        response = self.rag_chain.invoke(state_with_entities)

        return {
            "chat_history": [
                HumanMessage(state["input"]),
                AIMessage(response["answer"]),
            ],
            "context": response["context"],
            "answer": response["answer"],
            "current_intent": current_intent,
            "entities": entities,
        }


    def setup_workflow(self):
        self.workflow = StateGraph(state_schema=StateManager)

        self.workflow.add_sequence([
            self.db_manager.get_data, 
            self.db_manager.generate_answer
        ])

        self.workflow.add_node("classify_intent", self.classify_intent)
        self.workflow.add_node("manage_entities", self.manage_entities)
        self.workflow.add_node("model", self.call_model)  

        self.workflow.add_edge(START, "classify_intent")
        self.workflow.add_edge("classify_intent", "manage_entities")
        self.workflow.add_edge("manage_entities", "get_data")
        self.workflow.add_edge("get_data", "generate_answer")
        self.workflow.add_edge("generate_answer", "model")  

        self.app = self.workflow.compile(checkpointer=self.memory)
        return self.app

    def ask(self, question: str, config: dict, id_file_filter: str = None, student_id: str = None):
        thread_id = config.get("configurable", {}).get("thread_id", "default")
        self.entity_manager.register_thread(thread_id)
        
        state = {
            "input": question,
            "chat_history": [],
            "thread_id": thread_id,
            "context": "",
            
            "id_file_filter": id_file_filter,
            "student_id": student_id,
            "result_query": "" ,
            "answer_query": "",
            "answer": "",
            "current_intent": "CÔNG TÁC SINH VIÊN",
            "entities": {}
        }
        
        result = self.app.invoke(state, config=config)

        return result["current_intent"], result["answer"]