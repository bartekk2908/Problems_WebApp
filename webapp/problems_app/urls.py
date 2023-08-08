from django.urls import path

from . import views

urlpatterns = [
    path("problems/", views.enter_problem, name="enter_problem"),
    path("problems/solution/prob=<str:problem>/", views.solution, name="solution"),
    path("problems/solution/prob=<str:problem>/enter/", views.enter_solution, name="enter_solution"),
]
