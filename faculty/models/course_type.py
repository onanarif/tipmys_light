from django.db import models
from .acadyear import AcadYear

class CourseType(models.Model):
    TYPE_CHOICES = (
        ('Teorik Yüzyüze', 'Teorik Yüzyüze'),
        ('Teorik Tersyüz Video', 'Teorik Tersyüz Video'),
        ('Teorik Tersyüz Tartışma', 'Teorik Tersyüz Tartışma'),
        ('Uygulama', 'Uygulama'),       
    )
    name = models.CharField(max_length=25, choices=TYPE_CHOICES)
    acadyear = models.ForeignKey(AcadYear, on_delete= models.CASCADE)
    def __str__(self):
        return self.name