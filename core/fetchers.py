from student_app.models import Student

class StudentPsychologyFetcher:
    def __init__(self, student_id: int):
        self.student_id = student_id

    def get_data(self):
        try:
            student = Student.objects.get(pk=self.student_id)
        except Student.DoesNotExist:
            return None
        
        user = student.user

        if not user:
            return None
        
        survey_results = user.user_publishsurvey_results.order_by('-finished_at')[:3]
        result_data = []
        for survey in survey_results:
            publish_survey = survey.publish_survey
            result_data.append({
                'survey_title': publish_survey.survey_details.get('title'),
                'result': survey.result,
            })
        return result_data

class StudentFetcher:
    def __init__(self, student_id: int):
        self.student_id = student_id

    def get_data(self):
        try:
            student = Student.objects.get(pk=self.student_id)
        except Student.DoesNotExist:
            return None
        student_info = {
            'student_id': student.id,
            'student_name': student.name,
            'department_name': student.department.name,
            'major_name': student.major.name,
            'course_number': student.course.course_number,
            'class_name': student.school_class.class_name,
        }
        return {
            'student_info': student_info
        }


class StudentScoreFetcher:
    def __init__(self, student_id: int):
        self.student_id = student_id

    def get_data(self):
        try:
            student = Student.objects.select_related(
                'department', 'major', 'course', 'school_class'
            ).get(pk=self.student_id)
        except Student.DoesNotExist:
            return None

        student_info = {
            'student_id': student.id,
            'student_name': student.name,
            'department_name': student.department.name,
            'major_name': student.major.name,
            'course_number': student.course.course_number,
            'class_name': student.school_class.class_name,
        }

        student_scores = student.student_scores.all()

        if not student_scores.exists():
            return {
                'student_info': student_info,
                'message': 'Students do not have scores yet.'
            }
        
        scores = [
            {
                'subject_code': student_score.subject.code,
                'subject_name': student_score.subject.name,
                'subject_credit': student_score.subject.credit,
                'academic_year': student_score.semester.academic_year,
                'semester': student_score.semester.term,
                'score_x': student_score.x,
                'score_y': student_score.y,
                'score_z': student_score.z,
                'letter_grade': student_score.letter_grade,
            }
            for student_score in student_scores
        ]
        return {
            'student_info': student_info,
            'student_scores': scores
        }
     