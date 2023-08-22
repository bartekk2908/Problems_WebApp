import manage
manage.main()

from problems_app.models import Problems, Images
from django.utils import timezone
from problems_app.utils import give_embeddings
import json
from bs4 import BeautifulSoup
import imgkit


def reset_table(table):
    table.objects.all().delete()


def show_data(table):
    rows = table.objects.all()
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
        Problems(id=i,
                 problem_content_text=pytania[i],
                 solution_content_richtext=rozwiazania[i],
                 pub_date=timezone.now(),
                 embeddings_json=json.dumps(give_embeddings(pytania[i] + " " + rozwiazania[i]).tolist()),
                 is_newest=True).save()


def show_images():
    images = Images.objects.all()
    for im in images:
        img = imgkit.from_string(im.image_richtext, False)
        img.show()


if __name__ == "__main__":
    print("\n\n")

    show_data(Problems)
    show_data(Images)

    # reset_table(Problems)
    # reset_table(Images)

    # enter_examples_pl()

    # show_images()
