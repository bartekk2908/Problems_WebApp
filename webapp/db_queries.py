import manage
manage.main()

from problems_app.models import Solution, Image_feature, User
from django.utils import timezone
from problems_app.utils import *
import json
from bs4 import BeautifulSoup


def reset_table(table):
    table.objects.all().delete()


def show_data(table):
    rows = table.objects.all()
    print(rows)
    for d in rows:
        print(d)
    print(table.objects.values_list('pk', flat=True))


def enter_examples_pl():

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
        text_data = pytania[i] + " " + BeautifulSoup(rozwiazania[i], 'html.parser').get_text().replace('\n', ' ')
        Solution(id=i,
                 problem_content_text=pytania[i],
                 solution_content_richtext=rozwiazania[i],
                 pub_date=timezone.now(),
                 embeddings_json=json.dumps(give_text_embeddings(pytania[i] + " " + rozwiazania[i]).tolist()),
                 is_newest=True,
                 user_fk=User.objects.get(username="admin")).save()


def enter_examples_en():

    # List of questions (problems)
    questions = [
        "Slow website performance.",
        "Lack of task organization.",
        "Low conversion rate on the store's website.",
        "Lack of security in the web application.",
        "Low visibility in search engine results.",
        "Long loading time for the mobile application.",
        "Complicated registration process.",
        "Low user engagement in premium features.",
        "Increased spam on the social media platform.",
        "Lack of consistency in the user interface."
    ]

    # List of solutions
    solutions = [
        "Optimize images and code, leverage browser caching.",
        "Use project management tools like Trello or Asana.",
        "Improve the layout and appearance of the page, apply more persuasive CTAs.",
        "Implement authentication and authorization systems, update dependencies regularly.",
        "Apply SEO optimization strategies, create valuable content.",
        "Optimize files and resources, utilize asynchronous loading techniques.",
        "Simplify forms, implement social media registration.",
        "Provide appealing benefits, offer trial periods.",
        "Implement anti-spam mechanisms, apply content moderation.",
        "Create consistent design guidelines, use shared components."
    ]

    for i in range(len(questions)):
        text_data = questions[i] + " " + BeautifulSoup(solutions[i], 'html.parser').get_text().replace('\n', ' ')
        Solution(id=i,
                 problem_content_text=questions[i],
                 solution_content_richtext=solutions[i],
                 pub_date=timezone.now(),
                 embeddings_json=json.dumps(give_text_embeddings(questions[i] + " " + solutions[i]).tolist()),
                 is_newest=True,
                 user_fk=User.objects.get(username="admin")).save()


if __name__ == "__main__":
    print("\n\n")

    # show_data(Solution)
    # show_data(Image_feature)

    reset_table(Solution)
    reset_table(Image_feature)

    # enter_examples_pl()
    enter_examples_en()

    show_data(Solution)
    show_data(Image_feature)
