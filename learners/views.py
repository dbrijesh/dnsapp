from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from django.http import JsonResponse
from programs.models import (
    Program, Module, Lesson, LessonProgress, ModuleProgress,
    UserProgramEnrollment, UserOnboarding, UserBadge,
    Assessment, AssessmentResponse
)
from accounts.models import User
from core.storage import course_storage


@login_required
def dashboard(request):
    """Learner dashboard with progress metrics and module view"""
    # Get user's active enrollment
    enrollment = UserProgramEnrollment.objects.filter(
        user=request.user,
        is_active=True
    ).first()

    if not enrollment:
        # Check if user needs onboarding
        return redirect('learners:select_program')

    program = enrollment.program

    # Check onboarding status
    onboarding = UserOnboarding.objects.filter(
        user=request.user,
        program=program
    ).first()

    if onboarding and not onboarding.onboarding_completed:
        return redirect('learners:onboarding', program_id=program.id)

    # Calculate metrics
    overall_progress = enrollment.get_overall_progress()
    total_lessons = Lesson.objects.filter(module__program=program).count()
    completed_lessons = LessonProgress.objects.filter(
        user=request.user,
        lesson__module__program=program,
        status='completed'
    ).count()

    badges_earned = UserBadge.objects.filter(user=request.user).count()

    # Get upcoming tasks (lessons in progress or not started, ordered by module)
    upcoming_lessons = LessonProgress.objects.filter(
        user=request.user,
        lesson__module__program=program,
        status__in=['not_started', 'in_progress']
    ).select_related('lesson', 'lesson__module')[:5]

    # Get module progress
    modules = Module.objects.filter(program=program).order_by('start_month', 'order')
    module_progress_data = []

    for module in modules:
        module_lessons = Lesson.objects.filter(module=module).count()
        module_completed_lessons = LessonProgress.objects.filter(
            user=request.user,
            lesson__module=module,
            status='completed'
        ).count()

        progress = int((module_completed_lessons / module_lessons * 100)) if module_lessons > 0 else 0
        status = 'completed' if progress == 100 else ('in_progress' if progress > 0 else 'not_started')

        module_progress_data.append({
            'module': module,
            'progress': progress,
            'status': status,
            'lessons_total': module_lessons,
            'lessons_completed': module_completed_lessons,
        })

    context = {
        'program': program,
        'overall_progress': overall_progress,
        'total_lessons': total_lessons,
        'completed_lessons': completed_lessons,
        'badges_earned': badges_earned,
        'upcoming_lessons': upcoming_lessons,
        'module_progress_data': module_progress_data,
        'onboarding_complete': onboarding.onboarding_completed if onboarding else False,
    }

    return render(request, 'learners/dashboard.html', context)


@login_required
def my_program(request):
    """Display all modules with lessons in one view"""
    enrollment = UserProgramEnrollment.objects.filter(
        user=request.user,
        is_active=True
    ).first()

    if not enrollment:
        return redirect('learners:select_program')

    program = enrollment.program
    overall_progress = enrollment.get_overall_progress()

    # Get all modules with their lessons
    modules = Module.objects.filter(program=program).order_by('start_month', 'order')
    module_data = []

    for module in modules:
        lessons = Lesson.objects.filter(module=module).order_by('order')
        lesson_progress_list = []

        for lesson in lessons:
            progress = LessonProgress.objects.filter(user=request.user, lesson=lesson).first()
            lesson_progress_list.append({
                'lesson': lesson,
                'progress': progress,
                'status': progress.status if progress else 'not_started',
                'time_spent': progress.get_time_spent_display() if progress else '0 min',
            })

        # Get module-level progress
        completion_percentage = module.get_completion_percentage(request.user)
        status = 'completed' if completion_percentage == 100 else ('in_progress' if completion_percentage > 0 else 'not_started')

        # Check for assessments
        assessment = Assessment.objects.filter(module=module).first()

        module_data.append({
            'module': module,
            'lessons': lesson_progress_list,
            'completion_percentage': completion_percentage,
            'status': status,
            'assessment': assessment,
        })

    context = {
        'program': program,
        'overall_progress': overall_progress,
        'module_data': module_data,
    }

    return render(request, 'learners/my_program.html', context)


@login_required
def module_detail(request, module_id):
    """Display lessons within a module with assessment"""
    module = get_object_or_404(Module, id=module_id)
    enrollment = UserProgramEnrollment.objects.filter(
        user=request.user,
        program=module.program,
        is_active=True
    ).first()

    if not enrollment:
        messages.error(request, 'You are not enrolled in this program.')
        return redirect('learners:dashboard')

    # Get all lessons for this module
    lessons = Lesson.objects.filter(module=module).order_by('order')
    lesson_data = []

    for lesson in lessons:
        # Get or create progress for this lesson
        progress, created = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'status': 'not_started', 'progress_percentage': 0}
        )

        lesson_data.append({
            'lesson': lesson,
            'progress': progress,
            'time_spent': progress.get_time_spent_display(),
        })

    completion_percentage = module.get_completion_percentage(request.user)

    # Get module assessment if exists
    assessment = Assessment.objects.filter(module=module).first()
    assessment_completed = False
    if assessment:
        assessment_completed = AssessmentResponse.objects.filter(
            user=request.user,
            question__assessment=assessment
        ).exists()

    context = {
        'module': module,
        'lesson_data': lesson_data,
        'completion_percentage': completion_percentage,
        'program': module.program,
        'assessment': assessment,
        'assessment_completed': assessment_completed,
    }

    return render(request, 'learners/module_detail.html', context)


@login_required
def lesson_view(request, lesson_id):
    """Display lesson content with time tracking"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    enrollment = UserProgramEnrollment.objects.filter(
        user=request.user,
        program=lesson.module.program,
        is_active=True
    ).first()

    if not enrollment:
        messages.error(request, 'You are not enrolled in this program.')
        return redirect('learners:dashboard')

    # Get or create progress for this lesson
    progress, created = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
        defaults={
            'status': 'in_progress',
            'progress_percentage': 0,
            'started_at': timezone.now(),
            'first_accessed_at': timezone.now(),
            'last_accessed_at': timezone.now()
        }
    )

    # Update time tracking
    if progress.status == 'not_started':
        progress.status = 'in_progress'
        progress.started_at = timezone.now()
        progress.first_accessed_at = timezone.now()

    # Update last accessed time
    progress.last_accessed_at = timezone.now()
    progress.save()

    # Get file URLs from storage
    video_url = None
    document_url = None
    audio_url = None

    if lesson.video_url:
        video_url = course_storage.get_file_url(lesson.video_url)
    if lesson.document_file:
        document_url = course_storage.get_file_url(lesson.document_file)
    if lesson.audio_file:
        audio_url = course_storage.get_file_url(lesson.audio_file)

    # Get next and previous lessons
    all_lessons = Lesson.objects.filter(module=lesson.module).order_by('order')
    lesson_list = list(all_lessons)
    current_index = lesson_list.index(lesson)

    prev_lesson = lesson_list[current_index - 1] if current_index > 0 else None
    next_lesson = lesson_list[current_index + 1] if current_index < len(lesson_list) - 1 else None

    context = {
        'lesson': lesson,
        'progress': progress,
        'video_url': video_url,
        'document_url': document_url,
        'audio_url': audio_url,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'module': lesson.module,
        'program': lesson.module.program,
        'time_spent': progress.get_time_spent_display(),
    }

    return render(request, 'learners/lesson_view.html', context)


@login_required
def mark_lesson_complete(request, lesson_id):
    """Mark a lesson as completed"""
    if request.method == 'POST':
        lesson = get_object_or_404(Lesson, id=lesson_id)

        progress, created = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'status': 'not_started', 'progress_percentage': 0}
        )

        progress.status = 'completed'
        progress.progress_percentage = 100
        progress.completed_at = timezone.now()
        if not progress.started_at:
            progress.started_at = timezone.now()
        progress.save()

        messages.success(request, f'Lesson "{lesson.title}" marked as completed!')

        # Redirect to module detail or next lesson
        next_lesson = Lesson.objects.filter(
            module=lesson.module,
            order__gt=lesson.order
        ).order_by('order').first()

        if next_lesson and 'continue' in request.POST:
            return redirect('learners:lesson_view', lesson_id=next_lesson.id)
        else:
            return redirect('learners:module_detail', module_id=lesson.module.id)

    return redirect('learners:dashboard')


@login_required
def select_program(request):
    """Select a program to enroll in"""
    programs = Program.objects.filter(is_active=True)

    context = {
        'programs': programs,
    }

    return render(request, 'learners/select_program.html', context)


@login_required
def enroll_program(request, program_id):
    """Enroll in a program"""
    program = get_object_or_404(Program, id=program_id, is_active=True)

    enrollment, created = UserProgramEnrollment.objects.get_or_create(
        user=request.user,
        program=program,
        defaults={'is_active': True}
    )

    if created:
        messages.success(request, f'Successfully enrolled in {program.title}!')

    return redirect('learners:onboarding', program_id=program.id)


@login_required
def badges(request):
    """Display user's earned badges"""
    user_badges = UserBadge.objects.filter(user=request.user).select_related('badge')

    context = {
        'user_badges': user_badges,
    }

    return render(request, 'learners/badges.html', context)


@login_required
def assessments(request):
    """Display user's assessments"""
    # TODO: Implement assessment listing
    return render(request, 'learners/assessments.html')


@login_required
def co_learners(request):
    """Display other learners/participants in the same program"""
    enrollment = UserProgramEnrollment.objects.filter(
        user=request.user,
        is_active=True
    ).first()

    if not enrollment:
        messages.error(request, 'You are not enrolled in any program.')
        return redirect('learners:dashboard')

    program = enrollment.program

    # Get all learners enrolled in the same program (excluding current user)
    co_learner_enrollments = UserProgramEnrollment.objects.filter(
        program=program,
        is_active=True
    ).exclude(user=request.user).select_related('user')

    co_learner_data = []
    for co_enrollment in co_learner_enrollments:
        co_user = co_enrollment.user
        progress = co_enrollment.get_overall_progress()

        # Get badges earned
        badges_count = UserBadge.objects.filter(user=co_user).count()

        # Get lessons completed
        lessons_completed = LessonProgress.objects.filter(
            user=co_user,
            lesson__module__program=program,
            status='completed'
        ).count()

        co_learner_data.append({
            'user': co_user,
            'progress': progress,
            'badges_count': badges_count,
            'lessons_completed': lessons_completed,
            'enrolled_at': co_enrollment.enrolled_at,
        })

    # Sort by progress (highest first)
    co_learner_data.sort(key=lambda x: x['progress'], reverse=True)

    context = {
        'program': program,
        'co_learners': co_learner_data,
        'total_co_learners': len(co_learner_data),
    }

    return render(request, 'learners/co_learners.html', context)


@login_required
def update_lesson_time(request, lesson_id):
    """AJAX endpoint to update time spent on a lesson"""
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            time_spent_seconds = int(data.get('time_spent', 0))

            lesson = get_object_or_404(Lesson, id=lesson_id)
            progress = LessonProgress.objects.filter(
                user=request.user,
                lesson=lesson
            ).first()

            if progress:
                progress.total_time_spent_seconds += time_spent_seconds
                progress.last_accessed_at = timezone.now()
                progress.save()

                return JsonResponse({
                    'status': 'success',
                    'total_time': progress.total_time_spent_seconds,
                    'time_display': progress.get_time_spent_display()
                })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
