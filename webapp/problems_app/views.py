from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.db import transaction

from .forms import Q_Form, S_edit_Form, P_Form
from .utils import *
import json
from PIL import Image
import os
import cv2


temp_dir = "temp_dir/"
if not os.path.isdir(temp_dir):
    os.mkdir(temp_dir)


def main_page(request):

    if request.method == 'POST':
        form = Q_Form(request.POST, request.FILES)
        if form.is_valid():
            query = form.cleaned_data['data']
            file = form.cleaned_data['image']
            if query != "" and file:
                Image.open(file).save(temp_dir + "image.png")
                return redirect("solution", query=query)
            elif query != "":
                return redirect("solution", query=query)
            else:
                # print(os.getcwd())
                Image.open(file).save(temp_dir + "image.png")
                return redirect("solution")
    else:
        form = Q_Form()

    context = {
        'form': form,
    }

    return render(request, 'problems_app/main_page.html', context=context)


def add_solution(request):

    if request.method == 'POST':
        form = P_Form(request.POST)
        if form.is_valid():
            prob = form.cleaned_data['pdata']
            sol = form.cleaned_data['sdata']
            try:
                p = Solutions.objects.get(problem_content_text=prob)
                print("Rozwiązanie tego problemu już istnieje.")
            except Solutions.DoesNotExist:
                text_data = get_text_data(prob, sol)
                print(text_data)
                p = Solutions(problem_content_text=prob,
                              solution_content_richtext=sol,
                              pub_date=timezone.now(),
                              embeddings_json=json.dumps(give_text_embeddings(text_data).tolist()),
                              is_newest=True)
                p.save()
                save_images_features(sol, p)
            return redirect("main_page")
    else:
        form = P_Form()

    context = {
        'form': form,
    }

    return render(request, 'problems_app/add_solution.html', context=context)


def solution(request, query=None, p_id=None):

    n = 100

    if query is not None or os.path.isfile(temp_dir + "image.png"):
        if query is not None and os.path.isfile(temp_dir + "image.png"):
            im = cv2.imread(temp_dir + "image.png")
            sims = get_similar_problems_text_and_images(n, query, im)
            os.remove(temp_dir + "image.png")
        elif query is not None:
            sims = get_similar_problems_text(n, query)
        else:
            im = cv2.imread(temp_dir + "image.png")
            sims = get_similar_problems_images(n, im)
            os.remove(temp_dir + "image.png")
        pk = sims[0]
        others = sims[1:]
    else:
        pk = get_newest_problem(p_id)
        others = get_similar_problems_text(n, get_prob_text(pk), pk=pk)

    prob, sol = get_prob_text(pk), get_sol_text(pk)

    edit_url = reverse("edit_solution", kwargs={"p_id": get_p_id(pk)})

    sim_list = zip(list(map(lambda x: get_prob_text(x), others)),
                   list(map(lambda x: reverse("solution", kwargs={"p_id": get_p_id(x)}), others)))

    context = {
        'problem': prob,
        'solution': sol,
        'edit_url': edit_url,
        'list': sim_list,
    }

    return render(request, 'problems_app/solution.html', context=context)


def edit_solution(request, p_id):
    pk = get_newest_problem(p_id)
    prob = get_prob_text(pk)

    if request.method == 'POST':
        form = S_edit_Form(request.POST)
        if form.is_valid():

            sol = form.cleaned_data['data']

            text_data = get_text_data(prob, sol)
            print(text_data)

            with transaction.atomic():
                old = Solutions.objects.get(problem_id=p_id, is_newest=True)
                old.is_newest = False
                old.save()
                new = Solutions(problem_id=p_id,
                                problem_content_text=prob,
                                solution_content_richtext=sol,
                                pub_date=timezone.now(),
                                embeddings_json=json.dumps(give_text_embeddings(text_data).tolist()),
                                is_newest=True)
                new.save()
                save_images_features(sol, new)
            return redirect("solution", p_id=p_id)
    else:
        form = S_edit_Form(initial={"data": get_sol_text(get_newest_problem(p_id))})

    context = {
        'problem': prob,
        'form': form,
    }

    return render(request, 'problems_app/edit_solution.html', context=context)


def all_solutions(request, sorting, direction):

    alls = get_all_problems(sorting_by=sorting, direction=direction)

    all_list = zip(list(map(lambda x: get_prob_text(x), alls)),
                   list(map(lambda x: reverse("solution", kwargs={"p_id": get_p_id(x)}), alls)))

    context = {
        'list': all_list,
        'sorting': sorting,
        'direction': direction,
    }

    return render(request, 'problems_app/all_solutions.html', context=context)
