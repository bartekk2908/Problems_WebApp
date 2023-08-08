import manage
manage.main()

from problems_app.models import Problems
from django.utils import timezone


def reset_table():
    Problems.objects.all().delete()


if __name__ == "__main__":
    print("\n\n")

    # reset_table()

    # Problems(id=1, problem_content_text="Elo", solution_content_text="Tak", pub_date=timezone.now()).save()

    print(Problems.objects.all())

    print(Problems.objects.values_list('pk', flat=True))

    reset_table()
