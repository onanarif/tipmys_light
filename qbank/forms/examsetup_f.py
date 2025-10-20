# qbank/forms/examsetup.py
from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from ..models.examsetup import ExamSetup  # adjust to your app path: qbank.models.examsetup

DATETIME_INPUT_KW = {
    "class": "form-control",
    "type": "datetime-local",
}

class ExamSetupForm(forms.ModelForm):
    class Meta:
        model = ExamSetup
        fields = [
            "name", "type", "program", "committee",
            "date", "start", "finish", "qtotal",
            "apply_penalty", "locked",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Sınav adı"}),
            "type": forms.Select(attrs={"class": "form-select select2", "data-placeholder": "Tür"}),
            "program": forms.Select(attrs={"class": "form-select select2", "data-placeholder": "Program"}),
            "committee": forms.Select(attrs={"class": "form-select select2", "data-placeholder": "Kurul/Staj"}),
            # keep `date` as a date picker; your model is DateTimeField, we still show only the date part for UX
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "start": forms.DateTimeInput(attrs=DATETIME_INPUT_KW, format="%Y-%m-%dT%H:%M"),
            "finish": forms.DateTimeInput(attrs=DATETIME_INPUT_KW, format="%Y-%m-%dT%H:%M"),
            "qtotal": forms.NumberInput(attrs={"class": "form-control", "min": 0, "step": 1}),
            "apply_penalty": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "locked": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # datetime-local requires explicit input_formats
        for field in ("start", "finish"):
            if field in self.fields:
                self.fields[field].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]

        # Locking UX: if instance is locked, freeze fields except 'locked'
        if self.instance and self.instance.pk and self.instance.locked:
            for fname, f in self.fields.items():
                if fname != "locked":
                    f.disabled = True

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start")
        finish = cleaned.get("finish")
        date = cleaned.get("date")
        qtotal = cleaned.get("qtotal")

        # Validate finish > start (if both provided)
        if start and finish and finish <= start:
            raise ValidationError({"finish": "Bitiş, başlangıçtan sonra olmalıdır."})

        # If a 'date' is chosen, ensure start/finish fall on same calendar day (if provided)
        if date:
            date_day = (date if hasattr(date, "date") else timezone.make_aware(date)).date()
            if start and start.date() != date_day:
                raise ValidationError({"start": "Başlangıç, seçilen 'tarih' günü içinde olmalı."})
            if finish and finish.date() != date_day:
                raise ValidationError({"finish": "Bitiş, seçilen 'tarih' günü içinde olmalı."})

        # qtotal non-negative (allow blank/None to mean “not set”)
        if qtotal is not None and qtotal < 0:
            raise ValidationError({"qtotal": "Soru sayısı negatif olamaz."})

        return cleaned
