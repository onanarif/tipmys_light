from django import forms
from qbank.models import CourseQuestionDepot

CORRECT_CHOICES = [("A","A"),("B","B"),("C","C"),("D","D"),("E","E")]
YES_NO = [("Yes","Evet"),("No","Hayır")]

class CourseQuestionDepotForm(forms.ModelForm):
    # Optional: read-only echoes
    course_display = forms.CharField(required=False, disabled=True,
                                     widget=forms.TextInput(attrs={"class": "form-control"}))
    lecturer_display = forms.CharField(required=False, disabled=True,
                                       widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta:
        model = CourseQuestionDepot
        # Do not include the fraction fields here:
        fields = [
            "master", "name", "question_text",
            "type", "active",
            "answer_1_text", "answer_2_text", "answer_3_text", "answer_4_text", "answer_5_text",
            "correct_answer", "correct_feedback", 
        ]
        widgets = {
            "master": forms.Select(attrs={"class": "form-select select2", "data-placeholder": "Ders"}),
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Soru adı"}),
            "question_text": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "type": forms.Select(attrs={"class": "form-select select2"}),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "answer_1_text": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "A şıkkı"}),
            "answer_2_text": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "B şıkkı"}),
            "answer_3_text": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "C şıkkı"}),
            "answer_4_text": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "D şıkkı"}),
            "answer_5_text": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "E şıkkı"}),
            # Radio buttons are fast to use with keyboard
            "correct_answer": forms.RadioSelect(choices=CORRECT_CHOICES),
            "correct_feedback": forms.Textarea(attrs={"class": "form-control", "rows": 4}),

        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)  # harmless if not passed
        super().__init__(*args, **kwargs)
        # Simple defaults on create
        if not self.instance.pk:
            self.fields["correct_answer"].initial = "A"

        # optional mirrors
        m = self.instance.master if self.instance.pk else None
        if m:
            self.fields["course_display"].initial = getattr(m, "name", "") or ""
            try:
                self.fields["lecturer_display"].initial = m.lecturer.user.get_full_name()
            except Exception:
                self.fields["lecturer_display"].initial = ""
