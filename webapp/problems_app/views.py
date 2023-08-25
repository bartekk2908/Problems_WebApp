from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from .forms import *
from .models import *
from PIL import Image
import os
import cv2


temp_dir = "temp_dir/"
if not os.path.isdir(temp_dir):
    os.mkdir(temp_dir)


def login_view(request):

    if request.method == 'POST':
        form = Login_Form(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                print(f"Zalogowany jako: {user.username}")
                return redirect("main_page")
                # previous_page = request.session.get('previous_page', 'main_page')
                # return redirect(previous_page)
            else:
                print(f'Logowanie nie powiodło się.')
    else:
        form = Login_Form()

    context = {
        'form': form,
    }
    return render(request, 'authentication/login.html', context=context)


@login_required
def logout_view(request):
    previous_page = request.session.get('previous_page', 'main_page')
    logout(request)
    return redirect(previous_page)


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

    request.session["previous_page"] = request.path
    context = {
        'form': form,
    }
    return render(request, 'problems_app/main_page.html', context=context)


@login_required
def add_solution(request):

    if request.method == 'POST':
        form = P_Form(request.POST)
        if form.is_valid():
            prob = form.cleaned_data['pdata']
            sol = form.cleaned_data['sdata']
            try:
                p = Solution.objects.get(problem_content_text=prob)
                print("Rozwiązanie tego problemu już istnieje.")
            except Solution.DoesNotExist:
                p = Solution(problem_content_text=prob,
                             solution_content_richtext=sol)
                p.save()
            return redirect("main_page")
    else:
        form = P_Form()

    context = {
        'form': form,
    }
    return render(request, 'problems_app/add_solution.html', context=context)


@login_required
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
            sims = get_similar_problems_images(n, im, limit=10.0)
            os.remove(temp_dir + "image.png")
        pk = sims[0]
        others = sims[1:]
    elif p_id is not None:
        pk = get_newest_solution(p_id)
        others = get_similar_problems_text(n, get_prob_text(pk), pk=pk)     # FIXME
    else:
        sims = request.session.get("sims_list", [])
        pk = sims[0]
        others = sims[1:]

    prob, sol = get_prob_text(pk), get_sol_text(pk)

    edit_url = reverse("edit_solution", kwargs={"p_id": get_p_id(pk)})

    sim_list = zip(list(map(lambda x: get_prob_text(x), others)),
                   list(map(lambda x: reverse("solution", kwargs={"p_id": get_p_id(x)}), others)))

    request.session["sims_list"] = [int(x) for x in [pk] + others]
    request.session["previous_page"] = request.path
    context = {
        'problem': prob,
        'solution': sol,
        'edit_url': edit_url,
        'list': sim_list,
        'pk': pk,
    }
    return render(request, 'problems_app/solution.html', context=context)


@login_required
def edit_solution(request, p_id):
    pk = get_newest_solution(p_id)
    prob = get_prob_text(pk)

    if request.method == 'POST':
        form = S_edit_Form(request.POST)
        if form.is_valid():

            sol = form.cleaned_data['data']

            new = Solution(problem_id=p_id,
                           problem_content_text=prob,
                           solution_content_richtext=sol)
            new.save()
            return redirect("solution", p_id=p_id)
    else:
        form = S_edit_Form(initial={"data": get_sol_text(get_newest_solution(p_id))})

    context = {
        'problem': prob,
        'form': form,
    }
    return render(request, 'problems_app/edit_solution.html', context=context)


@login_required
def all_solutions(request, sorting, direction):

    alls = get_all_solutions(sorting_by=sorting, direction=direction)

    all_list = zip(list(map(lambda x: get_prob_text(x), alls)),
                   list(map(lambda x: reverse("solution", kwargs={"p_id": get_p_id(x)}), alls)))

    request.session["previous_page"] = request.path
    context = {
        'list': all_list,
        'sorting': sorting,
        'direction': direction,
    }
    return render(request, 'problems_app/all_solutions.html', context=context)
