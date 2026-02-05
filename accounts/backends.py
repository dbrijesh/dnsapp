from django.contrib.auth.backends import BaseBackend
from django.conf import settings
from .models import User
import logging

logger = logging.getLogger(__name__)


class AzureADBackend(BaseBackend):
    """
    Azure AD authentication backend using MSAL.
    Validates tokens and matches users by email.
    Users must exist in database before login.
    """

    def authenticate(self, request, token=None, **kwargs):
        """Authenticate user with Azure AD token."""
        if not token:
            return None

        try:
            # Extract ID token claims
            id_token_claims = token.get('id_token_claims')
            if not id_token_claims:
                logger.error("No id_token_claims found in token")
                return None

            # Validate token claims (issuer, audience, expiration)
            if not self._validate_token_claims(id_token_claims):
                logger.error("Token validation failed")
                return None

            # Extract email from claims (normalized to lowercase)
            email = id_token_claims.get('preferred_username') or id_token_claims.get('email')
            if not email:
                logger.error("No email found in token claims")
                return None
            email = email.lower()

            # Look up user in database by email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                logger.warning(f"User with email {email} not found in database")
                return None

            # Check if user is active
            if not user.is_active:
                logger.warning(f"User {email} is inactive")
                return None

            # Update Azure AD user ID if not set
            azure_user_id = id_token_claims.get('oid') or id_token_claims.get('sub')
            if azure_user_id and not user.azure_ad_user_id:
                user.azure_ad_user_id = azure_user_id
                user.save(update_fields=['azure_ad_user_id'])

            # Optionally update user profile from token
            self._update_user_profile(user, id_token_claims)

            logger.info(f"Successfully authenticated user: {email}")
            return user

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}", exc_info=True)
            return None

    def _validate_token_claims(self, claims):
        """Validate token issuer, audience, and expiration."""
        import time

        # Validate issuer
        expected_issuer = settings.AZURE_AD_TOKEN_ISSUER
        token_issuer = claims.get('iss')
        if not token_issuer or not token_issuer.startswith(expected_issuer.rstrip('/v2.0')):
            logger.error(f"Invalid issuer: {token_issuer}")
            return False

        # Validate audience
        if claims.get('aud') != settings.AZURE_AD_TOKEN_AUDIENCE:
            logger.error(f"Invalid audience: {claims.get('aud')}")
            return False

        # Validate expiration
        if claims.get('exp') and claims.get('exp') < time.time():
            logger.error("Token expired")
            return False

        return True

    def _update_user_profile(self, user, claims):
        """Update user profile fields from token claims."""
        updated = False
        if claims.get('given_name') and not user.first_name:
            user.first_name = claims.get('given_name')
            updated = True
        if claims.get('family_name') and not user.last_name:
            user.last_name = claims.get('family_name')
            updated = True
        if updated:
            user.save(update_fields=['first_name', 'last_name'])

    def get_user(self, user_id):
        """Get user by ID for session management."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
