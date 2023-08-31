import datetime
from haystack import indexes
from .models import Solution


class SolutionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    is_newest = indexes.BooleanField(model_attr='is_newest')

    def get_model(self):
        return Solution

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(pub_date__lte=datetime.datetime.now())
