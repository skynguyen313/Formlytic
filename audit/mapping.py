from student_app.models import Department, Major, Course, SchoolClass
from psychology_app.models import SurveyType, QuestionType, AnswerSet, Survey, PublishSurvey
from notify_app.models import Notification
from chatbot_app.models import FAQ, Document

MODEL_MAPPING = {
    'Department': Department,
    'Major': Major,
    'Course': Course,
    'SchoolClass': SchoolClass,

    'SurveyType': SurveyType,
    'QuestionType': QuestionType,
    'AnswerSet': AnswerSet,
    'Survey': Survey,
    'PublishSurvey': PublishSurvey,

    'Notification': Notification,

    'FAQ': FAQ,
    'Document': Document
}



MODEL_NAME_MAPPING = {
    'Department': 'Khoa',
    'Major': 'Ngành',
    'Course': 'Khóa học',
    'SchoolClass': 'Lớp học',

    'SurveyType': 'Loại khảo sát',
    'QuestionType': 'Loại câu hỏi',
    'AnswerSet': 'Bộ câu trả lời',
    'Survey': 'Bài khảo sát',
    'PublishSurvey': 'Bài đăng',

    'Notification': 'Thông báo',

    'FAQ': 'Câu hỏi thường gặp',
    'Document': 'Tài liệu'
}
