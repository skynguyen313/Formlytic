
from .state_manager import StateManager
from core.fetchers import CustomerPsychologyFetcher, CustomerFetcher


class DataManager:
    def __init__(self, llm):
        self.llm = llm
    
    def get_data(self, state: StateManager):
        intent = state["current_intent"]

        if intent == "0":
           result_query = CustomerFetcher().get_data()           
           return {"result_query": result_query}
        elif intent == "1":
            # result_query = CustomerPsychologyFetcher().get_data()
            result_query = state["result"]
            return {"result_query": result_query}
        
        
    def generate_answer(self, state: StateManager):
        """Answer question using retrieved information as context and store the result in state."""
        input_question = state.get("input")
        data_result = state.get("result")

        prompt = (
            "Given the following user question"
            "and json data result, summarize the data result in a concise way"
            "Note: If question relates to student score, keep the name of fields as is.\n\n"
            f'User Question: {input_question}\n'
            f'Data result: {data_result}\n'
        )
        
        try:
            response = self.llm.invoke(prompt)
            answer = response.content
            print("[D]answer:", answer)
            return {"answer_query": answer}
        except Exception as e:
            error_msg = f"Error generating answer: {str(e)}"
            state["answer_query"] = error_msg
            return {"answer_query": error_msg}
