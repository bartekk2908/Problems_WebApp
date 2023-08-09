from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse

from .models import Problems
from .forms import PForm, SForm
from django.utils import timezone
from .utils import give_sol, similar_problems


def main_page(request):

    url = reverse("enter_query")

    context = {
        "url": url,
    }

    return render(request, 'problems_app/main_page.html', context=context)


def enter_query(request):
    if request.method == 'POST':
        form = PForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['pdata']
            return redirect("solution", query=query)
    else:
        form = PForm()

    context = {
        'form': form,
    }

    return render(request, 'problems_app/enter_query.html', context=context)


def solution(request, query):
    sims = similar_problems(query, 3)

    problem = sims[0]
    sol = give_sol(problem)

    enter_url = reverse("enter_solution", kwargs={"problem": problem})

    sim_list = zip(sims, list(map(lambda x: reverse("solution", kwargs={"query": x}), sims[1:])))

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
            return redirect("solution", query=problem)
    else:
        form = SForm(initial={"sdata": give_sol(problem)})

    context = {
        'form': form,
    }

    return render(request, 'problems_app/enter_solution.html', context=context)

