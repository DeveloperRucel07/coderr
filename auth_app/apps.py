from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    """
    Configuration for the auth_app Django application.

    This class defines the configuration for the auth_app, including
    the app name and the ready method that imports signals.
    """
    name = 'auth_app'

    def ready(self):
        """
        Method called when the app is ready.

        Imports the signals module to register signal handlers.
        """
        import auth_app.signals

