from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.main_page, name="main_page"),
    path("enter_problem/", views.enter_problem, name="enter_problem"),
    path("search/", views.enter_query, name="enter_query"),
    path("search/query=<str:query>/", views.solution, name="solution"),
    path("search/prob=<str:problem>/edit/", views.edit_solution, name="edit_solution"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
