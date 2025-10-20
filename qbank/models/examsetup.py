from django.db import models
from django.utils import timezone
from faculty.models.program import Program
from faculty.models.committee import Committee
from django.core.exceptions import ValidationError


class ExamSetup(models.Model):
    EXAM_TYPES = [
        ('theoric', 'Teorik'),
        ('pratic', 'Pratik'),
        ('final', 'Final'),
        ('final_pratic', 'Final Pratik'),
    ]
    name = models.CharField(max_length=100)
    date = models.DateTimeField(blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    finish = models.DateTimeField(blank=True, null=True)
    qtotal = models.IntegerField(blank=True, null=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, default=1)
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE, default=1)
    type = models.CharField(max_length=12, choices=EXAM_TYPES, default='theoric')
    apply_penalty = models.BooleanField(default=True, help_text="If true, apply baraj/penalty scoring rule to all students")
    locked = models.BooleanField(default=False)


    class Meta:
        ordering = ['-date', 'start']
    
    def __str__(self):
        #return self.name
        return f"{self.name} ({self.get_type_display()}) - {self.date.strftime('%Y-%m-%d') if self.date else 'No date'}"

