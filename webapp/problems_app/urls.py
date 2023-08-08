from django.urls import path

from . import views

urlpatterns = [
    path("problems/", views.enter_problem, name="enter_problem"),
    path("problems/no_solution/", views.no_solution, name="no_solution"),
    path("problems/solution/<int:p_id>/", views.solution, name="solution"),
]
