from django.apps import AppConfig


class StarsConfig(AppConfig):
    name = 'stars'

    def ready(self):
        import stars.signals  # noqa: F401
