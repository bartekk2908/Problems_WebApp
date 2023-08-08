from .models import Problems


def give_sol(problem):
    try:
        sol = Problems.objects.get(problem_content_text=problem).solution_content_text
    except Problems.DoesNotExist:
        sol = ""
    return sol


def similar_problems(problem, n):
    p_list = []

    for _ in range(n):
        

    return p_list
