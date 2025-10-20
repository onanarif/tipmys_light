from django.utils import timezone
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.apps import apps
from django.contrib.auth.models import User 
from .course_master import CourseMaster
from faculty.models import FacultyProfile


class CourseQuestionDepot(models.Model):
    QUESTION_TYPES = [
        ('theoric', 'Theoric'),
        ('pratic', 'Pratic'),
        # Add other types if needed
    ]
    master = models.ForeignKey(CourseMaster, on_delete=models.CASCADE, default=1, related_name='questions')
    name = models.CharField(max_length=255, default="Please fill this field")
    question_text = models.TextField()
    general_feedback = models.TextField(blank=True, default="")
    default_grade = models.DecimalField(max_digits=10, decimal_places=7, default=0.0)
    penalty = models.DecimalField(max_digits=10, decimal_places=7, default=0.0)
    hidden = models.BooleanField(default=False)
    id_number = models.CharField(max_length=255, blank=True, null=True)
    single = models.BooleanField(default=True)
    shuffle_answers = models.BooleanField(default=True)
    answer_numbering = models.CharField(max_length=10, default="ABCD")
    show_standard_instruction = models.BooleanField(default=True)
    correct_feedback = models.TextField(blank=True, default="Doğru cevap.")
    partially_correct_feedback = models.TextField(blank=True, default="Kısmi olarak doğru.")
    incorrect_feedback = models.TextField(blank=True, default="Yanlış cevap.")
    show_num_correct = models.CharField(max_length=10, default="Yes")
    answer_1_fraction = models.DecimalField(max_digits=10, decimal_places=7, default=0.0)
    answer_1_text = models.TextField(default="Please fill this field")
    answer_2_fraction = models.DecimalField(max_digits=10, decimal_places=7, default=0.0)
    answer_2_text = models.TextField(default="Please fill this field")
    answer_3_fraction = models.DecimalField(max_digits=10, decimal_places=7, default=0.0)
    answer_3_text = models.TextField(default="Please fill this field")
    answer_4_fraction = models.DecimalField(max_digits=10, decimal_places=7, default=0.0)
    answer_4_text = models.TextField(default="Please fill this field")
    answer_5_fraction = models.DecimalField(max_digits=10, decimal_places=7, default=0.0)
    answer_5_text = models.TextField(default="Please fill this field")
    correct_answer = models.CharField(max_length=10, default="Please fill this field")
    tag_1 = models.CharField(max_length=255, default="Please fill this field", verbose_name="name")
    tag_2 = models.CharField(max_length=255, default="Please fill this field", verbose_name="lecturer")
    lecturer = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE, default=1)
    type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='theoric')
    picture = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name + " | Ders: " + self.tag_1 + " | Öğretim Elemanı: " +self.tag_2

    # ---- helpful validators ----
    def clean(self):
        super().clean()
        # must have a correct answer
        if not self.correct_answer:
            raise ValidationError({"correct_answer": "Doğru cevap seçilmelidir."})
        # ensure chosen letter's text is not empty
        mapping = {
            "A": "answer_1_text", "B": "answer_2_text", "C": "answer_3_text",
            "D": "answer_4_text", "E": "answer_5_text",
        }
        fld = mapping.get(self.correct_answer)
        if fld and not (getattr(self, fld) or "").strip():
            raise ValidationError({fld: "Doğru cevap olarak seçtiğiniz şıkkın metni boş olamaz."})



def _full_name(fp: FacultyProfile) -> str:
    try:
        return fp.user.get_full_name()
    except Exception:
        return ""

@receiver(pre_save, sender=CourseQuestionDepot)
def cq_pre_save(sender, instance: CourseQuestionDepot, **kwargs):
    """
    Before saving a question:
    - Pull lecturer from master.lecturer
    - Pull tag_1 from master.name
    - Pull tag_2 from lecturer full name
    - Normalize fractions if single-choice
    """
    m = instance.master
    if m:
        # lecturer ← master.lecturer
        if getattr(m, "lecturer_id", None):
            instance.lecturer_id = m.lecturer_id
            # tag_2 from lecturer name
            if not instance.tag_2:
                instance.tag_2 = _full_name(m.lecturer)
        # tag_1 from course name
        if not instance.tag_1:
            instance.tag_1 = (m.name or "")

    # Make single-choice consistent: correct gets 1, others 0
    if instance.single and instance.correct_answer:
        letter = instance.correct_answer.upper()[:1]
        vals = {"A":0, "B":0, "C":0, "D":0, "E":0}
        if letter in vals: vals[letter] = 1
        instance.answer_1_fraction = vals["A"]
        instance.answer_2_fraction = vals["B"]
        instance.answer_3_fraction = vals["C"]
        instance.answer_4_fraction = vals["D"]
        instance.answer_5_fraction = vals["E"]


@receiver(post_save, sender=CourseMaster)
def cq_master_sync(sender, instance: CourseMaster, **kwargs):
    """
    If a CourseMaster changes (name or lecturer), keep denormalized fields in sync.
    This is optional but keeps lists/exports fast and consistent.
    """
    lecturer_name = _full_name(instance.lecturer) if getattr(instance, "lecturer_id", None) else ""
    (instance.questions.all()
        .update(
            lecturer_id=instance.lecturer_id,
            tag_1=instance.name or "",
            tag_2=lecturer_name
        ))
