from django.urls import path

from . import views

urlpatterns = [
    path("enter_problem/", views.enter_problem, name="enter_problem"),
]
