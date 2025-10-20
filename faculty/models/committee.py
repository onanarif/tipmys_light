from django.db import models
from django.urls import reverse
from django.utils import timezone
import datetime
from .fct_profile import FacultyProfile

class Committee(models.Model):
    name = models.CharField(max_length=100)
    phase = models.ForeignKey(
        'Program',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    chair = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE,  related_name='fct_committee') # allows reverse access from FacultyProfile to Committeedepot objects
    start_date = models.DateField(default=datetime.date.today)
    end_date = models.DateField(default=datetime.date.today)    

    def get_absolute_url(self):
        return reverse('faculty:committee_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name
