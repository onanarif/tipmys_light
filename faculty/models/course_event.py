from django.db import models
from faculty.models.fct_profile import FacultyProfile
from qbank.models.course_master import CourseMaster

class CourseEvent(models.Model):
    course = models.ForeignKey(
        CourseMaster,
        on_delete=models.CASCADE,
        related_name='cenroll_courseevents',
        verbose_name='Course'
    )
    faculty = models.ForeignKey(
        FacultyProfile,
        on_delete=models.CASCADE,
        related_name='fprofile_courseevents',
        verbose_name='Faculty'
    )
    event_date = models.DateTimeField('Event Date')
    start_date = models.DateTimeField('Start Date')
    end_date = models.DateTimeField('End Date')

    def __str__(self):
        return f"{self.course.name} - {self.event_date.strftime('%Y-%m-%d')}"

    class Meta:
        ordering = ['-event_date']
        verbose_name = 'Course Event'
        verbose_name_plural = 'Course Events'
