from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.db import transaction

from .forms import Q_Form, Image_Form, S_edit_Form, P_Form
from .utils import *
import json
from PIL import Image


def main_page(request):

    if request.method == 'POST':
        form = Q_Form(request.POST)
        im_form = Image_Form(request.POST, request.FILES)
        if form.is_valid() and im_form.is_valid():
            query = form.cleaned_data['data']

            file = im_form.cleaned_data['image']
            im = Image.open(file)
            im.show()

            return redirect("solution", query=query)
    else:
        form = Q_Form()
        im_form = Image_Form

    url_as = reverse("add_solution")

    context = {
        "url_as": url_as,
        'form': form,
        'im_form': im_form,
    }

    return render(request, 'problems_app/main_page.html', context=context)


def add_solution(request):

    if request.method == 'POST':
        form = P_Form(request.POST)
        if form.is_valid():
            prob = form.cleaned_data['pdata']
            sol = form.cleaned_data['sdata']
            try:
                p = Problems.objects.get(problem_content_text=prob)
                print("Rozwiązanie tego problemu już istnieje.")
            except Problems.DoesNotExist:
                text_data = give_text_data(prob, sol)
                print(text_data)
                p = Problems(problem_content_text=prob,
                             solution_content_richtext=sol,
                             pub_date=timezone.now(),
                             embeddings_json=json.dumps(give_embeddings(text_data).tolist()),
                             is_newest=True)
                p.save()
            return redirect("main_page")
    else:
        form = P_Form()

    context = {
        'form': form,
    }

    return render(request, 'problems_app/add_solution.html', context=context)


def solution(request, query=None, p_id=None):

    n = len(give_all_problems())

    if query is not None:
        sims = give_similar_problems(n, query)
        pk = sims[0]
        others = sims[1:]
    else:
        pk = give_newest_problem(p_id)
        others = give_similar_problems(n, give_prob_text(pk), pk=pk)

    prob, sol = give_prob_text(pk), give_sol_text(pk)

    edit_url = reverse("edit_solution", kwargs={"p_id": give_p_id(pk)})

    sim_list = zip(list(map(lambda x: give_prob_text(x), others)),
                   list(map(lambda x: reverse("solution", kwargs={"p_id": give_p_id(x)}), others)))

    context = {
        'problem': prob,
        'solution': sol,
        'edit_url': edit_url,
        'list': sim_list,
    }

    return render(request, 'problems_app/solution.html', context=context)


def edit_solution(request, p_id):
    pk = give_newest_problem(p_id)
    prob = give_prob_text(pk)

    if request.method == 'POST':
        form = S_edit_Form(request.POST)
        if form.is_valid():

            sol = form.cleaned_data['data']

            text_data = give_text_data(prob, sol)
            print(text_data)

            with transaction.atomic():
                old = Problems.objects.get(problem_id=p_id, is_newest=True)
                old.is_newest = False
                old.save()
                new = Problems(problem_id=p_id,
                               problem_content_text=prob,
                               solution_content_richtext=sol,
                               pub_date=timezone.now(),
                               embeddings_json=json.dumps(give_embeddings(text_data).tolist()),
                               is_newest=True)
                new.save()

            return redirect("solution", p_id=p_id)
    else:
        form = S_edit_Form(initial={"data": give_sol_text(give_newest_problem(p_id))})

    context = {
        'problem': prob,
        'form': form,
    }

    return render(request, 'problems_app/edit_solution.html', context=context)


def all_solutions(request, sorting, direction):

    alls = give_all_problems(sorting_by=sorting, direction=direction)

    all_list = zip(list(map(lambda x: give_prob_text(x), alls)),
                   list(map(lambda x: reverse("solution", kwargs={"p_id": give_p_id(x)}), alls)))

    context = {
        'list': all_list,
        'sorting': sorting,
        'direction': direction,
    }

    return render(request, 'problems_app/all_solutions.html', context=context)
