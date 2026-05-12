from django.apps import AppConfig


class ForumsConfig(AppConfig):
    name = 'forums'

    def ready(self):
        import forums.signals
