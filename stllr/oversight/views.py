from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from pages.models import Page
from forums.models import Post
from .forms import PageReportForm, PostReportForm
from .models import PageReport, PostReport


@login_required
def report_page(request, page_id):
    page = get_object_or_404(Page, id=page_id)

    if PageReport.objects.filter(reporter=request.user, page=page).exists():
        return redirect(reverse("oversight:report_page_already"))

    if request.method == "POST":
        form = PageReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.page = page
            report.save()
            return redirect(reverse("oversight:report_page_success"))
    else:
        form = PageReportForm()

    return render(request, "report/form.html", {"form": form, "content_type": "page", "page": page})

@login_required
def report_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if PostReport.objects.filter(reporter=request.user, post=post).exists():
        return redirect(reverse("oversight:report_post_already"))
    
    if request.method == "POST":
        form = PostReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.post = post
            report.save()
            return redirect(reverse("oversight:report_post_success"))
    else:
        form = PostReportForm()

    return render(request, "report/form.html", {"form": form, "content_type": "post", "post": post})


def report_success(request, content_type):
    return render(request, "report/success.html", {"content_type": content_type})

def report_already(request, content_type):
    return render(request, "report/already.html", {"content_type": content_type})