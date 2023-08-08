from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse

from .models import Problems
from .forms import PForm, SForm


def enter_problem(request):
    if request.method == 'POST':
        pform = PForm(request.POST)
        if pform.is_valid():
            problem = pform.cleaned_data['pdata']

            try:
                data = Problems.objects.get(problem_content_text=problem)
                p_id = data.id
                return redirect("solution", p_id=p_id)
            except Problems.DoesNotExist:
                return redirect("no_solution")
    else:
        pform = PForm()

    context = {
        'form': pform,
    }

    return render(request, 'problems_app/enter_problem.html', context=context)


def solution(request, p_id):

    sol = Problems.objects.get(id=p_id).solution_content_text

    context = {
        'p_id': p_id,
        'solution': sol
    }

    return render(request, 'problems_app/solution.html', context=context)


def no_solution(request):
    context = {
        'form': SForm(),
    }
    return render(request, 'problems_app/no_solution.html', context=context)
