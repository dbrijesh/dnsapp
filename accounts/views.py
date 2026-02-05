from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.conf import settings
from .forms import LoginForm, RegisterForm
from .azure_auth import build_auth_url, acquire_token_by_auth_code
import secrets
import logging

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def login_view(request):
    """Initiate Azure AD SSO login or show username/password form."""
    if request.user.is_authenticated:
        return redirect('learners:dashboard')

    # Check if Azure AD SSO is enabled
    if settings.USE_AZURE_AD_SSO:
        # Generate CSRF state token
        state = secrets.token_urlsafe(32)
        request.session['azure_auth_state'] = state
        request.session['next_url'] = request.GET.get('next', 'learners:dashboard')

        # Build redirect URI and Azure AD auth URL
        redirect_uri = request.build_absolute_uri(reverse('accounts:auth_callback'))
        auth_url = build_auth_url(redirect_uri, state)
        return redirect(auth_url)

    else:
        # Local development: username/password form
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                user = authenticate(request, username=email, password=password)

                if user is not None:
                    login(request, user)
                    next_url = request.GET.get('next', 'learners:dashboard')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Invalid email or password.')
        else:
            form = LoginForm()

        return render(request, 'accounts/login.html', {'form': form})


@require_http_methods(["GET"])
def auth_callback(request):
    """Handle Azure AD OAuth callback."""
    if not settings.USE_AZURE_AD_SSO:
        messages.error(request, "Azure AD SSO is not enabled.")
        return redirect('accounts:login')

    # Get parameters
    auth_code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')

    # Handle Azure AD errors
    if error:
        error_description = request.GET.get('error_description', 'Unknown error')
        logger.error(f"Azure AD error: {error} - {error_description}")
        messages.error(request, f"Authentication failed: {error_description}")
        return redirect('accounts:login')

    # Validate state (CSRF protection)
    session_state = request.session.get('azure_auth_state')
    if not state or state != session_state:
        logger.error("Invalid state parameter - possible CSRF attack")
        messages.error(request, "Authentication failed. Please try again.")
        return redirect('accounts:login')

    # Validate authorization code
    if not auth_code:
        logger.error("No authorization code received")
        messages.error(request, "Authentication failed. No authorization code received.")
        return redirect('accounts:login')

    # Exchange code for token
    redirect_uri = request.build_absolute_uri(reverse('accounts:auth_callback'))
    token = acquire_token_by_auth_code(auth_code, redirect_uri)

    if not token:
        messages.error(request, "Failed to acquire token from Azure AD.")
        return redirect('accounts:login')

    # Authenticate user with token
    user = authenticate(request, token=token)

    if user is None:
        # User not found in database or inactive
        messages.error(request, "Access denied. Please contact your administrator.")
        logger.warning(f"Access denied for Azure AD user")
        return redirect('accounts:login')

    # Log user in
    login(request, user, backend='accounts.backends.AzureADBackend')

    # Clean up session
    request.session.pop('azure_auth_state', None)
    next_url = request.session.pop('next_url', 'learners:dashboard')

    messages.success(request, f"Welcome back, {user.get_full_name() or user.email}!")
    return redirect(next_url)


@require_http_methods(["GET", "POST"])
def register_view(request):
    """User registration (disabled when Azure AD SSO is enabled)."""
    # Block registration if SSO is enabled
    if settings.USE_AZURE_AD_SSO:
        messages.error(request, "Self-registration is not available. Please contact your administrator.")
        return redirect('accounts:login')

    # Existing registration logic for local development
    if request.user.is_authenticated:
        return redirect('learners:dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_learner = True
            user.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('learners:dashboard')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')
