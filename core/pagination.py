from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status

class CustomPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        if 'page' not in request.query_params:
            self.page = list(queryset)
            self.request = request
            return self.page
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        if hasattr(self.page, 'paginator'):
            total_pages = self.page.paginator.num_pages
            count = self.page.paginator.count
            next_link = self.get_next_link()
            previous_link = self.get_previous_link()
        else:
            total_pages = 1
            count = len(self.page)
            next_link = None
            previous_link = None

        return Response({
            'links': {
                'next': next_link,
                'previous': previous_link
            },
            'total_pages': total_pages,
            'count': count,
            'results': data
        }, status=status.HTTP_200_OK)
