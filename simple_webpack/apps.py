from django.apps import AppConfig
from django.conf import settings
from django.core.checks import Error, Tags, register
from django.utils.translation import ugettext_lazy as _


class SimpleWebpackConfig(AppConfig):
    name = 'simple_webpack'
    verbose_name = _('Simple Webpack')


@register(Tags.compatibility)
def check_config():
    """Check for proper Simple Webpack config in Django settings."""
    errors = []

    webpack_stats_path = getattr(settings, 'WEBPACK_STATS_PATH', None)
    if webpack_stats_path is None:
        errors.append(
            Error(
                'WEBPACK_STATS_PATH is not set in Django settings.',
                hint=(
                    'In your Django settings file, add the variable '
                    '"WEBPACK_STATS_PATH" with the value set to the '
                    'path of your Webpack Bundle Tracker file.'
                )
            )
        )

    allow_compiling = getattr(settings, 'WEBPACK_ALLOW_COMPILING', None)
    if allow_compiling is None:
        allow_compiling = 0
    if allow_compiling not in range(0, 11):
        errors.append(
            Error(
                'Invalid value for WEBPACK_ALLOW_COMPILING '
                'in Django settings.',
                hint=(
                    'WEBPACK_ALLOW_COMPILING is an optional development '
                    'setting that must be Falsey (e.g. False, None, or 0), '
                    'or an integer between 1 and 10.'
                )
            )
        )

    static_url_path = getattr(settings, 'STATIC_URL', None)
    if static_url_path is None:
        errors.append(
            Error(
                'STATIC_URL is not set in Django settings.',
                hint=(
                    'In your Django settings file, add the variable '
                    '"STATIC_URL" with the value set to the path you '
                    'want Django to serve your static files from.\n'
                    'Generally, that value would be "/static/".'
                )
            )
        )

    staticfiles_dirs = getattr(settings, 'STATICFILES_DIRS', None)
    if staticfiles_dirs is None:
        errors.append(
            Error(
                'STATICFILES_DIRS is not set in Django settings.',
                hint=(
                    'In your Django settings file, add the variable '
                    '"STATICFILES_DIRS" with the value set a tuple '
                    'containing any paths to where you keep the static '
                    'assets you want Django to serve from your STATIC_URL.'
                )
            )
        )

    return errors
