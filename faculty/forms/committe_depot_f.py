from django import forms
from ..models import Committee

class CommitteeForm(forms.ModelForm):
    class Meta:
        model = Committee
        fields = ["name", "phase", "chair", "start_date", "end_date"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Kurul/Staj adı"}),
            "phase": forms.Select(attrs={"class": "form-select select2", "data-placeholder": "Aşama seçiniz"}),
            "chair": forms.Select(attrs={"class": "form-select select2", "data-placeholder": "Başkan seçiniz"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }