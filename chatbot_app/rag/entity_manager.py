import json, re
from typing import Dict, Any, List


class EntityManager:
    """
    Quản lý các entity (thông tin) trích xuất từ cuộc hội thoại.
    Giúp duy trì ngữ cảnh giữa các intent khác nhau.
    """
    def __init__(self, llm):
        """
        Khởi tạo EntityManager.
        
        Args:
            llm: Mô hình ngôn ngữ để trích xuất thông tin
        """
        self.llm = llm
        self.entity_store = {}
        self.active_threads = set()
    
    def extract_entities(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Trích xuất các thực thể từ lịch sử tin nhắn.
        
        Args:
            messages: Danh sách các tin nhắn trong cuộc hội thoại
            
        Returns:
            Dict các entity đã trích xuất được
        """
        # Chuyển đổi messages thành văn bản
        conversation = "\n".join([
            f"{'User' if msg.get('type', '') == 'human' else 'Bot'}: {msg.get('content', '')}" 
            for msg in messages
        ])
        
        prompt = f"""
        Phân tích đoạn hội thoại sau và trích xuất các thông tin quan trọng:
        {conversation}
        
        Trả về kết quả chỉ dưới dạng JSON với các trường sau (chỉ bao gồm các trường có thông tin):
        - student_name: Tên của sinh viên
        - student_id: Mã số sinh viên
        - department_name: Khoa
        - major_name: Chuyên ngành
        - course_number: Khóa học
        - class_name: Tên lớp học
        - other_info: Thông tin quan trọng khác
        
        Chỉ trả về JSON thuần, không kèm thêm bất kỳ nội dung nào khác.
        """
        
        try:
            
            response = self.llm.invoke(prompt)
             
            # Kiểm tra nếu response có thuộc tính 'content', nếu không, sử dụng trực tiếp
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = response
            
            # Trích xuất phần JSON
            json_str = self._extract_json_from_response(content)
            
            entities = json.loads(json_str)
            return entities
        except Exception as e:
            return {}
        
    def _extract_json_from_response(self, response: str) -> str:
        """
        Trích xuất phần JSON từ phản hồi của LLM với cải tiến để xử lý các trường hợp phức tạp.
        """
        
        # Tìm cặp ngoặc nhọn đầu tiên và cuối cùng
        start_idx = response.find('{')
        end_idx = response.rfind('}')  # Tìm dấu ngoặc nhọn cuối cùng
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            potential_json = response[start_idx:end_idx+1]
            try:
                # Thử parse xem có phải JSON hợp lệ không
                json.loads(potential_json)
                return potential_json
            except json.JSONDecodeError:
                pass
                    
        # Phương pháp thay thế nếu không tìm thấy JSON hợp lệ
        # Sử dụng regex đơn giản để tìm chuỗi JSON
        json_pattern = r"\{.*\}"
        matches = re.findall(json_pattern, response, re.DOTALL)
        
        for match in matches:
            try:
                json.loads(match)
                return match
            except json.JSONDecodeError:
                continue
            
        return "{}"
    
    def get_entities(self, thread_id: str) -> Dict[str, Any]:
        """
        Lấy các entity đã lưu trữ cho một thread.
        
        Args:
            thread_id: ID của thread hội thoại
            
        Returns:
            Dict các entity đã lưu trữ
        """
        entities = self.entity_store.get(thread_id, {})
        
        return entities
            
    def update_entities(self, thread_id: str, new_entities: Dict[str, Any], overwrite: bool = False):
        """
        Cập nhật thông tin entity cho một thread cụ thể.
        
        Args:
            thread_id: ID của thread hội thoại
            new_entities: Dict các entity mới
            overwrite: Nếu True, ghi đè toàn bộ; nếu False, chỉ cập nhật các giá trị không trống
        """
        if thread_id not in self.entity_store:
            self.entity_store[thread_id] = {}
        
        old_entities = self.entity_store[thread_id].copy()
            
        if overwrite:
            # Ghi đè hoàn toàn
            self.entity_store[thread_id] = new_entities
        else:
            # Chỉ cập nhật các giá trị không trống
            for key, value in new_entities.items():
                if value is not None and (not isinstance(value, str) or value.strip()):
                    self.entity_store[thread_id][key] = value
        

    def clear_thread_entities(self, thread_id: str) -> None:
        """
        Xóa toàn bộ entities cho một thread cụ thể.
        
        Args:
            thread_id: ID của thread hội thoại cần xóa
        """
        if thread_id in self.entity_store:
            del self.entity_store[thread_id]

    
    def register_thread(self, thread_id: str) -> None:
        """
        Đăng ký một thread mới và xóa entities cũ nếu thread này đã tồn tại.
        
        Args:
            thread_id: ID của thread hội thoại
        """
        if thread_id in self.active_threads:
            # Thread đã tồn tại trước đó, xóa entities cũ
            self.clear_thread_entities(thread_id)
        else:
            # Thread mới, thêm vào danh sách theo dõi
            self.active_threads.add(thread_id)
            
    
    def enrich_question(self, question: str, thread_id: str) -> str:
        """
        Làm phong phú câu hỏi với thông tin từ entities đã lưu trữ.
        
        Args:
            question: Câu hỏi gốc
            thread_id: ID của thread hội thoại
            
        Returns:
            Câu hỏi đã được làm phong phú
        """
        entities = self.get_entities(thread_id)
        
        if not entities:
            return question
            
        prompt = f"""
        Dưới đây là thông tin về người dùng:
        {json.dumps(entities, ensure_ascii=False)}
        
        Và đây là câu hỏi của họ:
        {question}
        
        Hãy làm phong phú câu hỏi này bằng cách thêm các thông tin liên quan từ thông tin người dùng, 
        nhưng chỉ khi phù hợp và cần thiết để hiểu rõ hơn về câu hỏi.
        Ví dụ, nếu câu hỏi hỏi về "điểm của tôi" và chúng ta biết tên và mã sinh viên, 
        hãy thêm thông tin đó vào câu hỏi.
        
        Câu hỏi đã làm phong phú:
        """
        
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            return question 