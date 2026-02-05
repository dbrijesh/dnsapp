from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        # Set password if provided, otherwise unusable password for SSO users
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)

        # Superusers always need a password for Django admin
        if not password:
            raise ValueError('Superusers must have a password')

        return self.create_user(email, password, **extra_fields)

    def create_sso_user(self, email, first_name='', last_name='', azure_ad_user_id='', **extra_fields):
        """Create a new SSO user without a password."""
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_learner', extra_fields.get('is_learner', False))
        extra_fields.setdefault('is_admin', extra_fields.get('is_admin', False))

        user = self.create_user(
            email=email,
            password=None,
            first_name=first_name,
            last_name=last_name,
            azure_ad_user_id=azure_ad_user_id,
            **extra_fields
        )
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_learner = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    # Azure AD SSO fields
    azure_ad_user_id = models.CharField(max_length=255, blank=True, null=True, unique=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name
