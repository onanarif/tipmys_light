from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
import datetime
from .acadyear import AcadYear
from .program import Program
from .committee import Committee
from .fct_profile import FacultyProfile

class CommitteeDepot(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    acad_year = models.ForeignKey(AcadYear, on_delete=models.CASCADE, default=1, related_name='acadyear_committeedepots')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, default=4, related_name='pr_committeedepots') # allows reverse access from Program to Committeedepot objects
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE, default=4, related_name='cmt_committeedepots') # allows reverse access from Committee to Committeedepot objects
    chair = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE, default=207, related_name='fct_committeedepots') # allows reverse access from FacultyProfile to Committeedepot objects
    start_date = models.DateField(default=datetime.date.today)
    end_date = models.DateField(default=datetime.date.today)
    period = models.BooleanField(default=True)  # False for ghost CommitteeDepots representing phases
    is_final = models.BooleanField(default=True)  # True if this is the final CommitteeDepot for the program
    edit_locked = models.BooleanField(default=False, help_text="Tüm düzenlemeler kilitli mi?")   

    @property
    def is_ghost(self):
        return not self.period

    def __str__(self):
        #return self.program.name + " " + self.committee.name
        return f"{self.name}"
    
    def is_user_involved(self, user):
        #return self.chair.user == user or self.committeedepotdeputy_set.filter(deputy__user=user).exists()
        return self.chair.user == user or self.cmt_depot_committeedepotdeputies.filter(deputy__user=user).exists()
    
    def get_upcoming_exam(self):
        upcoming_exam = self.examsetup_set.filter(start__gt=timezone.now()).order_by('start').first()
        return upcoming_exam
    
    def get_absolute_url(self):
        return reverse('committee_depot_detail', args=[str(self.id)])

    def get_courses_for_program(self):
        """
        Fetch all courses for the program (phase) related to this CommitteeDepot.
        This method will fetch courses from CourseEnroll based on the program linked to this CommitteeDepot.
        """
        # Fetch all CommitteeDepot objects that belong to the same program
        related_committee_depots = CommitteeDepot.objects.filter(program=self.program)

        # Get all CourseEnroll objects for these CommitteeDepot records
        from faculty.models import CourseEnroll
        course_enrolls = CourseEnroll.objects.filter(committee_depot__in=related_committee_depots)

        # Fetch the distinct CourseMaster objects based on the CourseEnroll objects
        from qbank.models import CourseMaster
        courses_in_program = CourseMaster.objects.filter(id__in=course_enrolls.values_list('mastercourse', flat=True)).distinct()

        return courses_in_program  

    def can_user_edit(self, user):
        return (
            user.is_superuser or 
            self.chair.user == user or 
            self.cmt_depot_committeedepotdeputies.filter(deputy__user=user).exists()
        )  

    

