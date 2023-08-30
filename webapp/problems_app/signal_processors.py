from .models import Solution
from django.db import models
from haystack import signals


class SolutionOnlySignalProcessor(signals.BaseSignalProcessor):
    def setup(self):
        # Listen only to the `Solution` model.
        models.signals.post_save.connect(self.handle_save, sender=Solution)
        models.signals.post_delete.connect(self.handle_delete, sender=Solution)

    def teardown(self):
        # Disconnect only for the `Solution` model.
        models.signals.post_save.disconnect(self.handle_save, sender=Solution)
        models.signals.post_delete.disconnect(self.handle_delete, sender=Solution)
