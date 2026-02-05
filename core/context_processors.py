"""Context processors for making settings available in templates."""
from django.conf import settings


def azure_sso_settings(request):
    """Expose Azure AD SSO settings to templates."""
    return {
        'USE_AZURE_AD_SSO': settings.USE_AZURE_AD_SSO,
    }
