from django.db import models
from django.urls import reverse
class Department(models.Model):
    class Division(models.TextChoices):
        TEMEL = "Temel Bilimler", 'Temel Bilimler'
        DAHILI = "Dahili Bilimler", 'Dahili Bilimler'
        CERRAHI = "Cerrahi Bilimler", 'Cerrahi Bilimler'
    division = models.CharField(max_length=50, choices=Division.choices)
    name = models.CharField(max_length=100, null=False, blank=False)

    def get_absolute_url(self):
        return reverse('department-detail', args=[str(self.id)])

    def __str__(self):
        return self.division + " - " + self.name