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


if __name__ == "__main__":
    print("\n\n")

    testing_1()
