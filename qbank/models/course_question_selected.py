from django.utils import timezone
from django.db import models
from .course_master import CourseMaster
from .course_question_depot import CourseQuestionDepot
from .examsetup import ExamSetup
from faculty.models import FacultyProfile 
from django.utils.functional import cached_property



class CourseQuestionSelected(models.Model):
    master = models.ForeignKey(CourseMaster, on_delete=models.CASCADE, default=1200)
    question = models.ForeignKey(CourseQuestionDepot, on_delete=models.CASCADE, default=1000)
    exam = models.ForeignKey(ExamSetup, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('exam', 'question')
        indexes = [
            models.Index(fields=['master']),
            models.Index(fields=['master', 'exam']),
        ]  

    def __str__(self):
        return f"{self.master.name} - Q{self.question.id} "