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
        self.router_template = """Hãy xác định ý định phù hợp nhất cho câu hỏi dưới đây. Chỉ chọn một trong hai lĩnh vực sau và trả lời bằng đúng một từ:

        - "TTND": Khi người dùng muốn tra cứu thông tin cá nhân của người dùng khi đăng ký hệ thống.
        - "HTGD": Khi người dùng muốn đặt câu hỏi, được giải đáp thắc mắc trên lĩnh vực của họ.
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
            if "TTND" in intent:
                return "0"
            elif "HTGD" in intent:
                return "1"
        except Exception as e:
            return "1" 