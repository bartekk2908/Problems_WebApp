import datetime
from haystack import indexes
from .models import Solution


class SolutionIndex(indexes.SearchIndex, indexes.Indexable):
    elo = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Solution

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(pub_date__lte=datetime.datetime.now())
