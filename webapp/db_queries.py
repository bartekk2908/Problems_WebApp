import manage
manage.main()

from problems_app.models import Problems
from django.utils import timezone
from problems_app.utils import similar_problems


def reset_table():
    Problems.objects.all().delete()


def testing_1():
    # reset_table()
    # Problems(id=1, problem_content_text="Elo", solution_content_text="Tak", pub_date=timezone.now()).save()
    print(Problems.objects.all())
    print(Problems.objects.values_list('pk', flat=True))
    # reset_table()


def testing_s():
    print(similar_problems("Loro nie wiem co to amen", 3))


def enter_examples():

    # Lista pytań (problemy)
    pytania = [
        "Spowolniona strona internetowa.",
        "Brak organizacji w zadaniach.",
        "Niski współczynnik konwersji na stronie sklepu.",
        "Brak bezpieczeństwa w aplikacji internetowej.",
        "Niska widoczność w wynikach wyszukiwania.",
        "Długi czas ładowania aplikacji mobilnej.",
        "Skomplikowany proces rejestracji.",
        "Niski udział użytkowników w funkcjonalnościach premium.",
        "Zwiększona ilość spamu na platformie społecznościowej.",
        "Brak spójności w interfejsie użytkownika."
    ]

    # Lista rozwiązań
    rozwiazania = [
        "Zoptymalizować obrazy i kod, skorzystać z buforowania przeglądarki.",
        "Używać narzędzi do zarządzania projektami, takich jak Trello lub Asana.",
        "Poprawić układ i wygląd strony, zastosować bardziej przekonujące CTA.",
        "Wdrożyć system uwierzytelniania i autoryzacji, aktualizować regularnie zależności.",
        "Zastosować strategie optymalizacji SEO, tworzyć wartościową treść.",
        "Zoptymalizować pliki i zasoby, wykorzystać techniki ładowania asynchronicznego.",
        "Uproszczenie formularzy, wdrożenie rejestracji za pomocą kont społecznościowych.",
        "Dostarczyć atrakcyjne korzyści, oferować okresy próbne.",
        "Wdrożyć mechanizmy antyspamowe, zastosować moderację treści.",
        "Stworzyć jednolite wytyczne projektowe, używać wspólnych komponentów."
    ]

    for i in range(len(pytania)):
        Problems(id=i, problem_content_text=pytania[i], solution_content_text=rozwiazania[i], pub_date=timezone.now()).save()


def enter_examples_2():

    # List of questions (problems)
    questions = [
        "Sluggish website performance.",
        "Lack of task organization.",
        "Low conversion rate on the store website.",
        "Lack of security in the web application.",
        "Low visibility in search results.",
        "Long loading time for mobile application.",
        "Complex registration process.",
        "Low user engagement in premium features.",
        "Increased spam on the social media platform.",
        "Lack of consistency in the user interface."
    ]

    # List of solutions
    solutions = [
        "Optimize images and code, leverage browser caching.",
        "Use project management tools like Trello or Asana.",
        "Improve layout and design, implement more persuasive CTAs.",
        "Implement authentication and authorization system, regularly update dependencies.",
        "Apply SEO optimization strategies, create valuable content.",
        "Optimize files and resources, use asynchronous loading techniques.",
        "Simplify forms, implement registration via social accounts.",
        "Provide appealing benefits, offer trial periods.",
        "Implement anti-spam mechanisms, apply content moderation.",
        "Create consistent design guidelines, use shared components."
    ]

    for i in range(len(questions)):
        Problems(id=i, problem_content_text=questions[i], solution_content_text=solutions[i], pub_date=timezone.now()).save()


if __name__ == "__main__":
    print("\n\n")

    reset_table()
    enter_examples()
