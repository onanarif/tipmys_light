from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin  

from .models.acadyear import AcadYear
from .models.program import Program
from .models.department import Department
from .models.committee import Committee
from .models.fct_profile import FacultyProfile
from .models.course_type import CourseType
from .models.course_event import CourseEvent

admin.site.register(AcadYear)
admin.site.register(Program)
admin.site.register(CourseType)


class CommitteeResource(resources.ModelResource):
    class Meta:
        model = Committee

@admin.register(Committee)
class CommitteeAdmin(ImportExportModelAdmin):
    resource_class = CommitteeResource

class DepartmentResource(resources.ModelResource):
    class Meta:
        model = Department

@admin.register(Department)
class DepartmentAdmin(ImportExportModelAdmin):
    resource_class = DepartmentResource

class FacultyProfileResource(resources.ModelResource):
    class Meta:
        model = FacultyProfile

@admin.register(FacultyProfile)
class FacultyProfileAdmin(ImportExportModelAdmin):
    resource_class = FacultyProfileResource


class CourseEventResource(resources.ModelResource):
    class Meta:
        model = CourseEvent
        fields = ('id', 'course__name', 'faculty__user__username', 'event_date', 'start_date', 'end_date')
        export_order = ('id', 'course__name', 'faculty__user__username', 'event_date', 'start_date', 'end_date')


@admin.register(CourseEvent)
class CourseEventAdmin(ImportExportModelAdmin):
    resource_class = CourseEventResource
    list_display = ('course', 'faculty', 'event_date', 'start_date', 'end_date')
    list_filter = ('course', 'faculty')
    search_fields = ('course__name', 'faculty__user__username')
    ordering = ('-event_date',)

