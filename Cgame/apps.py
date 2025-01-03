from django.apps import AppConfig


class CgameConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Cgame'

    def ready(self):
        import Cgame.signals  # Import the signals module
