from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def home_redirect(request):
    if request.user.is_authenticated:
        return redirect("upload_videos")  # If logged in, go to upload page
    return redirect("login")   # Redirect to login if not logged in

urlpatterns = [
    path("admin/", admin.site.urls),
    path("upload/", include("myapp.urls")),
    path("", home_redirect, name="home"),
]
