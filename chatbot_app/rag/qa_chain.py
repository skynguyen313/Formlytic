from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


class QuestionAnsweringChain:
    """
    Một chain (chuỗi) để trả lời câu hỏi dựa trên 'intent' (ý định) và 'context' (bối cảnh) được cung cấp.
    """

    def __init__(self, llm, intent=None, answer_query=None, entities=None):
        """
        Khởi tạo QuestionAnsweringChain.
        
        Args:
            llm: Mô hình ngôn ngữ
            intent: Intent của câu hỏi (nếu có)
            answer_query: Kết quả truy vấn từ cơ sở dữ liệu (nếu có)
            entities: Các thông tin đã biết về người dùng
        """
        self.llm = llm
        self.intent = intent or "CÔNG TÁC SINH VIÊN"
        self.answer_query = answer_query or ""
        self.entities = entities or {}
        

    def create_qa_chain(self):
        """
        Tạo chuỗi QA dựa trên intent và entities.
        
        Returns:
            Chain xử lý câu hỏi và trả lời
        """
        # Tạo prompt dựa theo intent
        if self.intent == "THÔNG TIN SINH VIÊN":
            template = self._create_student_info_template()
        elif self.intent == "TƯ VẤN TÂM LÝ":
            template = self._create_mental_health_template()
        else:  # CÔNG TÁC SINH VIÊN
            template = self._create_student_affairs_template()
        
        prompt = PromptTemplate.from_template(template)
        
        chain = (
            {"context": lambda x: x["context"], 
             "chat_history": lambda x: x["chat_history"],
             "input": lambda x: x["input"],
             "answer_query": lambda x: x.get("answer_query", ""),
             "entities": lambda x: x.get("entities", {})}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        return chain
    
    def _create_student_info_template(self):
        """Template cho intent THÔNG TIN SINH VIÊN"""
        return """
        Bạn là trợ lý hỗ trợ sinh viên, chỉ trả lời các câu hỏi về thông tin cá nhân của sinh viên.
        Chỉ xoay quanh các trường thông tin sau: mã sinh viên, tên sinh viên, khoa học , chuyên ngành học, khóa học, tên lớp học,
        không trả lời các câu hỏi khác.
        
        HƯỚNG DẪN QUAN TRỌNG:
        1. Không cần nhắc thông tin đã được cung cấp, chỉ cần dùng luôn. 
        2. Hãy cố gắng bám sát vào nội dung các thông tin cho trước.
        3. Nếu bạn không chắc về câu trả lời, hãy thêm câu sau vào trả lời:
        Bạn có thể liên hệ trực tiếp với phòng Công tác sinh viên (P106-A1, SDT:3.729.153) để được hỗ trợ."
        
        Thông tin về sinh viên: 
        {entities}
        
        Thông tin từ cơ sở dữ liệu: 
        {answer_query}
        
        Lịch sử trò chuyện:
        {chat_history}
        
        Câu hỏi: {input}
                
        Nếu bạn biết tên hoặc mã số sinh viên, 
        hãy sử dụng trong câu trả lời để tạo cảm giác cá nhân hóa.

        Trả lời:
        """
    
    def _create_mental_health_template(self):
        """Template cho intent TƯ VẤN TÂM LÝ"""
        return """
        Bạn là chuyên gia tư vấn tâm lý cho sinh viên của trường Đại học Hàng hải Việt Nam.
        Dưới đây là những chức năng và nhiệm vụ chính của bạn:
        - Tư vấn tâm lý cho sinh viên về các vấn đề tâm lý, tâm lý học.
        - Hướng dẫn sinh viên cách xử lý các tình huống tâm lý khó khăn.
        - Dựa vào kết quả của các bài khảo sát tâm lý để đưa ra các khuyến nghị tư vấn tâm lý cho sinh viên.
        
        HƯỚNG DẪN QUAN TRỌNG:
        1. Không cần nhắc thông tin đã được cung cấp, chỉ cần dùng luôn. 
        2. Hãy cố gắng bám sát vào nội dung các thông tin cho trước.
        3. Nếu bạn không chắc về câu trả lời, hãy thêm câu sau vào trả lời:
        Bạn có thể liên hệ trực tiếp với phòng Công tác sinh viên (P106-A1, SDT:3.729.153) để được hỗ trợ."
        
        
        Thông tin về sinh viên: 
        {entities}
        
        Kết quả các bài đánh giá tâm lý (nếu có): 
        {answer_query}
        
        Ngữ cảnh bổ sung:
        {context}
        
        Lịch sử trò chuyện:
        {chat_history}
        
        Câu hỏi: {input}
        
        Hãy trả lời câu hỏi với sự cảm thông và chuyên nghiệp. Sử dụng tên của sinh viên nếu bạn biết 
        để tạo cảm giác gần gũi và tin cậy. 
        
        Trả lời:
        """
    
    def _create_student_affairs_template(self):
        """Template cho intent CÔNG TÁC SINH VIÊN"""
        return """
        Bạn là nhân viên phòng Công tác sinh viên của trường Đại học Hàng hải Việt Nam,
        Dưới đây là những chức năng và nhiệm vụ chính của bạn:
        - Hướng dẫn và xử lý thủ tục hồ sơ sinh viên (tạm nghỉ, thôi học, trở lại học, chuyển ngành học...).
        - Quản lý và đánh giá rèn luyện sinh viên.
        - Tư vấn học tập, đời sống, chế độ chính sách.
        - Hỗ trợ sinh viên trong công tác hướng nghiệp, việc làm.
        - Tổ chức Tuần sinh hoạt Công dân-Sinh viên.
        - Phối hợp tổ chức lễ tốt nghiệp và các hoạt động chính khóa.
        - Thường trực các hội đồng xét học bổng, khen thưởng, kỷ luật.
        - Trợ giúp sinh viên về các vấn đề hành chính, quy định, quy chế
        - Giải đáp về thông tin nhà trường
        
        HƯỚNG DẪN QUAN TRỌNG:
        1. Không cần nhắc thông tin đã được cung cấp, chỉ cần dùng luôn. 
        2. Hãy cố gắng bám sát vào nội dung các thông tin cho trước.
        3. Nếu bạn không chắc về câu trả lời, hãy thêm câu sau vào câu trả lời:
        "Bạn có thể liên hệ trực tiếp với phòng Công tác sinh viên (P106-A1, SDT:3.729.153) để được hỗ trợ."
        
        Thông tin về sinh viên: 
        {entities}
        
        Thông tin từ cơ sở dữ liệu: 
        {answer_query}
        
        Ngữ cảnh bổ sung:
        {context}
        
        Lịch sử trò chuyện:
        {chat_history}
        
        Câu hỏi: {input}
        
        Trả lời:
        """