from django.db import models
from django.urls import reverse
class AcadYear(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return self.name