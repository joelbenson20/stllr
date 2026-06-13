from django.apps import AppConfig


class ForumsConfig(AppConfig):
    name = 'forums'

    def ready(self):
        import forums.signals


# TODO: Clean up firmament sort, handle like Pages app handles sorting by firmament
# TODO: Consier a post feeder template that feeds posts under pages or replies to posts, modeled after the page feeder
# TODO: Clariy whether there is a more efficient way to use get_descendents() if I want unlimited thread depth
# TODO: Post removal should only supported removal by the author for now, and it should take away the display of the author's username and profile image.