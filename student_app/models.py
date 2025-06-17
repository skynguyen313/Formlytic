from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model


User = get_user_model()


class Course(models.Model):
    course_number = models.PositiveIntegerField(default=0)
    start_year = models.PositiveIntegerField(default=0)
    activate = models.BooleanField(default=True)
    class Meta:
        db_table = 'student_course'

class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)
    activate = models.BooleanField(default=True)
    class Meta:
        db_table = 'student_department'


class Major(models.Model):
    name = models.CharField(max_length=255, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='majors')
    activate = models.BooleanField(default=True)
    class Meta:
        db_table = 'student_major'


class SchoolClass(models.Model):
    class_name = models.CharField(max_length=255, unique=True)
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='classes')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='classes')
    activate = models.BooleanField(default=True)
    class Meta:
        db_table = 'student_class'


class Student(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    sex = models.BooleanField(default=False)
    dob  = models.DateField()
    email = models.EmailField(max_length=255, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='students')
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='students')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='students')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='students')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student', null=True, blank=True)
    class Meta:
        db_table = 'student_student'

class Subject(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    credit = models.PositiveSmallIntegerField(default=1)
    activate = models.BooleanField(default=True)
    class Meta:
        db_table = 'student_subject'

class Semester(models.Model):
    TERM_CHOICES = [
        (1, "Semester 1"),
        (2, "Semester 2"),
        (3, "Extra semester"),
    ]
    
    start_year = models.PositiveIntegerField(default=0)
    term = models.PositiveSmallIntegerField(choices=TERM_CHOICES)
    activate = models.BooleanField(default=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['start_year', 'term'], name='unique_year_semester'
            )
        ]
        db_table ='student_semester'

    @property
    def end_year(self):
        return self.start_year + 1
    
    @property
    def academic_year(self):
        return f"{self.start_year} - {self.end_year}"
    

class StudentScore(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, related_name='student_scores', null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='student_scores')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='student_scores')
    grading_formula = models.CharField(max_length=255)
    x = models.FloatField(default=0.0)
    y = models.FloatField(default=0.0)
    z = models.FloatField(default=0.0)
    letter_grade = models.CharField(max_length=5)
    class Meta:
        db_table = 'student_score'


class LevelAlert(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, related_name='levelalerts', null=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='levelalerts')
    level = models.SmallIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(3)])
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'semester'], name='unique_student_semesterlevel'
            )
        ]
        db_table = 'student_levelalert'


class TuitionAlert(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, related_name='tuitionalerts', null=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='tuitionalerts')
    tuition = models.BooleanField(default=False)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'semester'], name='unique_student_semestertuition'
            )
        ]
        db_table = 'student_tuitionalert'