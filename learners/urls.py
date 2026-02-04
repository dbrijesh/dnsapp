from django.urls import path
from . import views
from . import onboarding_views

app_name = 'learners'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-program/', views.my_program, name='my_program'),
    path('module/<int:module_id>/', views.module_detail, name='module_detail'),
    path('lesson/<int:lesson_id>/', views.lesson_view, name='lesson_view'),
    path('lesson/<int:lesson_id>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    path('lesson/<int:lesson_id>/update-time/', views.update_lesson_time, name='update_lesson_time'),

    # Program selection and enrollment
    path('select-program/', views.select_program, name='select_program'),
    path('enroll/<int:program_id>/', views.enroll_program, name='enroll_program'),

    # Onboarding
    path('onboarding/<int:program_id>/', onboarding_views.onboarding, name='onboarding'),
    path('onboarding/<int:program_id>/pledge/', onboarding_views.accept_pledge, name='accept_pledge'),
    path('onboarding/<int:program_id>/assessment/', onboarding_views.self_assessment, name='self_assessment'),

    # Co-learners
    path('co-learners/', views.co_learners, name='co_learners'),

    # Badges and assessments
    path('badges/', views.badges, name='badges'),
    path('assessments/', views.assessments, name='assessments'),
]
