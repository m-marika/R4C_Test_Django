"""
Apps configuration
"""
from django.apps import AppConfig


class RobotsConfig(AppConfig):
    """
    Configuration class for the robots app.

    This class defines the default auto field and the name of the app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'robots'

    def ready(self):
        import robots.signals # pylint: disable=import-outside-toplevel, unused-import
