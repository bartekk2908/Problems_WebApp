from django.urls import path

from . import views

urlpatterns = [
    path("", views.main_page, name="main_page"),
    path("problems/", views.enter_query, name="enter_query"),
    path("problems/solution/query=<str:query>/", views.solution, name="solution"),
    path("problems/solution/prob=<str:problem>/edit/", views.enter_solution, name="enter_solution"),
]
