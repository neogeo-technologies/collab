import logging

from django.conf import settings

from geocontrib.models import Authorization

logger = logging.getLogger(__name__)


def sso_setted(request):
    return request.META.get('HTTP_SEC_PROXY', 'false') == 'true'

def login_url():
    return "cas_ng_login" if hasattr(settings, "CAS_SERVER_URL") else "geocontrib:login"


def custom_contexts(request):
    try:
        user_level_projects = Authorization.get_user_level_projects(request.user)
    except Exception:
        user_level_projects = {}
        logger.exception('Cannot retrieve user level project')

    return {
        'APPLICATION_NAME': settings.APPLICATION_NAME,
        'LOGO_PATH': settings.LOGO_PATH,
        'APPLICATION_ABSTRACT': settings.APPLICATION_ABSTRACT,
        'FAVICON_PATH': settings.FAVICON_PATH,
        'IMAGE_FORMAT': settings.IMAGE_FORMAT,
        'FILE_MAX_SIZE': settings.FILE_MAX_SIZE,
        'USER_LEVEL_PROJECTS': user_level_projects,
        'SERVICE': settings.DEFAULT_BASE_MAP.get('SERVICE'),
        'OPTIONS': settings.DEFAULT_BASE_MAP.get('OPTIONS'),
        'DEFAULT_MAP_VIEW': settings.DEFAULT_MAP_VIEW,
        'GEOCODER_PROVIDERS': settings.GEOCODER_PROVIDERS,
        'SELECTED_GEOCODER_PROVIDER': settings.SELECTED_GEOCODER.get('PROVIDER'),
        'SSO_SETTED': sso_setted(request),
        'LOGIN_URL': login_url(),
        'LOGIN_REDIRECT_URL': settings.LOGIN_REDIRECT_URL
    }
