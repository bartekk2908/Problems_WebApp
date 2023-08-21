import manage
manage.main()

from problems_app.models import Problems
from django.utils import timezone
from problems_app.utils import give_similar_problems, give_embeddings
import json
from bs4 import BeautifulSoup


def reset_table():
    Problems.objects.all().delete()


def show_data():
    problems = Problems.objects.all()
    for p in problems:
        print(p)

    print(Problems.objects.values_list('pk', flat=True))


def testing_s():
    print(give_similar_problems("Loro nie wiem co to amen", 5))


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
        Problems(id=i, problem_content_text=pytania[i],
                 solution_content_richtext=rozwiazania[i],
                 pub_date=timezone.now(),
                 embeddings_json=json.dumps(give_embeddings(pytania[i] + " " + rozwiazania[i]).tolist()),
                 is_newest=True).save()


if __name__ == "__main__":
    print("\n\n")

    show_data()
    reset_table()
    enter_examples_pl()
    show_data()
