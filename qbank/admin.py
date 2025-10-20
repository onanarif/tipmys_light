# admin.py
from django.contrib import admin
from django import forms
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django_select2.forms import Select2Widget

# Eğer CourseMaster bu app'in models'ında ise:
from .models import CourseMaster, CourseQuestionDepot, ExamSetup, CourseQuestionSelected
# Eğer CourseMaster qbank içindeyse bunun yerine:
# from qbank.models import CourseMaster

class CourseMasterForm(forms.ModelForm):
    class Meta:
        model = CourseMaster
        fields = "__all__"
        widgets = {
            # Modelindeki alan adı 'lecturer' ise:
            "lecturer": Select2Widget,
        }

class CourseMasterResource(resources.ModelResource):
    class Meta:
        model = CourseMaster

@admin.register(CourseMaster)
class CourseMasterAdmin(ImportExportModelAdmin):
    form = CourseMasterForm
    resource_class = CourseMasterResource

    # Liste görünümü
    list_display = ("id", "name", "committee", "lecturer", "department", "type", "active")
    list_display_links = ("id", "name")
    list_filter = ("active", "department", "type", "committee")
    search_fields = ("name", "lecturer__user__first_name", "lecturer__user__last_name")
    list_per_page = 50

    # JOIN performansı
    list_select_related = ("committee", "lecturer__user", "department", "type")

    # Okunur alanlar (modelinde varsa)
    readonly_fields = ("created_at", "updated_at")

    # Kolay düzenleme için (opsiyonel)
    list_editable = ("active",)

    # Sütunlarda insan-dostu görünüm (opsiyonel)
    def lecturer(self, obj):
        # Model alanı zaten 'lecturer' ise bu methodu kaldırabilirsin.
        # Burada örnek olsun diye isim biçimlendirmesi gösterdik:
        lf = getattr(obj, "lecturer", None)
        if lf and getattr(lf, "user", None):
            return lf.user.get_full_name() or lf.user.username
        return "—"

class CourseQuestionDepotResource(resources.ModelResource):
    class Meta:
        model = CourseQuestionDepot

@admin.register(CourseQuestionDepot)
class CourseQuestionDepotAdmin(ImportExportModelAdmin):
    resource_class = CourseQuestionDepotResource

    list_display = ("id", "name", "master", "lecturer", "active", "hidden", "created_at")
    list_display_links = ("id", "name")
    list_filter = ("active", "hidden")
    search_fields = ("name", "lecturer__user__first_name", "lecturer__user__last_name")
    list_per_page = 50

    list_select_related = ("master", "lecturer__user")

    readonly_fields = ("created_at", "updated_at")

    list_editable = ("active", "hidden")

    def lecturer(self, obj):
        lf = getattr(obj, "lecturer", None)
        if lf and getattr(lf, "user", None):
            return lf.user.get_full_name() or lf.user.username
        return "—"  
    
class ExamSetupResource(resources.ModelResource):
    class Meta:
        model = ExamSetup

@admin.register(ExamSetup)
class ExamSetupAdmin(ImportExportModelAdmin):
    resource_class = ExamSetupResource

    list_display = ("id", "name", "type", "date", "program", "committee", "qtotal", "apply_penalty", "locked")
    list_display_links = ("id", "name")
    list_filter = ("type", "program", "committee", "apply_penalty", "locked")
    search_fields = ("name",)
    list_per_page = 50

    list_select_related = ("program", "committee")

    list_editable = ("apply_penalty", "locked") 

class CourseQuestionSelectedResource(resources.ModelResource):
    class Meta:
        model = CourseQuestionSelected

@admin.register(CourseQuestionSelected)
class CourseQuestionSelectedAdmin(ImportExportModelAdmin):
    resource_class = CourseQuestionSelectedResource

    list_display = ("id", "exam", "master", "question")
    list_display_links = ("id",)
    list_filter = ("exam", "master")
    search_fields = ("exam__name", "master__name", "question__name")
    list_per_page = 50

    list_select_related = ("exam", "master", "question")


