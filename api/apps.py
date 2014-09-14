from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        # Register signal handlers
        from api.signals import create_auth_token

