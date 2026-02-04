from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from programs.models import (
    Program, Month, Module, Lesson, Badge, Assessment,
    AssessmentQuestion, OnboardingTemplate, UserProgramEnrollment,
    LessonProgress, ModuleProgress, AssessmentResponse
)
from accounts.models import User
from core.storage import course_storage
from .forms import (
    ProgramForm, MonthForm, ModuleForm, LessonForm,
    BadgeForm, AssessmentForm, AssessmentQuestionForm,
    OnboardingTemplateForm
)


def is_admin(user):
    return user.is_authenticated and (user.is_admin or user.is_superuser)


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard overview"""
    total_programs = Program.objects.count()
    total_learners = User.objects.filter(is_learner=True).count()
    total_lessons = Lesson.objects.count()
    total_badges = Badge.objects.count()

    context = {
        'total_programs': total_programs,
        'total_learners': total_learners,
        'total_lessons': total_lessons,
        'total_badges': total_badges,
    }

    return render(request, 'admins/dashboard.html', context)


# Program Management
@login_required
@user_passes_test(is_admin)
def program_list(request):
    """List all programs"""
    programs = Program.objects.all().order_by('-created_at')

    context = {
        'programs': programs,
    }

    return render(request, 'admins/programs/list.html', context)


@login_required
@user_passes_test(is_admin)
def program_create(request):
    """Create a new program"""
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            program = form.save()
            messages.success(request, f'Program "{program.title}" created successfully!')
            return redirect('admins:program_detail', program_id=program.id)
    else:
        form = ProgramForm()

    context = {
        'form': form,
        'action': 'Create',
    }

    return render(request, 'admins/programs/form.html', context)


@login_required
@user_passes_test(is_admin)
def program_edit(request, program_id):
    """Edit a program"""
    program = get_object_or_404(Program, id=program_id)

    if request.method == 'POST':
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            program = form.save()
            messages.success(request, f'Program "{program.title}" updated successfully!')
            return redirect('admins:program_detail', program_id=program.id)
    else:
        form = ProgramForm(instance=program)

    context = {
        'form': form,
        'program': program,
        'action': 'Edit',
    }

    return render(request, 'admins/programs/form.html', context)


@login_required
@user_passes_test(is_admin)
def program_detail(request, program_id):
    """View program details and curriculum"""
    program = get_object_or_404(Program, id=program_id)
    modules = Module.objects.filter(program=program).order_by('start_month', 'order')

    context = {
        'program': program,
        'modules': modules,
    }

    return render(request, 'admins/programs/detail.html', context)


@login_required
@user_passes_test(is_admin)
def program_delete(request, program_id):
    """Delete a program"""
    program = get_object_or_404(Program, id=program_id)

    if request.method == 'POST':
        program_title = program.title
        program.delete()
        messages.success(request, f'Program "{program_title}" deleted successfully!')
        return redirect('admins:program_list')

    return redirect('admins:program_detail', program_id=program.id)


# Month Management
@login_required
@user_passes_test(is_admin)
def month_create(request, program_id):
    """Create a new month"""
    program = get_object_or_404(Program, id=program_id)

    if request.method == 'POST':
        form = MonthForm(request.POST)
        if form.is_valid():
            month = form.save(commit=False)
            month.program = program
            month.save()
            messages.success(request, f'Month "{month.title}" created successfully!')
            return redirect('admins:month_detail', month_id=month.id)
    else:
        # Suggest next month number
        last_month = Month.objects.filter(program=program).order_by('-month_number').first()
        initial_month_number = last_month.month_number + 1 if last_month else 1

        form = MonthForm(initial={'month_number': initial_month_number})

    context = {
        'form': form,
        'program': program,
        'action': 'Create',
    }

    return render(request, 'admins/months/form.html', context)


@login_required
@user_passes_test(is_admin)
def month_edit(request, month_id):
    """Edit a month"""
    month = get_object_or_404(Month, id=month_id)

    if request.method == 'POST':
        form = MonthForm(request.POST, instance=month)
        if form.is_valid():
            month = form.save()
            messages.success(request, f'Month "{month.title}" updated successfully!')
            return redirect('admins:month_detail', month_id=month.id)
    else:
        form = MonthForm(instance=month)

    context = {
        'form': form,
        'month': month,
        'program': month.program,
        'action': 'Edit',
    }

    return render(request, 'admins/months/form.html', context)


@login_required
@user_passes_test(is_admin)
def month_detail(request, month_id):
    """View month details and modules"""
    month = get_object_or_404(Month, id=month_id)
    modules = Module.objects.filter(month=month).order_by('order')

    context = {
        'month': month,
        'modules': modules,
        'program': month.program,
    }

    return render(request, 'admins/months/detail.html', context)


# Module Management
@login_required
@user_passes_test(is_admin)
def module_create(request, program_id):
    """Create a new module"""
    program = get_object_or_404(Program, id=program_id)

    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.program = program
            module.save()
            messages.success(request, f'Module "{module.title}" created successfully!')
            return redirect('admins:module_detail', module_id=module.id)
    else:
        # Suggest next order number
        last_module = Module.objects.filter(program=program).order_by('-order').first()
        initial_order = last_module.order + 1 if last_module else 1

        form = ModuleForm(initial={'order': initial_order})

    context = {
        'form': form,
        'program': program,
        'action': 'Create',
    }

    return render(request, 'admins/modules/form.html', context)


@login_required
@user_passes_test(is_admin)
def module_edit(request, module_id):
    """Edit a module"""
    module = get_object_or_404(Module, id=module_id)

    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            module = form.save()
            messages.success(request, f'Module "{module.title}" updated successfully!')
            return redirect('admins:module_detail', module_id=module.id)
    else:
        form = ModuleForm(instance=module)

    context = {
        'form': form,
        'module': module,
        'program': module.program,
        'action': 'Edit',
    }

    return render(request, 'admins/modules/form.html', context)


@login_required
@user_passes_test(is_admin)
def module_detail(request, module_id):
    """View module details and lessons"""
    module = get_object_or_404(Module, id=module_id)
    lessons = Lesson.objects.filter(module=module).order_by('order')

    # Get assessment linked to this module
    assessment = Assessment.objects.filter(module=module).first()

    context = {
        'module': module,
        'lessons': lessons,
        'assessment': assessment,
        'program': module.program,
    }

    return render(request, 'admins/modules/detail.html', context)


# Lesson Management
@login_required
@user_passes_test(is_admin)
def lesson_create(request, module_id):
    """Create a new lesson"""
    module = get_object_or_404(Module, id=module_id)

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module

            # Save lesson first to get an ID for file paths
            lesson.save()

            # Handle file uploads with lesson-specific paths
            files_uploaded = False
            if 'video_file' in request.FILES:
                file = request.FILES['video_file']
                blob_name = f"lessons/{lesson.id}/video/{file.name}"
                lesson.video_url = course_storage.upload_file(file, blob_name)
                files_uploaded = True

            if 'document_file_upload' in request.FILES:
                file = request.FILES['document_file_upload']
                blob_name = f"lessons/{lesson.id}/documents/{file.name}"
                lesson.document_file = course_storage.upload_file(file, blob_name)
                files_uploaded = True

            if 'audio_file_upload' in request.FILES:
                file = request.FILES['audio_file_upload']
                blob_name = f"lessons/{lesson.id}/audio/{file.name}"
                lesson.audio_file = course_storage.upload_file(file, blob_name)
                files_uploaded = True

            # Save again if files were uploaded to update file paths
            if files_uploaded:
                lesson.save()

            messages.success(request, f'Lesson "{lesson.title}" created successfully!')
            return redirect('admins:module_detail', module_id=module.id)
    else:
        # Suggest next order number
        last_lesson = Lesson.objects.filter(module=module).order_by('-order').first()
        initial_order = last_lesson.order + 1 if last_lesson else 1

        form = LessonForm(initial={'order': initial_order})

    context = {
        'form': form,
        'module': module,
        'program': module.program,
        'action': 'Create',
    }

    return render(request, 'admins/lessons/form.html', context)


@login_required
@user_passes_test(is_admin)
def lesson_edit(request, lesson_id):
    """Edit a lesson"""
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            lesson = form.save(commit=False)

            # Handle file uploads with lesson-specific paths
            if 'video_file' in request.FILES:
                file = request.FILES['video_file']
                blob_name = f"lessons/{lesson.id}/video/{file.name}"
                lesson.video_url = course_storage.upload_file(file, blob_name)

            if 'document_file_upload' in request.FILES:
                file = request.FILES['document_file_upload']
                blob_name = f"lessons/{lesson.id}/documents/{file.name}"
                lesson.document_file = course_storage.upload_file(file, blob_name)

            if 'audio_file_upload' in request.FILES:
                file = request.FILES['audio_file_upload']
                blob_name = f"lessons/{lesson.id}/audio/{file.name}"
                lesson.audio_file = course_storage.upload_file(file, blob_name)

            lesson.save()
            messages.success(request, f'Lesson "{lesson.title}" updated successfully!')
            return redirect('admins:module_detail', module_id=lesson.module.id)
    else:
        form = LessonForm(instance=lesson)

    context = {
        'form': form,
        'lesson': lesson,
        'module': lesson.module,
        'program': lesson.module.program,
        'action': 'Edit',
    }

    return render(request, 'admins/lessons/form.html', context)


# Badge Management
@login_required
@user_passes_test(is_admin)
def badge_list(request):
    """List all badges"""
    badges = Badge.objects.all()

    context = {
        'badges': badges,
    }

    return render(request, 'admins/badges/list.html', context)


@login_required
@user_passes_test(is_admin)
def badge_create(request):
    """Create a new badge"""
    if request.method == 'POST':
        form = BadgeForm(request.POST)
        if form.is_valid():
            badge = form.save()
            messages.success(request, f'Badge "{badge.title}" created successfully!')
            return redirect('admins:badge_list')
    else:
        form = BadgeForm()

    context = {
        'form': form,
        'action': 'Create',
    }

    return render(request, 'admins/badges/form.html', context)


@login_required
@user_passes_test(is_admin)
def badge_edit(request, badge_id):
    """Edit a badge"""
    badge = get_object_or_404(Badge, id=badge_id)

    if request.method == 'POST':
        form = BadgeForm(request.POST, instance=badge)
        if form.is_valid():
            badge = form.save()
            messages.success(request, f'Badge "{badge.title}" updated successfully!')
            return redirect('admins:badge_list')
    else:
        form = BadgeForm(instance=badge)

    context = {
        'form': form,
        'badge': badge,
        'action': 'Edit',
    }

    return render(request, 'admins/badges/form.html', context)


# Assessment Management
@login_required
@user_passes_test(is_admin)
def assessment_list(request):
    """List all assessments"""
    assessments = Assessment.objects.all()

    context = {
        'assessments': assessments,
    }

    return render(request, 'admins/assessments/list.html', context)


@login_required
@user_passes_test(is_admin)
def assessment_create(request):
    """Create a new assessment"""
    if request.method == 'POST':
        form = AssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save()
            messages.success(request, f'Assessment "{assessment.title}" created successfully!')
            return redirect('admins:assessment_detail', assessment_id=assessment.id)
    else:
        form = AssessmentForm()

    context = {
        'form': form,
        'action': 'Create',
    }

    return render(request, 'admins/assessments/form.html', context)


@login_required
@user_passes_test(is_admin)
def assessment_edit(request, assessment_id):
    """Edit an existing assessment"""
    assessment = get_object_or_404(Assessment, id=assessment_id)

    if request.method == 'POST':
        form = AssessmentForm(request.POST, instance=assessment)
        if form.is_valid():
            assessment = form.save()
            messages.success(request, f'Assessment "{assessment.title}" updated successfully!')
            return redirect('admins:assessment_detail', assessment_id=assessment.id)
    else:
        form = AssessmentForm(instance=assessment)

    context = {
        'form': form,
        'action': 'Edit',
        'assessment': assessment,
    }

    return render(request, 'admins/assessments/form.html', context)


@login_required
@user_passes_test(is_admin)
def assessment_detail(request, assessment_id):
    """View assessment details and questions"""
    assessment = get_object_or_404(Assessment, id=assessment_id)
    questions = AssessmentQuestion.objects.filter(assessment=assessment).order_by('order')

    context = {
        'assessment': assessment,
        'questions': questions,
    }

    return render(request, 'admins/assessments/detail.html', context)


@login_required
@user_passes_test(is_admin)
def question_create(request, assessment_id):
    """Create a new assessment question"""
    assessment = get_object_or_404(Assessment, id=assessment_id)

    if request.method == 'POST':
        form = AssessmentQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.assessment = assessment
            question.save()
            messages.success(request, 'Question created successfully!')
            return redirect('admins:assessment_detail', assessment_id=assessment.id)
    else:
        # Suggest next order number
        last_question = AssessmentQuestion.objects.filter(assessment=assessment).order_by('-order').first()
        initial_order = last_question.order + 1 if last_question else 1

        form = AssessmentQuestionForm(initial={'order': initial_order})

    context = {
        'form': form,
        'assessment': assessment,
        'action': 'Create',
    }

    return render(request, 'admins/assessments/question_form.html', context)


# Onboarding Template Management
@login_required
@user_passes_test(is_admin)
def onboarding_template_create(request, program_id):
    """Create onboarding template for a program"""
    program = get_object_or_404(Program, id=program_id)

    if request.method == 'POST':
        form = OnboardingTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.program = program
            template.save()
            messages.success(request, 'Onboarding template created successfully!')
            return redirect('admins:program_detail', program_id=program.id)
    else:
        form = OnboardingTemplateForm()

    context = {
        'form': form,
        'program': program,
        'action': 'Create',
    }

    return render(request, 'admins/onboarding/form.html', context)


@login_required
@user_passes_test(is_admin)
def onboarding_template_edit(request, template_id):
    """Edit onboarding template"""
    template = get_object_or_404(OnboardingTemplate, id=template_id)

    if request.method == 'POST':
        form = OnboardingTemplateForm(request.POST, instance=template)
        if form.is_valid():
            template = form.save()
            messages.success(request, 'Onboarding template updated successfully!')
            return redirect('admins:program_detail', program_id=template.program.id)
    else:
        form = OnboardingTemplateForm(instance=template)

    context = {
        'form': form,
        'template': template,
        'program': template.program,
        'action': 'Edit',
    }

    return render(request, 'admins/onboarding/form.html', context)


# Participant Progress Tracking
@login_required
@user_passes_test(is_admin)
def participant_list(request):
    """List all participants/learners"""
    learners = User.objects.filter(is_learner=True).order_by('-date_joined')

    context = {
        'learners': learners,
    }

    return render(request, 'admins/participants/list.html', context)


@login_required
@user_passes_test(is_admin)
def participant_progress(request, user_id):
    """View detailed progress for a specific participant"""
    participant = get_object_or_404(User, id=user_id, is_learner=True)
    enrollments = UserProgramEnrollment.objects.filter(user=participant).select_related('program')

    # Get enrolled program (assuming one active enrollment)
    enrollment = enrollments.filter(is_active=True).first()

    if enrollment:
        program = enrollment.program
        modules = Module.objects.filter(program=program).order_by('start_month', 'order')

        # Get progress for each module
        module_progress_data = []
        for module in modules:
            lessons = Lesson.objects.filter(module=module).order_by('order')
            lesson_progress_list = []

            for lesson in lessons:
                progress = LessonProgress.objects.filter(user=participant, lesson=lesson).first()
                lesson_progress_list.append({
                    'lesson': lesson,
                    'progress': progress,
                })

            module_progress_data.append({
                'module': module,
                'lessons': lesson_progress_list,
            })

        # Get assessment responses
        assessments = Assessment.objects.filter(module__program=program)
        assessment_responses = []
        for assessment in assessments:
            responses = AssessmentResponse.objects.filter(
                user=participant,
                question__assessment=assessment
            ).select_related('question')
            if responses.exists():
                assessment_responses.append({
                    'assessment': assessment,
                    'responses': responses,
                })

        context = {
            'participant': participant,
            'program': program,
            'enrollment': enrollment,
            'module_progress_data': module_progress_data,
            'assessment_responses': assessment_responses,
        }
    else:
        context = {
            'participant': participant,
            'program': None,
        }

    return render(request, 'admins/participants/progress.html', context)


@login_required
@user_passes_test(is_admin)
def override_lesson_completion(request, user_id, lesson_id):
    """Admin override to mark a lesson as complete or incomplete"""
    participant = get_object_or_404(User, id=user_id, is_learner=True)
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        note = request.POST.get('note', '')

        progress, created = LessonProgress.objects.get_or_create(
            user=participant,
            lesson=lesson,
            defaults={'status': status}
        )

        if not created:
            progress.status = status

        progress.is_overridden = True
        progress.overridden_by = request.user
        progress.overridden_at = timezone.now()
        progress.override_note = note

        if status == 'completed':
            progress.completed_at = timezone.now()
            progress.progress_percentage = 100
        elif status == 'in_progress':
            progress.started_at = timezone.now()

        progress.save()

        messages.success(request, f'Lesson "{lesson.title}" status updated to "{status}" for {participant.email}')
        return redirect('admins:participant_progress', user_id=user_id)

    context = {
        'participant': participant,
        'lesson': lesson,
    }

    return render(request, 'admins/participants/override_lesson.html', context)


@login_required
@user_passes_test(is_admin)
def override_module_completion(request, user_id, module_id):
    """Admin override to mark a module as complete or incomplete"""
    participant = get_object_or_404(User, id=user_id, is_learner=True)
    module = get_object_or_404(Module, id=module_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        note = request.POST.get('note', '')

        progress, created = ModuleProgress.objects.get_or_create(
            user=participant,
            module=module,
            defaults={'status': status}
        )

        if not created:
            progress.status = status

        progress.is_overridden = True
        progress.overridden_by = request.user
        progress.overridden_at = timezone.now()
        progress.override_note = note

        if status == 'completed':
            progress.completed_at = timezone.now()
            progress.progress_percentage = 100
        elif status == 'in_progress':
            progress.started_at = timezone.now()

        progress.save()

        messages.success(request, f'Module "{module.title}" status updated to "{status}" for {participant.email}')
        return redirect('admins:participant_progress', user_id=user_id)

    context = {
        'participant': participant,
        'module': module,
    }

    return render(request, 'admins/participants/override_module.html', context)


# Assessment Responses View
@login_required
@user_passes_test(is_admin)
def assessment_responses(request, assessment_id):
    """View all responses for a specific assessment"""
    assessment = get_object_or_404(Assessment, id=assessment_id)
    questions = AssessmentQuestion.objects.filter(assessment=assessment).order_by('order')

    # Get all users who have responded
    responded_users = User.objects.filter(
        assessment_responses__question__assessment=assessment
    ).distinct()

    # Organize responses by user
    user_responses = []
    for user in responded_users:
        responses = AssessmentResponse.objects.filter(
            user=user,
            question__assessment=assessment
        ).select_related('question').order_by('question__order')

        user_responses.append({
            'user': user,
            'responses': responses,
        })

    context = {
        'assessment': assessment,
        'questions': questions,
        'user_responses': user_responses,
    }

    return render(request, 'admins/assessments/responses.html', context)
