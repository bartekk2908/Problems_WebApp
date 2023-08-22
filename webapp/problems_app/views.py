from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.db import transaction

from .forms import Q_Form, S_edit_Form, P_Form
from .utils import *
import json
from PIL import Image
import base64
from io import BytesIO


def main_page(request):

    if request.method == 'POST':
        form = Q_Form(request.POST, request.FILES)
        if form.is_valid():
            query = form.cleaned_data['data']
            file = form.cleaned_data['image']
            if query != "":
                return redirect("solution", query=query)
            elif file:
                im = Image.open(file)
                buffered = BytesIO()
                im.save(buffered, format="PNG")
                im_str = base64.b64encode(buffered.getvalue())
                print()
                print(im_str)
                request.session['image'] = str(im_str)
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
                p = Problems.objects.get(problem_content_text=prob)
                print("Rozwiązanie tego problemu już istnieje.")
            except Problems.DoesNotExist:
                text_data = get_text_data(prob, sol)
                print(text_data)
                p = Problems(problem_content_text=prob,
                             solution_content_richtext=sol,
                             pub_date=timezone.now(),
                             embeddings_json=json.dumps(give_embeddings(text_data).tolist()),
                             is_newest=True)
                p.save()
                save_images(sol, p)
            return redirect("main_page")
    else:
        form = P_Form()

    context = {
        'form': form,
    }

    return render(request, 'problems_app/add_solution.html', context=context)


def solution(request, query=None, p_id=None):

    n = len(get_all_problems())

    im_str = request.session.get('image', None)

    if im_str is not None or query is not None:
        if im_str is not None:
            Image.open(BytesIO(base64.b64encode(bytes(im_str, "utf-8")))).show()
            # sims = get_similar_problems_images(n, im)
        else:
            sims = get_similar_problems(n, query)
        pk = sims[0]
        others = sims[1:]
    else:
        pk = get_newest_problem(p_id)
        others = get_similar_problems(n, get_prob_text(pk), pk=pk)

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
                save_images(sol, new)
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
