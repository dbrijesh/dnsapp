from django.urls import path
from . import views

app_name = 'admins'

urlpatterns = [
    # Dashboard
    path('', views.admin_dashboard, name='dashboard'),

    # Program Management
    path('programs/', views.program_list, name='program_list'),
    path('programs/create/', views.program_create, name='program_create'),
    path('programs/<int:program_id>/', views.program_detail, name='program_detail'),
    path('programs/<int:program_id>/edit/', views.program_edit, name='program_edit'),
    path('programs/<int:program_id>/delete/', views.program_delete, name='program_delete'),

    # Month Management
    path('programs/<int:program_id>/months/create/', views.month_create, name='month_create'),
    path('months/<int:month_id>/', views.month_detail, name='month_detail'),
    path('months/<int:month_id>/edit/', views.month_edit, name='month_edit'),

    # Module Management
    path('programs/<int:program_id>/modules/create/', views.module_create, name='module_create'),
    path('modules/<int:module_id>/', views.module_detail, name='module_detail'),
    path('modules/<int:module_id>/edit/', views.module_edit, name='module_edit'),

    # Lesson Management
    path('modules/<int:module_id>/lessons/create/', views.lesson_create, name='lesson_create'),
    path('lessons/<int:lesson_id>/edit/', views.lesson_edit, name='lesson_edit'),

    # Badge Management
    path('badges/', views.badge_list, name='badge_list'),
    path('badges/create/', views.badge_create, name='badge_create'),
    path('badges/<int:badge_id>/edit/', views.badge_edit, name='badge_edit'),

    # Assessment Management
    path('assessments/', views.assessment_list, name='assessment_list'),
    path('assessments/create/', views.assessment_create, name='assessment_create'),
    path('assessments/<int:assessment_id>/', views.assessment_detail, name='assessment_detail'),
    path('assessments/<int:assessment_id>/edit/', views.assessment_edit, name='assessment_edit'),
    path('assessments/<int:assessment_id>/questions/create/', views.question_create, name='question_create'),
    path('assessments/<int:assessment_id>/responses/', views.assessment_responses, name='assessment_responses'),

    # Onboarding Template Management
    path('programs/<int:program_id>/onboarding/create/', views.onboarding_template_create, name='onboarding_template_create'),
    path('onboarding/<int:template_id>/edit/', views.onboarding_template_edit, name='onboarding_template_edit'),

    # Participant Progress Tracking
    path('participants/', views.participant_list, name='participant_list'),
    path('participants/<int:user_id>/', views.participant_progress, name='participant_progress'),
    path('participants/<int:user_id>/lessons/<int:lesson_id>/override/', views.override_lesson_completion, name='override_lesson'),
    path('participants/<int:user_id>/modules/<int:module_id>/override/', views.override_module_completion, name='override_module'),
]
