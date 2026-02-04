from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Program(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    duration_months = models.IntegerField(default=12)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'programs'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Month(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='months')
    month_number = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    learning_objectives = models.TextField(blank=True)

    class Meta:
        db_table = 'months'
        ordering = ['month_number']
        unique_together = ['program', 'month_number']

    def __str__(self):
        return f"Month {self.month_number}: {self.title}"


class Module(models.Model):
    MODULE_TYPES = [
        ('behavioral', 'Behavioral'),
        ('technical', 'Technical'),
        ('domain', 'Domain'),
    ]

    # Updated hierarchy: Module now belongs directly to Program
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='modules', null=True, blank=True)
    month = models.ForeignKey(Month, on_delete=models.SET_NULL, related_name='modules', null=True, blank=True)  # Deprecated, kept for backward compatibility

    title = models.CharField(max_length=255)
    description = models.TextField()
    module_type = models.CharField(max_length=20, choices=MODULE_TYPES)
    order = models.IntegerField(default=0)
    duration_minutes = models.IntegerField(default=0)

    # Month range for the module
    start_month = models.IntegerField(default=1, help_text="Starting month (1-12)")
    end_month = models.IntegerField(default=1, help_text="Ending month (1-12)")

    class Meta:
        db_table = 'modules'
        ordering = ['order']

    def __str__(self):
        if self.program:
            month_range = f"M{self.start_month}" if self.start_month == self.end_month else f"M{self.start_month}-{self.end_month}"
            return f"{self.program.title} - {month_range}: {self.title}"
        return self.title

    def get_total_lessons(self):
        return self.lessons.count()

    def get_completion_percentage(self, user):
        total_lessons = self.lessons.count()
        if total_lessons == 0:
            return 0
        completed_lessons = LessonProgress.objects.filter(
            user=user,
            lesson__module=self,
            status='completed'
        ).count()
        return int((completed_lessons / total_lessons) * 100)


class Lesson(models.Model):
    CONTENT_TYPES = [
        ('video', 'Video'),
        ('document', 'Document'),
        ('text', 'Text'),
        ('audio', 'Audio'),
        ('mixed', 'Mixed'),
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    order = models.IntegerField(default=0)
    duration_minutes = models.IntegerField(default=0)

    # Content fields
    text_content = models.TextField(blank=True)
    video_url = models.CharField(max_length=500, blank=True)
    document_file = models.CharField(max_length=500, blank=True)
    audio_file = models.CharField(max_length=500, blank=True)

    is_optional = models.BooleanField(default=False)

    class Meta:
        db_table = 'lessons'
        ordering = ['order']

    def __str__(self):
        return self.title


class LessonProgress(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    progress_percentage = models.IntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Time tracking: record each time user views the lesson
    first_accessed_at = models.DateTimeField(null=True, blank=True)
    last_accessed_at = models.DateTimeField(null=True, blank=True)
    total_time_spent_seconds = models.IntegerField(default=0, help_text="Total time spent in seconds")

    # Admin override
    is_overridden = models.BooleanField(default=False)
    overridden_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='overridden_progress')
    overridden_at = models.DateTimeField(null=True, blank=True)
    override_note = models.TextField(blank=True, help_text="Reason for override")

    class Meta:
        db_table = 'lesson_progress'
        unique_together = ['user', 'lesson']

    def __str__(self):
        return f"{self.user.email} - {self.lesson.title} - {self.status}"

    def get_time_spent_display(self):
        """Return human-readable time spent"""
        if self.total_time_spent_seconds == 0:
            return "0 min"
        minutes = self.total_time_spent_seconds // 60
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if hours > 0:
            return f"{hours}h {remaining_minutes}m"
        return f"{minutes}m"


class ModuleProgress(models.Model):
    """Track completion status at module level"""
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='module_progress')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='progress')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    progress_percentage = models.IntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Admin override
    is_overridden = models.BooleanField(default=False)
    overridden_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='overridden_module_progress')
    overridden_at = models.DateTimeField(null=True, blank=True)
    override_note = models.TextField(blank=True, help_text="Reason for override")

    class Meta:
        db_table = 'module_progress'
        unique_together = ['user', 'module']

    def __str__(self):
        return f"{self.user.email} - {self.module.title} - {self.status}"


class Badge(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    icon = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=20, default='blue')
    criteria = models.TextField(help_text="Description of how to earn this badge")

    class Meta:
        db_table = 'badges'

    def __str__(self):
        return self.title


class UserBadge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_badges'
        unique_together = ['user', 'badge']

    def __str__(self):
        return f"{self.user.email} - {self.badge.title}"


class Assessment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='assessments', null=True, blank=True)
    is_onboarding = models.BooleanField(default=False)

    class Meta:
        db_table = 'assessments'

    def __str__(self):
        return self.title


class AssessmentQuestion(models.Model):
    QUESTION_TYPES = [
        ('rating', 'Rating Scale'),
        ('multiple_choice', 'Multiple Choice'),
        ('text', 'Text Response'),
    ]

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    order = models.IntegerField(default=0)

    # For rating scale questions
    min_rating = models.IntegerField(default=1)
    max_rating = models.IntegerField(default=5)
    min_label = models.CharField(max_length=100, blank=True)
    max_label = models.CharField(max_length=100, blank=True)

    # For multiple choice questions
    choices = models.TextField(blank=True, help_text="JSON array of choices")

    class Meta:
        db_table = 'assessment_questions'
        ordering = ['order']

    def __str__(self):
        return self.question_text[:50]


class AssessmentResponse(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assessment_responses')
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE)
    rating_value = models.IntegerField(null=True, blank=True)
    text_value = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'assessment_responses'
        unique_together = ['user', 'question']

    def __str__(self):
        return f"{self.user.email} - {self.question.question_text[:30]}"


class OnboardingTemplate(models.Model):
    program = models.OneToOneField(Program, on_delete=models.CASCADE, related_name='onboarding_template')
    pledge_title = models.CharField(max_length=255, default="Program Pledge")
    pledge_content = models.TextField()
    welcome_message = models.TextField()
    self_assessment = models.ForeignKey(Assessment, on_delete=models.SET_NULL, null=True, blank=True, related_name='onboarding_programs')

    class Meta:
        db_table = 'onboarding_templates'

    def __str__(self):
        return f"Onboarding for {self.program.title}"


class UserOnboarding(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='onboardings')
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    pledge_accepted = models.BooleanField(default=False)
    pledge_accepted_at = models.DateTimeField(null=True, blank=True)
    assessment_completed = models.BooleanField(default=False)
    assessment_completed_at = models.DateTimeField(null=True, blank=True)
    onboarding_completed = models.BooleanField(default=False)
    onboarding_completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'user_onboardings'
        unique_together = ['user', 'program']

    def __str__(self):
        return f"{self.user.email} - {self.program.title}"


class UserProgramEnrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'user_program_enrollments'
        unique_together = ['user', 'program']

    def __str__(self):
        return f"{self.user.email} - {self.program.title}"

    def get_overall_progress(self):
        """Calculate overall program completion percentage"""
        total_lessons = Lesson.objects.filter(module__program=self.program).count()
        if total_lessons == 0:
            return 0
        completed_lessons = LessonProgress.objects.filter(
            user=self.user,
            lesson__module__program=self.program,
            status='completed'
        ).count()
        return int((completed_lessons / total_lessons) * 100)

    def get_module_progress(self, module):
        """Calculate progress for a specific module"""
        total_lessons = Lesson.objects.filter(module=module).count()
        if total_lessons == 0:
            return 0
        completed_lessons = LessonProgress.objects.filter(
            user=self.user,
            lesson__module=module,
            status='completed'
        ).count()
        return int((completed_lessons / total_lessons) * 100)
