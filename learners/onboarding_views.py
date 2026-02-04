from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from programs.models import (
    Program, UserOnboarding, OnboardingTemplate,
    AssessmentResponse, AssessmentQuestion
)


@login_required
def onboarding(request, program_id):
    """Main onboarding flow"""
    program = get_object_or_404(Program, id=program_id)

    # Get or create onboarding record
    onboarding, created = UserOnboarding.objects.get_or_create(
        user=request.user,
        program=program
    )

    # If onboarding already completed, redirect to dashboard
    if onboarding.onboarding_completed:
        return redirect('learners:dashboard')

    # Check if onboarding template exists
    try:
        template = program.onboarding_template
    except OnboardingTemplate.DoesNotExist:
        messages.warning(request, 'Onboarding not configured for this program.')
        onboarding.onboarding_completed = True
        onboarding.onboarding_completed_at = timezone.now()
        onboarding.save()
        return redirect('learners:dashboard')

    context = {
        'program': program,
        'onboarding': onboarding,
        'template': template,
    }

    return render(request, 'learners/onboarding.html', context)


@login_required
def accept_pledge(request, program_id):
    """Accept program pledge"""
    program = get_object_or_404(Program, id=program_id)
    onboarding = get_object_or_404(UserOnboarding, user=request.user, program=program)

    if request.method == 'POST':
        onboarding.pledge_accepted = True
        onboarding.pledge_accepted_at = timezone.now()
        onboarding.save()

        messages.success(request, 'Pledge accepted! Please complete the self-assessment.')
        return redirect('learners:self_assessment', program_id=program.id)

    try:
        template = program.onboarding_template
    except OnboardingTemplate.DoesNotExist:
        messages.error(request, 'Onboarding template not found.')
        return redirect('learners:dashboard')

    context = {
        'program': program,
        'template': template,
        'onboarding': onboarding,
    }

    return render(request, 'learners/pledge.html', context)


@login_required
def self_assessment(request, program_id):
    """Self-assessment form"""
    program = get_object_or_404(Program, id=program_id)
    onboarding = get_object_or_404(UserOnboarding, user=request.user, program=program)

    if not onboarding.pledge_accepted:
        messages.warning(request, 'Please accept the pledge first.')
        return redirect('learners:accept_pledge', program_id=program.id)

    try:
        template = program.onboarding_template
        assessment = template.self_assessment
    except (OnboardingTemplate.DoesNotExist, AttributeError):
        messages.warning(request, 'Self-assessment not configured.')
        onboarding.onboarding_completed = True
        onboarding.onboarding_completed_at = timezone.now()
        onboarding.save()
        return redirect('learners:dashboard')

    if request.method == 'POST':
        # Save assessment responses
        questions = assessment.questions.all()

        for question in questions:
            response_key = f'question_{question.id}'
            response_value = request.POST.get(response_key)

            if response_value:
                if question.question_type == 'rating':
                    AssessmentResponse.objects.update_or_create(
                        user=request.user,
                        question=question,
                        defaults={'rating_value': int(response_value)}
                    )
                else:
                    AssessmentResponse.objects.update_or_create(
                        user=request.user,
                        question=question,
                        defaults={'text_value': response_value}
                    )

        # Mark assessment and onboarding as completed
        onboarding.assessment_completed = True
        onboarding.assessment_completed_at = timezone.now()
        onboarding.onboarding_completed = True
        onboarding.onboarding_completed_at = timezone.now()
        onboarding.save()

        messages.success(request, 'Assessment completed! Welcome to the program.')
        return redirect('learners:dashboard')

    questions = assessment.questions.all() if assessment else []

    context = {
        'program': program,
        'assessment': assessment,
        'questions': questions,
        'onboarding': onboarding,
    }

    return render(request, 'learners/self_assessment.html', context)
