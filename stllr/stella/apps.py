from django.apps import AppConfig


class StellaConfig(AppConfig):
    name = 'stella'

    def ready(self):
        import stella.signals
