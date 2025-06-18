from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langchain.chains import create_retrieval_chain
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

    def ask(self, question: str, config: dict, user_id: int):
        
        clean_question = preprocess_text(question)
        
        state = {
            "input": clean_question,
            "context": "",
            "result_query": "" ,
            "answer_query": "",
            "answer": "",
            "current_intent": "",
            "user_id": user_id,
        }
        
        result = self.app.invoke(state, config=config)

        return result["current_intent"], result["answer"]
  