from django.urls import path
from . import views

# Done by Claude, requires review
app_name = "oversight"

urlpatterns = [
    path("report/page/<int:page_id>/", views.report_page, name="report_page"),
    path("report/page/success/", views.report_success, {"content_type": "page"}, name="report_page_success"),
    path("report/page/already/", views.report_already, {"content_type": "page"}, name="report_page_already"),
    path("report/post/<int:post_id>/", views.report_post, name="report_post"),
    path("report/post/success/", views.report_success, {"content_type": "post"}, name="report_post_success"),
    path("report/post/already/", views.report_already, {"content_type": "post"}, name="report_post_already"),
]
