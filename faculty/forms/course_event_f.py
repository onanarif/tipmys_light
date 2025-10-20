from django import forms
from ..models import CourseEvent
from faculty.models import Committee
from django.forms import DateTimeInput, Select
from qbank.models import CourseMaster
from datetime import datetime
DATETIME_LOCAL_FMT = "%Y-%m-%dT%H:%M"  # for <input type="datetime-local">

class CourseEventForm(forms.ModelForm):
    class Meta:
        model = CourseEvent
        # faculty çıkarıldı – sunucuda set edeceğiz
        fields = ["course", "start_date", "end_date"]
        widgets = {
            "course": Select(attrs={"class": "form-select"}),
            "start_date": DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}, format=DATETIME_LOCAL_FMT),
            "end_date": DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}, format=DATETIME_LOCAL_FMT),
        }

    def __init__(self, *args, committee: Committee = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["start_date"].input_formats = [DATETIME_LOCAL_FMT, "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]
        self.fields["end_date"].input_formats = [DATETIME_LOCAL_FMT, "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]

        if committee:
            self.fields["course"].queryset = (
                CourseMaster.objects
                .filter(committee=committee)
                .select_related("lecturer__user", "department", "type")
                .order_by("name")
            )

    def clean(self):
        cleaned = super().clean()
        s = cleaned.get("start_date")
        e = cleaned.get("end_date")
        if s and e and e < s:
            self.add_error("end_date", "Bitiş, başlangıçtan önce olamaz.")
        # Zorunlu: course->lecturer var mı kontrol et
        course = cleaned.get("course")
        if course and not getattr(course, "lecturer_id", None):
            self.add_error("course", "Seçilen dersin atanmış bir öğretim üyesi yok (lecturer).")
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        # faculty’yi course.lecturer’dan türet
        if obj.course and getattr(obj.course, "lecturer_id", None):
            obj.faculty_id = obj.course.lecturer_id
        # event_date’yi start/end’den belirle
        obj.event_date = (obj.start_date or obj.end_date).date() if (obj.start_date or obj.end_date) else obj.event_date
        if commit:
            obj.save()
            self.save_m2m()
        return obj
    