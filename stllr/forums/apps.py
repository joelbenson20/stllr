from django.apps import AppConfig


class ForumsConfig(AppConfig):
    name = 'forums'

    def ready(self):
        import forums.signals


# TODO: Post removal should only supported removal by the author for now, and it should take away the display of the author's username and profile image.