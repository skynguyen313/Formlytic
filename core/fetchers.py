from organizers.models import Organization, Partner, Customer


class CustomerPsychologyFetcher:
    def get_data(self):
        result_data = []
        result_data.append({
                'survey_title': 'DASS 21',
                'result': {
                    'Lo âu': 'Trung bình',
                    'Trầm cảm': 'Nhẹ',
                    'Stress': 'Nặng',
                },
        })
        return result_data

class CustomerFetcher:

    def get_data(self):
        
        extra_info = {
            'name': 'Hoàng Đức Long',
            'date_of_birth': '2003-02-2',
            'sex': 'Nam',
            'company': 'Công ty VMU',
            'position': 'Sĩ quan Boong',
        }
        return extra_info