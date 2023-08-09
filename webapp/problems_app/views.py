from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse

from .models import Problems
from .forms import PForm, SForm
from django.utils import timezone
from .utils import give_sol, similar_problems


def enter_problem(request):
    if request.method == 'POST':
        form = PForm(request.POST)
        if form.is_valid():
            problem = form.cleaned_data['pdata']
            return redirect("solution", problem=problem)
    else:
        form = PForm()

    context = {
        'form': form,
    }

    return render(request, 'problems_app/enter_problem.html', context=context)


def solution(request, problem):

    sol = give_sol(problem)

    enter_url = reverse("enter_solution", kwargs={"problem": problem})

    if sol == "":
        sims = similar_problems(problem, 3)
        sim_list = zip(sims, list(map(lambda x: reverse("solution", kwargs={"problem": x}), sims)))
    else:
        sim_list = []

    context = {
        'problem': problem,
        'solution': sol,
        'enter_url': enter_url,
        'list': sim_list,
    }

    return render(request, 'problems_app/solution.html', context=context)


def enter_solution(request, problem):

    if request.method == 'POST':
        form = SForm(request.POST)
        if form.is_valid():
            given_solution = form.cleaned_data['sdata']
            try:
                p = Problems.objects.get(problem_content_text=problem)
                p.solution_content_text = given_solution
            except:
                p = Problems(problem_content_text=problem, solution_content_text=given_solution,
                             pub_date=timezone.now())
            p.save()
            return redirect("solution", problem=problem)
    else:
        form = SForm(initial={"sdata": give_sol(problem)})

    context = {
        'form': form,
    }

    return render(request, 'problems_app/enter_solution.html', context=context)

