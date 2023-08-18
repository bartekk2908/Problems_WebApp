from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [
    path("", views.main_page, name="main_page"),
    path("add_solution/", views.add_solution, name="add_solution"),
    path("search=<str:query>/", views.solution, name="solution"),
    path("search=<int:p_id>/edit/", views.edit_solution, name="edit_solution"),
    path("all_solutions/sorting=<str:sorting>+<str:direction>/", views.all_solutions, name="all_solutions"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
