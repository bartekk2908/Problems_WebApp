from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse

from .models import Problems
from .forms import Q_Form, S_edit_Form, P_Form
from django.utils import timezone
from .utils import give_sol, give_similar_problems, give_embeddings, give_all_problems
import json
from bs4 import BeautifulSoup


def main_page(request):

    if request.method == 'POST':
        form = Q_Form(request.POST)
        if form.is_valid():
            query = form.cleaned_data['data']
            return redirect("solution", query=query)
    else:
        form = Q_Form()

    url_ep = reverse("add_solution")

    context = {
        "url_ep": url_ep,
        'form': form,
    }

    return render(request, 'problems_app/main_page.html', context=context)


def add_solution(request):

    if request.method == 'POST':
        form = P_Form(request.POST)
        if form.is_valid():
            problem = form.cleaned_data['pdata']
            sol = form.cleaned_data['sdata']
            try:
                p = Problems.objects.get(problem_content_text=problem)
                print("Rozwiązanie tego problemu już istnieje.")
            except:
                text_data = problem + " " + BeautifulSoup(sol, 'html.parser').get_text().replace('\n', ' ')
                print(text_data)
                p = Problems(problem_content_text=problem,
                             solution_content_richtext=sol,
                             pub_date=timezone.now(),
                             embeddings_json=json.dumps(give_embeddings(text_data).tolist()))
                p.save()
            return redirect("main_page")
    else:
        form = P_Form()

    context = {
        'form': form,
    }

    return render(request, 'problems_app/add_solution.html', context=context)


def solution(request, query):

    n = 10
    sims = give_similar_problems(query, n=n)

    problem = sims[0]
    sol = give_sol(problem)

    enter_url = reverse("edit_solution", kwargs={"problem": problem})

    sim_list = zip(sims[1:], list(map(lambda x: reverse("solution", kwargs={"query": x}), sims[1:])))

    context = {
        'problem': problem,
        'solution': sol,
        'enter_url': enter_url,
        'list': sim_list,
    }

    return render(request, 'problems_app/solution.html', context=context)


def edit_solution(request, problem):

    if request.method == 'POST':
        form = S_edit_Form(request.POST)
        if form.is_valid():
            sol = form.cleaned_data['data']
            p = Problems.objects.get(problem_content_text=problem)
            p.solution_content_richtext = sol
            p.pub_date = timezone.now()
            p.save()
            return redirect("solution", query=problem)
    else:
        form = S_edit_Form(initial={"data": give_sol(problem)})

    context = {
        'problem': problem,
        'form': form,
    }

    return render(request, 'problems_app/edit_solution.html', context=context)


def all_solutions(request, sorting, direction):

    alls = give_all_problems(sorting_by=sorting, direction=direction)

    all_list = zip(alls, list(map(lambda x: reverse("solution", kwargs={"query": x}), alls)))

    context = {
        'list': all_list,
        'sorting': sorting,
        'direction': direction,
    }

    return render(request, 'problems_app/all_solutions.html', context=context)
