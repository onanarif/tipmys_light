from django.db import models
from django.urls import reverse
from .department import Department
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver

class FacultyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    faculty_id = models.IntegerField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.DO_NOTHING, default=1)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name