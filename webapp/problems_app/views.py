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
import glob


temp_dir = "temp_dir/"
if not os.path.isdir(temp_dir):
    os.mkdir(temp_dir)


def login_view(request):

    if request.method == 'POST':
        form = LoginForm(request.POST)
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
        form = LoginForm()

    context = {
        'form': form,
    }
    return render(request, 'authentication/login.html', context=context)


@login_required
def logout_view(request):
    previous_page = request.session.get('previous_page', 'main_page')
    logout(request)
    return redirect(previous_page)


@login_required
def main_page(request):

    if request.method == 'POST':
        """
        form = QForm(request.POST, request.FILES)
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
        """
        form_v2 = QFormv2(request.POST)
        if form_v2.is_valid():
            richtext = form_v2.cleaned_data['richtext']
            query = richtext_to_text(richtext)
            images_data = richtext_to_img_base64(richtext)
            if images_data:
                for i in range(len(images_data)):
                    with open(temp_dir + f'{i}.png', 'wb') as f:
                        f.write(base64.b64decode(images_data[i]))

            if query != "" and images_data:
                # zapisz obrazy
                return redirect("solution", query=query)
            elif query != "":
                return redirect("solution", query=query)
            else:
                # zapisz obrazy
                return redirect("solution")
    else:
        # form = QForm()
        form_v2 = QFormv2()

    request.session["previous_page"] = request.path
    context = {
        # 'form': form,
        'form_v2': form_v2,
    }
    return render(request, 'problems_app/main_page.html', context=context)


@login_required
def add_solution(request):

    if request.method == 'POST':
        form = PForm(request.POST)
        if form.is_valid():
            prob = form.cleaned_data['pdata']
            sol = form.cleaned_data['sdata']
            try:
                p = Solution.objects.get(problem_content_text=prob)
                print("Rozwiązanie tego problemu już istnieje.")
                form = PForm(initial={"pdata": prob, "sdata": sol})
            except Solution.DoesNotExist:
                p = Solution(problem_content_text=prob,
                             solution_content_richtext=sol,
                             user=request.user)
                p.save()
                p.save_images_features()
                return redirect("main_page")
    else:
        form = PForm()

    context = {
        'form': form,
    }
    return render(request, 'problems_app/add_solution.html', context=context)


@login_required
def search(request, query=None):
    n = 100

    images_paths = glob.glob(temp_dir + "*.png")

    if query is not None and images_paths:
        images = [cv2.imread(path) for path in images_paths]
        sims = get_similar_problems_text_and_images(n, query, images)
        [os.remove(path) for path in images_paths]
    elif query is not None:
        sims = search_solutions(query, n)
        # sims = get_similar_problems_text(n, query)
    elif images_paths:
        images = [cv2.imread(path) for path in images_paths]
        sims = get_similar_problems_multiple_images(n, images)
        [os.remove(path) for path in images_paths]
    else:
        sims = request.session.get("sims_list", [])

    request.session["sims_list"] = [int(x) for x in print_pks(sims)]
    request.session["previous_page"] = request.path
    context = {
        'sims': sims,
    }
    return render(request, 'problems_app/search.html', context=context)


@login_required
def solution(request, solution_id):
    obj = get_newest_solution(solution_id)

    context = {
        'obj': obj,
    }
    return render(request, 'problems_app/solution.html', context=context)


@login_required
def edit_solution(request, solution_id):
    obj = get_newest_solution(solution_id)
    is_edited = True
    if request.method == 'POST':
        form = SEditForm(request.POST)
        if form.is_valid():
            sol = form.cleaned_data['data']
            if sol == obj.solution_content_richtext:
                is_edited = False
            else:
                new = Solution(solution_id=solution_id,
                               problem_content_text=obj.problem_content_text,
                               solution_content_richtext=sol,
                               user=request.user)
                new.save()
                new.save_images_features()
                return redirect("solution", solution_id=solution_id)
    else:
        form = SEditForm(initial={"data": obj.solution_content_richtext})

    context = {
        'obj': obj,
        'form': form,
        'is_edited': is_edited,
    }
    return render(request, 'problems_app/edit_solution.html', context=context)


@login_required
def all_solutions(request, sorting, direction):
    alls = get_all_solutions(sorting_by=sorting, direction=direction)

    request.session["previous_page"] = request.path
    context = {
        'alls': alls,
        'sorting': sorting,
        'direction': direction,
    }
    return render(request, 'problems_app/all_solutions.html', context=context)
