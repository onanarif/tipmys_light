from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from faculty.models import FacultyProfile, Committee, Department
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

class CourseMaster(models.Model):

    name = models.CharField(max_length=255, default="")
    lecturer = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE, default=207, related_name='fct_courses')
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE, default=4, related_name='cmt_courses') 
    department = models.ForeignKey(Department, on_delete=models.CASCADE, default=1, related_name='dpt_courses') 
    multilecture = models.BooleanField(default=False)
    event_count = models.PositiveSmallIntegerField(default=1)    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    type = models.ForeignKey("faculty.CourseType", on_delete=models.CASCADE, default=1)
    active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    event_count = models.PositiveSmallIntegerField(default=1)
    question_set = models.PositiveSmallIntegerField(default=1)
    final_question_set = models.PositiveSmallIntegerField(default=1)   

    class Meta:
        db_table = 'course_master'
        verbose_name = 'Ders'
        verbose_name_plural = 'Dersler'        

    def __str__(self):
        return self.name 

