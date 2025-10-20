from django.db import models
from .acadyear import AcadYear

class Program(models.Model):
    PHASE_CHOICES = (
        ('Dönem I', 'Dönem I'),
        ('Dönem II', 'Dönem II'),
        ('Dönem III', 'Dönem III'),
        ('Dönem IV', 'Dönem IV'),       
        ('Dönem V', 'Dönem V'),
        ('Dönem VI', 'Dönem VI'),
        ('Dönem I_VI', 'Dönem I_VI'),
    )
    name = models.CharField(max_length=10, choices=PHASE_CHOICES)
    #acadyear = models.ForeignKey(AcadYear, on_delete= models.CASCADE)
    def __str__(self):
        return self.name