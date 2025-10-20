from django import forms
from django.utils.translation import gettext_lazy as _
from faculty.models import FacultyProfile
from ..models.course_master import CourseMaster
from ..models.course_question_depot import CourseQuestionDepot


class CourseMasterForm(forms.ModelForm):
    department_display = forms.CharField(
        label="Bölüm (otomatik)",
        required=False,
        disabled=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = CourseMaster
        fields = ["name", "lecturer", "committee", "department", "type", "multilecture", "event_count", "active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ders adı"}),
            "lecturer": forms.Select(attrs={
                "class": "form-select select2",
                "data-placeholder": "Öğretim üyesi seçiniz"
            }),
            "committee": forms.Select(attrs={
                "class": "form-select select2",
                "data-placeholder": "Kurul/Staj seçiniz"
            }),
            "department": forms.HiddenInput(),
            "type": forms.Select(attrs={
                "class": "form-select select2",
                "data-placeholder": "Tür seçiniz"
            }),
            "multilecture": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "event_count": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }            

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ⚠️ Asla self.instance.lecturer demeyin; bu DB'ye gider ve DoesNotExist fırlatabilir
        lecturer_id = None
        if self.is_bound:
            # POST/GET verisi > initial > instance.lecturer_id sırası
            lecturer_id = self.data.get("lecturer") or self.initial.get("lecturer") or self.instance.lecturer_id
        else:
            lecturer_id = self.instance.lecturer_id

        dept_name = ""
        dept_id = None
        if lecturer_id:
            # Güvenli: yoksa None döner, exception atmaz
            lecturer = (FacultyProfile.objects
                        .select_related("department")
                        .filter(pk=lecturer_id).first())
            if lecturer and lecturer.department_id:
                dept_name = getattr(lecturer.department, "name", "") or ""
                dept_id = lecturer.department_id

        # Görsel alan (salt-okunur) ve gizli gerçek FK
        self.fields["department_display"].initial = dept_name
        if dept_id:
            self.fields["department"].initial = dept_id

    def clean_event_count(self):
        val = self.cleaned_data.get("event_count") or 0
        if val < 0:
            raise forms.ValidationError("Etkinlik sayısı negatif olamaz.")
        return val

    def clean(self):
        cleaned = super().clean()
        lecturer = cleaned.get("lecturer")
        # Departmanı her zaman lecturer'dan türet
        if lecturer and getattr(lecturer, "department_id", None):
            cleaned["department"] = lecturer.department
        else:
            cleaned["department"] = None
        return cleaned
