from django.apps import AppConfig


class AuthenticateConfig(AppConfig):
    name = 'Authenticate'
    def ready(self):
        import Authenticate.signals 


