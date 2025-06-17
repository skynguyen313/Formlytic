from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

class IntentClassifier:
    """
    Classifies the intent of a user's question into predefined categories.
    """

    def __init__(self, llm):
        """
        Initializes the IntentClassifier.

        Args:
            llm: The language model to use for intent classification.
        """
        self.llm = llm
        self.router_template = """Hãy xác định lĩnh vực phù hợp nhất cho câu hỏi dưới đây. Chỉ chọn một trong ba lĩnh vực sau và trả lời bằng đúng một từ:

        - "THÔNG TIN SINH VIÊN": Câu hỏi liên quan đến thông tin cá nhân sinh viên như mã sinh viên, tên sinh viên, khoa học, chuyên ngành học, khóa học, tên lớp học.
        - "TƯ VẤN TÂM LÝ": Câu hỏi liên quan đến tâm lý học đường của sinh viên, bao gồm cả bài kiểm tra tâm lý.
        - "CÔNG TÁC SINH VIÊN": Câu hỏi liên quan đến quy định, quy chế, thủ tục học vụ, học phí, học bổng, cơ sở vật chất, hoạt động và thông tin về nhà trường.
        đối với các câu hỏi không liên quan đến các lĩnh vực trên, hãy trả lời: "CÔNG TÁC SINH VIÊN"
        Câu hỏi: {input}
        Lĩnh vực:
        """

        self.router_chain = (
            PromptTemplate.from_template(self.router_template)
            | self.llm
            | StrOutputParser()
        )


    def classify(self, user_input: str) -> str:
        """
        Classifies the user input and returns the intent.

        Args:
            user_input: The user's input question.

        Returns:
            The classified intent (one of the predefined categories).
        """
        try:
            intent = self.router_chain.invoke({"input": user_input})
            
            # Chuẩn hóa kết quả intent
            if "THÔNG TIN SINH VIÊN" in intent:
                return "THÔNG TIN SINH VIÊN"
            elif "TƯ VẤN TÂM LÝ" in intent:
                return "TƯ VẤN TÂM LÝ"
            else:
                return "CÔNG TÁC SINH VIÊN"
        except Exception as e:
            return "CÔNG TÁC SINH VIÊN" 