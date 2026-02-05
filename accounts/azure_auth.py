"""Azure AD authentication utilities using MSAL."""
import msal
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def get_msal_app():
    """Create MSAL ConfidentialClientApplication instance."""
    return msal.ConfidentialClientApplication(
        client_id=settings.AZURE_AD_CLIENT_ID,
        client_credential=settings.AZURE_AD_CLIENT_SECRET,
        authority=settings.AZURE_AD_AUTHORITY
    )


def build_auth_url(redirect_uri, state):
    """Build Azure AD authorization URL."""
    msal_app = get_msal_app()
    auth_url = msal_app.get_authorization_request_url(
        scopes=settings.AZURE_AD_SCOPES,
        redirect_uri=redirect_uri,
        state=state
    )
    logger.info(f"Built authorization URL with redirect_uri: {redirect_uri}")
    return auth_url


def acquire_token_by_auth_code(auth_code, redirect_uri):
    """Exchange authorization code for access token."""
    msal_app = get_msal_app()
    try:
        result = msal_app.acquire_token_by_authorization_code(
            code=auth_code,
            scopes=settings.AZURE_AD_SCOPES,
            redirect_uri=redirect_uri
        )
        if "error" in result:
            logger.error(f"Token acquisition error: {result.get('error_description')}")
            return None
        logger.info("Successfully acquired token from Azure AD")
        return result
    except Exception as e:
        logger.error(f"Exception during token acquisition: {str(e)}", exc_info=True)
        return None
