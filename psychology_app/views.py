import json
from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from core.permissions import IsPartnerUser, IsCustomerUser
from core.ratelimit import rate_limit_decorator
from core.pagination import CustomPagination
from collections import defaultdict
from django.utils import timezone
from datetime import datetime

from .models import (
    SurveyType, Survey, QuestionType, Question, AnswerSet,
    PublishSurvey, PublishSurveyResult, UserPublishSurveyResult
)
from .serializers import (
    SurveyTypeSerializer, SurveySerializer, SurveyDetailSerializer,
    QuestionTypeSerializer, QuestionSerializer, AnswerSetSerializer,
    PublishSurveySerializer, UserPublishSurveyResultSerializer, QATemplateSerializer, UserSurveyCompletedSerializer, UserSurveyIncompletedSerializer
)


User = get_user_model()

# ==============================================================
# 1. AnswerSetViewSet
# ==============================================================

class AnswerSetViewSet(viewsets.ViewSet):
    permission_classes = [IsPartnerUser]
    def get_queryset(self):
        user = self.request.user

        if hasattr(user, 'partner_profile') and user.partner_profile is not None:
            return AnswerSet.objects.filter(partner=user.partner_profile)
        if hasattr(user, 'organization_profile') and user.organization_profile is not None:
            return AnswerSet.objects.filter(organization=user.organization_profile)
        return AnswerSet.objects.none()

    @rate_limit_decorator(rate='20/m')
    def list(self, request):
        answer_sets = self.get_queryset().filter(activate=True).order_by('-id')
        serializer = AnswerSetSerializer(answer_sets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @rate_limit_decorator(rate='20/m')
    def create(self, request):
        serializer = AnswerSetSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @rate_limit_decorator(rate='20/m')
    def partial_update(self, request, pk=None):
        answer_set = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = AnswerSetSerializer(answer_set, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @rate_limit_decorator(rate='20/m')
    def destroy(self, request, pk=None):
        answer_set = get_object_or_404(self.get_queryset(), pk=pk)
        if answer_set.activate:
            answer_set.activate = False
            answer_set.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==============================================================
# 2. QuestionTypeViewSet
# ==============================================================

class QuestionTypeViewSet(viewsets.ViewSet):
    permission_classes = [IsPartnerUser]

    @rate_limit_decorator(rate='20/m')
    def list(self, request):
        qtypes = QuestionType.objects.filter(activate=True)
        serializer = QuestionTypeSerializer(qtypes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @rate_limit_decorator(rate='20/m')
    def create(self, request):
        serializer = QuestionTypeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @rate_limit_decorator(rate='20/m')
    def partial_update(self, request, pk=None):
        qtype = get_object_or_404(QuestionType, pk=pk)
        serializer = QuestionTypeSerializer(qtype, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @rate_limit_decorator(rate='20/m')
    def destroy(self, request, pk=None):
        qtype = get_object_or_404(QuestionType, pk=pk)
        if qtype.activate:
            qtype.activate = False
            qtype.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==============================================================
# 3. SurveyTypeViewSet
# ==============================================================

class SurveyTypeViewSet(viewsets.ViewSet):
    permission_classes = [IsPartnerUser]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'partner_profile') and user.partner_profile is not None:
            return SurveyType.objects.filter(partner=user.partner_profile)
        if hasattr(user, 'organization_profile') and user.organization_profile is not None:
            return SurveyType.objects.filter(organization=user.organization_profile)
        return SurveyType.objects.none()

    @rate_limit_decorator(rate='20/m')
    def list(self, request):
        survey_types = self.get_queryset().filter(activate=True).order_by('-id')
        serializer = SurveyTypeSerializer(survey_types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @rate_limit_decorator(rate='20/m')
    def create(self, request):
        serializer = SurveyTypeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @rate_limit_decorator(rate='20/m')
    def partial_update(self, request, pk=None):
        survey_type = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = SurveyTypeSerializer(survey_type, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @rate_limit_decorator(rate='20/m')
    def destroy(self, request, pk=None):
        survey_type = get_object_or_404(self.get_queryset(), pk=pk)
        if survey_type.activate:
            survey_type.activate = False
            survey_type.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==============================================================
# 4. QuestionViewSet
# ==============================================================

class QuestionViewSet(viewsets.ViewSet):
    permission_classes = [IsPartnerUser]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'partner_profile') and user.partner_profile is not None:
            return SurveyType.objects.filter(partner=user.partner_profile)
        if hasattr(user, 'organization_profile') and user.organization_profile is not None:
            return SurveyType.objects.filter(organization=user.organization_profile)
        return SurveyType.objects.none()

    @rate_limit_decorator(rate='20/m')
    def list(self, request):
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @rate_limit_decorator(rate='20/m')
    def create(self, request):
        is_many = isinstance(request.data, list)
        serializer = QuestionSerializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @rate_limit_decorator(rate='20/m')
    def partial_update(self, request, pk=None):
        answer_set = get_object_or_404(Question, pk=pk)
        serializer = QuestionSerializer(answer_set, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @rate_limit_decorator(rate='20/m')
    def destroy(self, request, pk=None):
        answer_set = get_object_or_404(Question, pk=pk)
        if answer_set.activate:
            answer_set.activate = False
            answer_set.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==============================================================
# 5. SurveyViewSet (IsPartnerUser)
# ==============================================================

class SurveyViewSet(viewsets.ViewSet):
    permission_classes = [IsPartnerUser]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'partner_profile') and user.partner_profile is not None:
            return Survey.objects.filter(partner=user.partner_profile)
        if hasattr(user, 'organization_profile') and user.organization_profile is not None:
            return Survey.objects.filter(organization=user.organization_profile)
        return Survey.objects.none()

    @rate_limit_decorator(rate='20/m')
    def list(self, request):
        surveys = self.get_queryset().filter(activate=True).order_by('-created_at')
        serializer = SurveySerializer(surveys, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @rate_limit_decorator(rate='20/m')
    def create(self, request):
        serializer = SurveySerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @rate_limit_decorator(rate='20/m')
    def partial_update(self, request, pk=None):
        survey = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = SurveySerializer(survey, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @rate_limit_decorator(rate='20/m')
    def destroy(self, request, pk=None):
        survey = get_object_or_404(self.get_queryset(), pk=pk)
        if survey.activate:
            survey.activate = False
            survey.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==============================================================
# 6. SurveyDetailViewSet (User – lấy chi tiết bài khảo sát)
# ==============================================================

class SurveyDetailViewSet(viewsets.ViewSet):
    permission_classes = [IsCustomerUser]

    @rate_limit_decorator(rate='20/m')
    def retrieve(self, request, pk=None):
        try:
            survey = Survey.objects.prefetch_related('survey_questions__question').get(id=pk)
        except Survey.DoesNotExist:
            return Response({'error': 'Survey not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SurveyDetailSerializer(survey)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ==============================================================
# 7. PublishSurveyViewSet (Staff)
# ==============================================================

class PublishSurveyViewSet(viewsets.ViewSet):
    permission_classes = [IsPartnerUser]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'partner_profile') and user.partner_profile is not None:
            return PublishSurvey.objects.filter(partner=user.partner_profile)
        if hasattr(user, 'organization_profile') and user.organization_profile is not None:
            return PublishSurvey.objects.filter(organization=user.organization_profile)
        return PublishSurvey.objects.none()

    @rate_limit_decorator(rate='20/m')
    def list(self, request):
        publish_surveys = self.get_queryset().order_by('-published_at')
        serializer = PublishSurveySerializer(publish_surveys, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @rate_limit_decorator(rate='20/m')
    def create(self, request):
        serializer = PublishSurveySerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @rate_limit_decorator(rate='20/m')
    def partial_update(self, request, pk=None):
        publish_survey = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = PublishSurveySerializer(publish_survey, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @rate_limit_decorator(rate='20/m')
    def destroy(self, request, pk=None):
        publish_survey = get_object_or_404(self.get_queryset(), pk=pk)
        publish_survey.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # Custom action: lấy kết quả khảo sát cho một PublishSurvey
    @action(detail=True, methods=['get'], url_path='result', url_name='publishsurvey-result')
    @rate_limit_decorator(rate='20/m')
    def result(self, request, pk=None):
        publish_survey = get_object_or_404(self.get_queryset(), pk=pk)
        cache_key = f'publish_survey_result_{pk}'
        cached_data = cache.get(cache_key)
        
        if cached_data is None:
            publish_survey_result = PublishSurveyResult.objects.filter(publish_survey=publish_survey).first()
            if publish_survey_result:
                return Response(publish_survey_result.result, status=status.HTTP_200_OK)
            else:
                return Response(None, status=status.HTTP_200_OK)
        
        return Response(json.loads(cached_data), status=status.HTTP_200_OK)


# ==============================================================
# 8. PublishedSurveyViewSet (User – khảo sát đã công bố)
# ==============================================================

class PublishedSurveyViewSet(viewsets.ViewSet):
    permission_classes = [IsCustomerUser]

    class PublishedSurveyViewSet(viewsets.ViewSet):
        permission_classes = [IsCustomerUser]

        @rate_limit_decorator(rate='20/m')
        def list(self, request): # 'request' argument is passed by DRF
            user = self.request.user

            try:
                customer_profile = user.customer_profile # Hoặc self.request.user.customer_profile
            except User.customer_profile.RelatedObjectDoesNotExist:
                return Response({"detail": "Customer profile không tìm thấy cho người dùng này."}, status=status.HTTP_403_FORBIDDEN)

            partner_of_customer = customer_profile.partner

            if not partner_of_customer:
                return Response(
                    {"detail": "Customer này không được liên kết với bất kỳ Partner nào."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cache_key = f'published_survey_list_customer_{self.request.user.id}_partner_{partner_of_customer.id}'
            cached_data = cache.get(cache_key)

            if cached_data is None:
                published_surveys = PublishSurvey.objects.filter(
                    partner=partner_of_customer,
                    is_finished=False,
                    user_publishsurvey_results__user=self.request.user,
                    user_publishsurvey_results__result__isnull=True
                ).distinct().order_by('-published_at')

                serializer = PublishSurveySerializer(
                    published_surveys,
                    many=True,
                    context={'request': self.request}
                )
                cached_data = serializer.data
                cache.set(cache_key, cached_data, timeout=3600)

            return Response(cached_data, status=status.HTTP_200_OK)


# ===============================================================
# 9. UserPublishSurveyResultViewSet (User – Gửi kết quả làm bài khảo sát)
# ===============================================================

class UserPublishSurveyResultViewSet(viewsets.ViewSet):
    permission_classes = [IsCustomerUser]

    @rate_limit_decorator(rate='20/m')
    def list(self, request):
        user = request.user
        cache_key = f'user_{user.id}_publish_survey_result_list'
        cached_data = cache.get(cache_key)
        if cached_data is None:
            user_survey_results = UserPublishSurveyResult.objects.filter(
                user=user,
                response__isnull=False,
                result__isnull=False
                ).order_by('-finished_at')
            serializer = UserPublishSurveyResultSerializer(user_survey_results, many=True)
            cached_data = serializer.data
            cache.set(cache_key, cached_data, timeout=3600) # 1 hour
        return Response(cached_data, status=status.HTTP_200_OK)

    @rate_limit_decorator(rate='5/m')
    def update(self, request, pk=None):
        user = request.user
        try:
            instance = UserPublishSurveyResult.objects.get(
                user=user, 
                publish_survey_id=pk
            )
        except UserPublishSurveyResult.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserPublishSurveyResultSerializer(
            instance, 
            data=request.data, 
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

# ==============================================================
# 10. UserSurveyCompletionViewSet (Danh sách user hoàn thành bài khảo sát)
# ==============================================================

class UserSurveyCompletedViewSet(viewsets.ViewSet):
    permission_classes = [IsPartnerUser]
    pagination_class = CustomPagination

    @rate_limit_decorator(rate='20/m')
    def retrieve(self, request, pk=None):
        question_type_names = request.query_params.get('question_type_names')
        psychology_level = request.query_params.get('psychology_level')

        partner = request.user.partner_profile

        publish_survey = get_object_or_404(PublishSurvey, pk=pk)
        
        filters = {
            'response__isnull': False,
            'result__isnull': False,
            'user__customer_profile__partner': partner,
        }
        
        user_publishsurvey_results = publish_survey.user_publishsurvey_results.filter(**filters)
        
        if question_type_names and psychology_level:
            question_type_names_list = question_type_names.split(',')
            result_filter = Q()
            for name in question_type_names_list:
                name = name.strip()
                if name:
                    result_filter |= Q(result__contains={name: psychology_level})
            user_publishsurvey_results = user_publishsurvey_results.filter(result_filter)
        
        user_publishsurvey_results = user_publishsurvey_results.order_by('id')
        total_completed = user_publishsurvey_results.count()

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(user_publishsurvey_results, request)
        user_surveycompleted_serializer = UserSurveyCompletedSerializer(paginated_queryset, many=True)
        qa_serializer = QATemplateSerializer(publish_survey)

        paginated_response = paginator.get_paginated_response(user_surveycompleted_serializer.data)
        paginated_response.data['qa_template'] = qa_serializer.data
        paginated_response.data['total_completed'] = total_completed
        return paginated_response
    
# ==============================================================
# 10. UserSurveyIncompletionViewSet (Danh sách user chưa hoàn thành bài khảo sát)
# ==============================================================
class UserSurveyIncompletedViewSet(viewsets.ViewSet):
    permission_classes = [IsPartnerUser]
    pagination_class = CustomPagination

    @rate_limit_decorator(rate='20/m')
    def retrieve(self, request, pk=None):
        partner = request.user.partner_profile
        publish_survey = get_object_or_404(PublishSurvey, pk=pk)

        filters = {
            'response__isnull': True,
            'result__isnull': True,
            'user__customer_profile__partner': partner,
        }
        user_publishsurvey_results = publish_survey.user_publishsurvey_results.filter(**filters).order_by('id')

        total_incompleted = user_publishsurvey_results.count()

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(user_publishsurvey_results, request)
        serializer = UserSurveyIncompletedSerializer(page, many=True)
        paginated_response = paginator.get_paginated_response(serializer.data)
        paginated_response.data['total_incompleted'] = total_incompleted
        return paginated_response


# ============================================================================================
# 10. SurveyCustomerCountViewSet (Thống kê sinh só lượng khach hang tham gia khảo sát
# ============================================================================================

class SurveyCustomerCountViewSet(viewsets.ViewSet):
    """
    Provides statistics on survey participation for a partner user.
    Counts the total number of students invited, how many participated,
    and how many did not, optionally filtered by a date range.
    """
    permission_classes = [IsPartnerUser]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'partner_profile') and user.partner_profile is not None:
            return UserPublishSurveyResult.objects.filter(partner=user.partner_profile)
        if hasattr(user, 'organization_profile') and user.organization_profile is not None:
            return UserPublishSurveyResult.objects.filter(organization=user.organization_profile)
        return UserPublishSurveyResult.objects.none()


    @rate_limit_decorator(rate='20/m')
    def list(self, request):
        """
        Returns an aggregated count of total, participated, and non-participated students.
        
        Query Parameters:
        - `start_date` (YYYY-MM-DD): Filter results from this date onwards.
        - `end_date` (YYYY-MM-DD): Filter results up to this date.
        """
        queryset = self.get_queryset()

        # --- Date Filtering ---
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        try:
            if start_date_str:
                naive_start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
                aware_start_date = timezone.make_aware(naive_start_date, timezone.get_default_timezone())
                queryset = queryset.filter(finished_at__gte=aware_start_date)

            if end_date_str:
                naive_end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
                # Add one day to include all records on the end_date
                aware_end_date = timezone.make_aware(naive_end_date, timezone.get_default_timezone()) + datetime.timedelta(days=1)
                queryset = queryset.filter(finished_at__lt=aware_end_date)
        
        except ValueError:
            return Response(
                {"error": "Invalid date format. Please use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # --- Counting Logic ---
        total_customers_count = queryset.count()

        participated_count = queryset.filter(
            response__isnull=False,
            result__isnull=False
        ).count()
        
        not_participated_count = total_customers_count - participated_count
        
        # --- Prepare Response Data ---
        data = {
            "total_customers": total_customers_count,
            "participated": participated_count,
            "not_participated": not_participated_count
        }

        return Response(data, status=status.HTTP_200_OK)


# =====================================================================================
# 11. PsychologyCustomerViewSet (Thống kê sinh tình trạng tâm lý khách hàng)
# ======================================================================================

class PsychologyCustomerViewSet(viewsets.ViewSet):
    permission_classes = [IsPartnerUser]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'partner_profile') and user.partner_profile is not None:
            return UserPublishSurveyResult.objects.filter(partner=user.partner_profile)
        if hasattr(user, 'organization_profile') and user.organization_profile is not None:
            return UserPublishSurveyResult.objects.filter(organization=user.organization_profile)
        return UserPublishSurveyResult.objects.none()

    @rate_limit_decorator(rate='20/m')
    def list(self, request, pk=None):
        start_date_str = request.query_params.get('start_date')
        question_type_name = request.query_params.get('question_type_name')

        start_date = None
        if start_date_str:
            naive_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            start_date = timezone.make_aware(naive_date)

        queryset = self.get_queryset()

        data = []

        default_levels = {
            'Bình thường': 0,
            'Nhẹ': 0,
            'Trung bình': 0,
            'Nặng': 0,
            'Rất nặng': 0,
        }

        filters = {}
        if start_date:
            filters['finished_at__gte'] = start_date
        if question_type_name:
            filters[f"result__{question_type_name}__isnull"] = False
            
            qs = queryset.filter(**filters)

            level_counts = defaultdict(int, default_levels.copy())

            for record in qs:
                res = record.result
                if res and question_type_name in res:
                    level = res.get(question_type_name)

                    if level in level_counts:
                        level_counts[level] += 1
                    else:
                        level_counts[level] = 1


            data.append({
                "levels": dict(level_counts)
            })

        return Response(data, status=status.HTTP_200_OK)