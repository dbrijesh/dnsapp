from django import forms
from programs.models import (
    Program, Month, Module, Lesson, Badge, Assessment,
    AssessmentQuestion, OnboardingTemplate
)


class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = ['title', 'description', 'duration_months', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'duration_months': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MonthForm(forms.ModelForm):
    class Meta:
        model = Month
        fields = ['month_number', 'title', 'description', 'learning_objectives']
        widgets = {
            'month_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'learning_objectives': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'module_type', 'order', 'duration_minutes', 'start_month', 'end_month']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'module_type': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_month': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12, 'placeholder': '1-12'}),
            'end_month': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12, 'placeholder': '1-12'}),
        }
        help_texts = {
            'start_month': 'Starting month (1-12) for this module in the program',
            'end_month': 'Ending month (1-12) for this module in the program',
        }


class LessonForm(forms.ModelForm):
    video_file = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    document_file_upload = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    audio_file_upload = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Lesson
        fields = ['title', 'description', 'content_type', 'order', 'duration_minutes',
                  'text_content', 'is_optional']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'content_type': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'text_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'is_optional': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BadgeForm(forms.ModelForm):
    class Meta:
        model = Badge
        fields = ['title', 'description', 'icon', 'color', 'criteria']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., trophy, star, award'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., blue, green, orange'}),
            'criteria': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['title', 'description', 'module', 'is_onboarding']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'module': forms.Select(attrs={'class': 'form-select'}),
            'is_onboarding': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make module optional (can be blank for onboarding assessments)
        self.fields['module'].required = False
        self.fields['module'].label = "Associate with Module"
        self.fields['module'].empty_label = "Select a module (optional for onboarding)"
        self.fields['module'].help_text = "Choose a module to tie this assessment to. Leave blank for onboarding assessments."
        # Order modules by program and start month
        self.fields['module'].queryset = Module.objects.select_related('program').order_by('program__title', 'start_month', 'order')
        # Update other field labels
        self.fields['is_onboarding'].label = "Is Onboarding Assessment"
        self.fields['is_onboarding'].help_text = "Check if this assessment should be used during user onboarding"


class AssessmentQuestionForm(forms.ModelForm):
    class Meta:
        model = AssessmentQuestion
        fields = ['question_text', 'question_type', 'order', 'min_rating', 'max_rating',
                  'min_label', 'max_label', 'choices']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'question_type': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_rating': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_rating': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_label': forms.TextInput(attrs={'class': 'form-control'}),
            'max_label': forms.TextInput(attrs={'class': 'form-control'}),
            'choices': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                              'placeholder': 'JSON array: ["Option 1", "Option 2", "Option 3"]'}),
        }


class OnboardingTemplateForm(forms.ModelForm):
    class Meta:
        model = OnboardingTemplate
        fields = ['pledge_title', 'pledge_content', 'welcome_message', 'self_assessment']
        widgets = {
            'pledge_title': forms.TextInput(attrs={'class': 'form-control'}),
            'pledge_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'welcome_message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'self_assessment': forms.Select(attrs={'class': 'form-select'}),
        }
