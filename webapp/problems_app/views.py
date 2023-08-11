from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse

from .models import Problems
from .forms import Q_Form, S_edit_Form, P_Form
from django.utils import timezone
from .utils import give_sol, similar_problems, give_embeddings
import json
from bs4 import BeautifulSoup


def main_page(request):

    url_eq = reverse("enter_query")
    url_ep = reverse("enter_problem")

    context = {
        "url_eq": url_eq,
        "url_ep": url_ep,
    }

    return render(request, 'problems_app/main_page.html', context=context)


def enter_problem(request):

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

    return render(request, 'problems_app/enter_problem.html', context=context)


def enter_query(request):

    if request.method == 'POST':
        form = Q_Form(request.POST)
        if form.is_valid():
            query = form.cleaned_data['data']
            return redirect("solution", query=query)
    else:
        form = Q_Form()

    context = {
        'form': form,
    }

    return render(request, 'problems_app/enter_query.html', context=context)


def solution(request, query):

    n = 3
    sims = similar_problems(query, n=n)

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
