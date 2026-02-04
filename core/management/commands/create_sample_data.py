"""
Management command to create sample program data for testing.
Usage: python manage.py create_sample_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from programs.models import (
    Program, Month, Module, Lesson, Badge, Assessment,
    AssessmentQuestion, OnboardingTemplate, UserProgramEnrollment
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates sample program data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create sample program
        program, created = Program.objects.get_or_create(
            title='Leadership Excellence Program 2024',
            defaults={
                'description': 'A comprehensive 12-month journey to develop your leadership skills',
                'duration_months': 12,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created program: {program.title}'))

        # Create Month 1
        month1, created = Month.objects.get_or_create(
            program=program,
            month_number=1,
            defaults={
                'title': 'Foundation of Leadership',
                'description': 'Build the fundamental principles of effective leadership',
                'learning_objectives': 'Understand core leadership principles, develop self-awareness, and establish your leadership foundation.'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created month: {month1.title}'))

        # Create modules directly under program (new structure)
        module1, created = Module.objects.get_or_create(
            program=program,
            title='Understanding Leadership',
            defaults={
                'description': 'Explore what leadership means and discover different leadership styles and approaches.',
                'module_type': 'behavioral',
                'order': 1,
                'duration_minutes': 120,
                'start_month': 1,
                'end_month': 1,
                'month': month1  # Keep for backward compatibility
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created module: {module1.title}'))

        # Create lessons for module 1
        lessons_data = [
            {
                'title': 'What is Leadership?',
                'description': 'Introduction to the fundamentals of leadership',
                'content_type': 'video',
                'order': 1,
                'duration_minutes': 15,
                'text_content': 'Leadership is the art of motivating a group of people to act toward achieving a common goal. In a business setting, this can mean directing workers and colleagues with a strategy to meet the company\'s needs.'
            },
            {
                'title': 'Leadership vs Management',
                'description': 'Understanding the key differences',
                'content_type': 'text',
                'order': 2,
                'duration_minutes': 20,
                'text_content': '''Leadership and management are often confused, but they are distinctly different:

Leadership:
- Sets vision and direction
- Inspires and motivates
- Focuses on people
- Embraces change
- Takes risks

Management:
- Plans and organizes
- Directs and controls
- Focuses on processes
- Maintains stability
- Mitigates risk

Great organizations need both strong leaders and effective managers.'''
            },
            {
                'title': 'Leadership Styles Overview',
                'description': 'Discover different approaches to leadership',
                'content_type': 'video',
                'order': 3,
                'duration_minutes': 25,
                'text_content': 'Explore various leadership styles including autocratic, democratic, transformational, servant leadership, and more.'
            },
            {
                'title': 'Discovering Your Leadership Style',
                'description': 'Self-reflection exercise',
                'content_type': 'mixed',
                'order': 4,
                'duration_minutes': 30,
                'text_content': 'Complete the self-assessment questionnaire to discover your natural leadership tendencies and areas for development.'
            },
            {
                'title': 'Case Studies: Great Leaders',
                'description': 'Learn from historical and contemporary leaders',
                'content_type': 'document',
                'order': 5,
                'duration_minutes': 30,
                'is_optional': True,
                'text_content': 'Study cases of successful leaders and extract key principles you can apply to your own leadership journey.'
            }
        ]

        for lesson_data in lessons_data:
            lesson, created = Lesson.objects.get_or_create(
                module=module1,
                title=lesson_data['title'],
                defaults=lesson_data
            )
            if created:
                self.stdout.write(f'  Created lesson: {lesson.title}')

        # Create Month 2
        month2, created = Month.objects.get_or_create(
            program=program,
            month_number=2,
            defaults={
                'title': 'Communication Mastery',
                'description': 'Master communication techniques for effective leadership',
                'learning_objectives': 'Develop active listening skills, master verbal and non-verbal communication, and learn to communicate with impact.'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created month: {month2.title}'))

        # Create module for Month 2
        module2, created = Module.objects.get_or_create(
            program=program,
            title='Effective Communication',
            defaults={
                'description': 'Learn the art of clear, impactful communication',
                'module_type': 'behavioral',
                'order': 2,
                'duration_minutes': 150,
                'start_month': 2,
                'end_month': 2,
                'month': month2  # Keep for backward compatibility
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created module: {module2.title}'))

        # Create badges
        badges_data = [
            {
                'title': 'First Steps',
                'description': 'Completed your first lesson',
                'icon': 'star',
                'color': '#3b82f6',
                'criteria': 'Complete first lesson in any module'
            },
            {
                'title': 'Month Completion',
                'description': 'Finished an entire month of content',
                'icon': 'trophy',
                'color': '#10b981',
                'criteria': 'Complete all lessons in a month'
            },
            {
                'title': 'Assessment Master',
                'description': 'Completed all assessments',
                'icon': 'award',
                'color': '#f59e0b',
                'criteria': 'Complete all module assessments'
            }
        ]

        for badge_data in badges_data:
            badge, created = Badge.objects.get_or_create(
                title=badge_data['title'],
                defaults=badge_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created badge: {badge.title}'))

        # Create onboarding assessment
        assessment, created = Assessment.objects.get_or_create(
            title='Leadership Self-Assessment',
            defaults={
                'description': 'Evaluate your current leadership capabilities',
                'is_onboarding': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created assessment: {assessment.title}'))

            # Create assessment questions
            questions_data = [
                {
                    'question_text': 'How would you rate your current leadership skills?',
                    'question_type': 'rating',
                    'order': 1,
                    'min_rating': 1,
                    'max_rating': 5,
                    'min_label': 'Beginner',
                    'max_label': 'Expert'
                },
                {
                    'question_text': 'How confident are you in making difficult decisions?',
                    'question_type': 'rating',
                    'order': 2,
                    'min_rating': 1,
                    'max_rating': 5,
                    'min_label': 'Not Confident',
                    'max_label': 'Very Confident'
                },
                {
                    'question_text': 'How effective are you at communicating with your team?',
                    'question_type': 'rating',
                    'order': 3,
                    'min_rating': 1,
                    'max_rating': 5,
                    'min_label': 'Needs Improvement',
                    'max_label': 'Excellent'
                },
                {
                    'question_text': 'What are your main leadership development goals?',
                    'question_type': 'text',
                    'order': 4
                }
            ]

            for question_data in questions_data:
                question = AssessmentQuestion.objects.create(
                    assessment=assessment,
                    **question_data
                )
                self.stdout.write(f'  Created question: {question.question_text[:50]}')

        # Create onboarding template
        template, created = OnboardingTemplate.objects.get_or_create(
            program=program,
            defaults={
                'pledge_title': 'Leadership Program Pledge',
                'pledge_content': '''I pledge to:

1. Commit to my leadership development journey
2. Actively participate in all learning activities
3. Apply the principles and techniques I learn
4. Support and encourage fellow learners
5. Seek feedback and continuously improve
6. Lead with integrity and authenticity

I understand that leadership is a journey, not a destination, and I am committed to continuous growth and development.''',
                'welcome_message': 'Welcome to the Leadership Excellence Program 2024! This 12-month journey will transform your leadership capabilities. Complete the onboarding to begin your journey.',
                'self_assessment': assessment
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created onboarding template'))

        # Create demo learner user if it doesn't exist
        demo_user, created = User.objects.get_or_create(
            email='learner@example.com',
            defaults={
                'first_name': 'Demo',
                'last_name': 'Learner',
                'is_learner': True
            }
        )
        if created:
            demo_user.set_password('password123')
            demo_user.save()
            self.stdout.write(self.style.SUCCESS('Created demo learner user (email: learner@example.com, password: password123)'))

            # Enroll demo user
            enrollment = UserProgramEnrollment.objects.create(
                user=demo_user,
                program=program,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS('Enrolled demo user in program'))

        # Create demo admin user if it doesn't exist
        admin_user, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'is_learner': True,
                'is_admin': True,
                'is_staff': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created demo admin user (email: admin@example.com, password: admin123)'))

        self.stdout.write(self.style.SUCCESS('\nSample data creation complete!'))
        self.stdout.write('\nYou can now:')
        self.stdout.write('1. Login as learner: learner@example.com / password123')
        self.stdout.write('2. Login as admin: admin@example.com / admin123')
        self.stdout.write('3. Access admin portal to create more content')
