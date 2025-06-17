from .state_manager import StateManager
from core.fetchers import StudentPsychologyFetcher, StudentFetcher, StudentScoreFetcher


class DataManager:
    def __init__(self, llm):
        self.llm = llm
    
    def get_data(self, state: StateManager):
        student_id = state["student_id"]
        intent = state["current_intent"]

        if intent == "THÔNG TIN SINH VIÊN":
           result_query = StudentFetcher(student_id=student_id).get_data()
           return {"result_query": result_query}
        elif intent == "TƯ VẤN TÂM LÝ":
            result_query = StudentPsychologyFetcher(student_id=student_id).get_data()
            return {"result_query": result_query}
        
        else: # CÔNG TÁC SINH VIÊN
            return StudentScoreFetcher(student_id=student_id).get_data()
        
    def generate_answer(self, state: StateManager):
        """Answer question using retrieved information as context and store the result in state."""
        input_question = state.get("input")
        data_result = state.get("result_query")

        prompt = (
            "Given the following user question"
            "and json data result, answer the user question."
            "Note: If question relates to student score, keep the name of fields as is.\n\n"
            f'User Question: {input_question}\n'
            f'Data result: {data_result}\n'
        )
        
        try:
            response = self.llm.invoke(prompt)
            answer = response.content
            return {"answer_query": answer}
        except Exception as e:
            error_msg = f"Error generating answer: {str(e)}"
            state["answer_query"] = error_msg
            return {"answer_query": error_msg}
