from rest_framework import serializers
from .models import (SurveyType,
                     QuestionType,
                     AnswerSet,
                     Survey,
                     PublishSurvey,
                     Question,
                     SurveyQuestion,
                     UserPublishSurveyResult
                    )
from django.contrib.auth import get_user_model

User = get_user_model()


class AnswerSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerSet
        fields = ['id', 'name', 'answers', 'scores']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user

        # 1. Nếu user là owner của một Partner
        if hasattr(user, 'partner_profile') and user.partner_profile is not None:
            partner_obj = user.partner_profile
            validated_data['partner'] = partner_obj
            # Đồng thời gán organization dựa trên partner.organ ization
            validated_data['organization'] = partner_obj.organization

        # 2. Nếu user là owner của một Organization
        elif hasattr(user, 'organization_profile') and user.organization_profile is not None:
            org_obj = user.organization_profile
            validated_data['organization'] = org_obj
            # partner để mặc định là None (trong model cho phép null=True, blank=True)

        else:
            raise serializers.ValidationError(
                "User này chưa được gán Organization hay Partner."
            )

        return super().create(validated_data)

class QuestionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionType
        fields = ['symbol', 'name']
        extra_kwargs = {
            'symbol': {'validators': []},
        }
    
    def create(self, validated_data):
        symbol = validated_data.get('symbol')
        question_type = QuestionType.objects.filter(symbol=symbol).first()
        
        if question_type:
            if question_type.activate:
                raise serializers.ValidationError({
                    'symbol': ['QuestionType with symbol already exists.']
                })
            question_type.activate = True
            question_type.name = validated_data.get('name', question_type.name)
            question_type.save()
            return question_type
        
        return super().create(validated_data)


class SurveyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyType
        fields = ['id', 'name']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user

        # 1. Nếu user là owner của một Partner
        if hasattr(user, 'partner_profile') and user.partner_profile is not None:
            partner_obj = user.partner_profile
            validated_data['partner'] = partner_obj
            validated_data['organization'] = partner_obj.organization

        # 2. Nếu user là owner của một Organization
        elif hasattr(user, 'organization_profile') and user.organization_profile is not None:
            org_obj = user.organization_profile
            validated_data['organization'] = org_obj

        else:
            raise serializers.ValidationError(
                "User này chưa được gán Organization hay Partner."
            )

        return super().create(validated_data)


class QuestionSerializer(serializers.ModelSerializer):
    question_type_name = serializers.CharField(source='question_type.name', read_only=True)
    class Meta:
        model = Question
        fields = ['id', 'question_type', 'question_type_name', 'text']


class SurveySerializer(serializers.ModelSerializer):
    questions = serializers.PrimaryKeyRelatedField(  
        queryset=Question.objects.all(),
        many=True,
        write_only=True,
        default=[] 
    )
    answer_set = serializers.PrimaryKeyRelatedField(
        queryset=AnswerSet.objects.all(),
        write_only=True
    )
    evaluate = serializers.JSONField(write_only=True)

    class Meta:
        model = Survey
        fields = ['id', 'survey_type', 'title', 'description', 'answer_set', 'evaluate', 'created_at', 'questions']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user

        partner_obj = None
        if hasattr(user, 'partner_profile') and user.partner_profile is not None:
            partner_obj = user.partner_profile
        
        organization_obj = None
        if hasattr(user, 'organization_profile') and user.organization_profile is not None:
            organization_obj = user.organization_profile

        validated_data['partner'] = partner_obj
        validated_data['organization'] = organization_obj

        questions = validated_data.pop('questions', None)
        survey = Survey.objects.create(**validated_data)

        if questions:
            survey_questions_to_create = [
                SurveyQuestion(survey=survey, question=question)
                for question in questions
            ]
            SurveyQuestion.objects.bulk_create(survey_questions_to_create)
            
        return survey
    
    def update(self, instance, validated_data):
        questions = validated_data.pop('questions', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if questions is not None:
            new_question_ids = set(q.id for q in questions)
            current_survey_questions = instance.survey_questions.all()
            current_question_ids = set(sq.question.id for sq in current_survey_questions)

            for survey_question in current_survey_questions:
                if survey_question.question.id not in new_question_ids:
                    survey_question.question.delete()

            for question in questions:
                if question.id not in current_question_ids:
                    SurveyQuestion.objects.create(survey=instance, question=question)

        return instance


class SurveyQuestionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = SurveyQuestion
        fields = ['id', 'question']

class SurveyDetailSerializer(serializers.ModelSerializer):
    answer_set = AnswerSetSerializer(read_only=True)
    survey_questions = SurveyQuestionSerializer(many=True, read_only=True)
    class Meta:
        model = Survey
        fields = ['id', 'survey_type', 'title', 'answer_set', 'description', 'evaluate', 'created_at', 'survey_questions']


class PublishSurveySerializer(serializers.ModelSerializer):
    survey = serializers.PrimaryKeyRelatedField(queryset=Survey.objects.all(), write_only=True)
    survey_details = serializers.JSONField(read_only=True)

    class Meta:
        model = PublishSurvey
        fields = ['id', 'survey', 'survey_details', 'published_at', 'expired_at', 'is_finished', 'target']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            survey = validated_data.pop('survey', None)
            if survey:
                serialized_survey = SurveyDetailSerializer(survey).data
                validated_data['survey_details'] = serialized_survey
            user = request.user
            if hasattr(user, 'partner_profile') and user.partner_profile is not None:
                partner_obj = user.partner_profile
                validated_data['partner'] = partner_obj
                validated_data['organization'] = partner_obj.organization

            # 2. Nếu user là owner của một Organization
            elif hasattr(user, 'organization_profile') and user.organization_profile is not None:
                org_obj = user.organization_profile
                validated_data['organization'] = org_obj

            else:
                raise serializers.ValidationError(
                    "User này chưa được gán Organization hay Partner."
                )
        return super().create(validated_data)


class UserPublishSurveyResultSerializer(serializers.ModelSerializer): 
    survey_title = serializers.SerializerMethodField()
    
    class Meta:
        model = UserPublishSurveyResult
        fields = ['id', 'survey_title', 'response', 'result', 'finished_at']
        
    def get_survey_title(self, obj):
        return obj.publish_survey.survey_details.get('title', None)
    
    def create(self, validated_data):
        """
        Overrides the default create method to automatically populate the
        `organization` and `partner` fields from the request user.
        """
        # Get the user from the serializer's context, which is passed by the ViewSet.
        user = self.context['request'].user
        
        organization = None
        partner = None

        # Determine if the user is a Partner or an Organization owner.
        # A Partner has higher precedence.
        if hasattr(user, 'partner_profile'):
            partner = user.partner_profile
            organization = partner.organization # A partner always belongs to an organization.
        elif hasattr(user, 'organization_profile'):
            organization = user.organization_profile
            
        # Add the determined organization and partner to the validated data.
        validated_data['organization'] = organization
        validated_data['partner'] = partner
        
        # Call the parent's create method to save the instance to the database.
        return super().create(validated_data)

class QATemplateSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField(read_only=True)
    answers = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = PublishSurvey
        fields = ['questions', 'answers']

    def get_questions(self, obj):
        survey_details = obj.survey_details or {}
        return survey_details.get('survey_questions')
    
    def get_answers(self, obj):
        survey_details = obj.survey_details or {}
        answer_set = survey_details.get('answer_set', {})
        return answer_set.get('answers')
    
class CustomerUserSerializer(serializers.ModelSerializer):
    extra_info = serializers.JSONField(source='customer_profile.extra_info', read_only=True)

    class Meta:
        model = User
        fields = [
            'extra_info'
        ]

class UserSurveyCompletedSerializer(serializers.ModelSerializer):
    customer = CustomerUserSerializer(source='user', read_only=True)
    class Meta:
        model = UserPublishSurveyResult
        fields = ['customer', 'response', 'result', 'finished_at']


class UserSurveyIncompletedSerializer(serializers.ModelSerializer):
    customer = CustomerUserSerializer(source='user', read_only=True)
    class Meta:
        model = UserPublishSurveyResult
        fields = ['customer']