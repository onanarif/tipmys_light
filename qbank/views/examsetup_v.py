import os, base64, xml.etree.ElementTree as ET
from django.utils.html import escape
from datetime import datetime, time
from django.utils import timezone
import re
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.core.exceptions import ObjectDoesNotExist

from ..models import ExamSetup, CourseMaster, CourseQuestionSelected
from ..forms import ExamSetupForm
from faculty.models import Program, Committee  

class ExamSetupListView(LoginRequiredMixin, ListView):
    model = ExamSetup
    template_name = "qbank/examsetup_list.html"
    context_object_name = "exams"
    paginate_by = 20

    def get_queryset(self):
        qs = (ExamSetup.objects
              .select_related("program", "committee")
              .order_by("-date", "start"))
        q = self.request.GET.get("q")
        typ = self.request.GET.get("type")
        program = self.request.GET.get("program")
        committee = self.request.GET.get("committee")
        locked = self.request.GET.get("locked")

        if q:
            qs = qs.filter(Q(name__icontains=q))
        if typ:
            qs = qs.filter(type=typ)
        if program:
            qs = qs.filter(program_id=program)
        if committee:
            qs = qs.filter(committee_id=committee)
        if locked in ("0", "1"):
            qs = qs.filter(locked=(locked == "1"))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["programs"] = Program.objects.all()
        ctx["committees"] = Committee.objects.all()
        return ctx

class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self): return self.request.user.is_superuser

class ExamSetupCreateView(LoginRequiredMixin, SuperuserRequiredMixin, CreateView):
    model = ExamSetup
    form_class = ExamSetupForm
    template_name = "qbank/examsetup_form.html"
    success_url = reverse_lazy("qbank:examsetup_list")


    def form_valid(self, form):
        messages.success(self.request, "Sınav oluşturuldu.")
        resp = super().form_valid(form)
        return redirect(reverse("qbank:examsetup_list"))

class ExamSetupUpdateView(LoginRequiredMixin, SuperuserRequiredMixin, UpdateView):
    model = ExamSetup
    form_class = ExamSetupForm
    template_name = "qbank/examsetup_form.html"
    success_url = reverse_lazy("qbank:examsetup_list")

    def form_valid(self, form):
        messages.success(self.request, "Sınav güncellendi.")
        resp = super().form_valid(form)
        return redirect(reverse("qbank:examsetup_list"))

class ExamSetupDetailView(LoginRequiredMixin, DetailView):
    model = ExamSetup
    template_name = "qbank/examsetup_detail.html"
    context_object_name = "exam"

    def get_queryset(self):
        return (ExamSetup.objects
                .select_related("program", "committee"))

    def _is_exam_chair(self, user, exam) -> bool:
        if not user.is_authenticated:
            return False
        try:
            fct = user.facultyprofile
        except ObjectDoesNotExist:
            return False

        cmt = getattr(exam, "committee", None)
        if not cmt:
            return False

        if getattr(cmt, "chair_id", None) == getattr(fct, "id", None):
            return True
        chair_fp = getattr(cmt, "chair", None)
        if chair_fp and getattr(chair_fp, "id", None) == getattr(fct, "id", None):
            return True
        chair_user = getattr(cmt, "chair_user", None)
        try:
            if chair_user and chair_user.facultyprofile.id == fct.id:
                return True
        except Exception:
            pass
        return False

    def _is_upcoming_exam(self, exam) -> bool:
        if getattr(exam, "locked", False):
            return False
        now = timezone.now()
        start = getattr(exam, "start", None)
        if start:
            return start > now
        exam_date = getattr(exam, "date", None)
        if exam_date:
            tz = timezone.get_current_timezone()
            start_dt = timezone.make_aware(datetime.combine(exam_date, time.min), tz)
            return start_dt > now
        return False

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        exam = self.object
        user = self.request.user

        base_qs = (CourseMaster.objects
                   .select_related("lecturer__user", "department", "type")
                   .filter(committee=exam.committee)
                   .order_by("name"))

        show_all = user.is_superuser or self._is_exam_chair(user, exam)

        if show_all:
            courses = base_qs
        else:
            try:
                fct = user.facultyprofile
            except ObjectDoesNotExist:
                courses = base_qs.none()
            else:
                lecturer_filter = Q(lecturer=fct)
                courses = base_qs.filter(lecturer_filter).distinct()

        courses = courses.annotate(total_questions=Count("questions", distinct=True))
        selected_map = dict(
            CourseQuestionSelected.objects
            .filter(exam=exam, master_id__in=courses.values_list("id", flat=True))
            .values_list("master_id")
            .annotate(n=Count("id"))
            .values_list("master_id", "n")
        )

        selected_total, required_total = 0, 0
        for c in courses:
            c.selected_count = int(selected_map.get(c.id, 0))
            c.required = int(getattr(c, "question_set", 0) or 0)
            c.remaining = max(c.required - c.selected_count, 0)
            c.over = max(c.selected_count - c.required, 0)
            if c.selected_count == c.required:
                c.status = "ok"
            elif c.selected_count < c.required:
                c.status = "less"
            else:
                c.status = "more"
            selected_total += c.selected_count
            required_total += c.required

        ctx["courses"] = courses
        ctx["course_count"] = courses.count()
        ctx["showing_all_courses"] = show_all
        ctx["selected_total"] = selected_total
        ctx["required_total"] = required_total
        ctx["total_match"] = (selected_total == required_total)

        exam_upcoming = self._is_upcoming_exam(exam)
        ctx["exam_upcoming"] = exam_upcoming
        ctx["can_edit_qset"] = show_all and exam_upcoming
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        exam = self.object

        if not (request.user.is_superuser or self._is_exam_chair(request.user, exam)):
            messages.error(request, "Bu işlem için yetkiniz yok.")
            return redirect(reverse("qbank:examsetup_detail", args=[exam.pk]))

        if not self._is_upcoming_exam(exam):
            messages.error(request, "Sınav yaklaşmıyor veya kilitli. Değişiklik yapılamaz.")
            return redirect(reverse("qbank:examsetup_detail", args=[exam.pk]))

        committee_courses = CourseMaster.objects.filter(
            committee=exam.committee
        ).only("id", "question_set")
        id_to_course = {c.id: c for c in committee_courses}

        to_update, changed, errors = [], 0, 0
        for key, val in request.POST.items():
            if not key.startswith("qs_"):
                continue
            try:
                course_id = int(key[3:])
                if course_id not in id_to_course:
                    continue
                new_val = int(val)
                if new_val < 0:
                    raise ValueError("negative")
            except Exception:
                errors += 1
                continue

            course = id_to_course[course_id]
            if course.question_set != new_val:
                course.question_set = new_val
                to_update.append(course)
                changed += 1

        if to_update:
            CourseMaster.objects.bulk_update(to_update, ["question_set"])

        if changed:
            messages.success(request, f"{changed} ders için 'gerekli soru sayısı' güncellendi.")
        if errors:
            messages.warning(request, f"{errors} satır işlenemedi (geçersiz sayı).")

        return redirect(reverse("qbank:examsetup_detail", args=[exam.pk]))

@require_POST
def examsetup_delete(request, pk: int):
    obj = get_object_or_404(ExamSetup, pk=pk)

    if obj.locked:
        messages.error(request, f'"{obj.name}" kilitli olduğu için silinemez.')
        return redirect(reverse("qbank:examsetup_list"))
    obj.delete()
    messages.success(request, f'"{obj.name}" silindi.')
    return redirect(reverse("qbank:examsetup_list"))

class ExamSetupDetailQuestionListView(LoginRequiredMixin, DetailView):
    model = ExamSetup
    template_name = "qbank/examsetup_detail_question_list.html"
    context_object_name = "exam"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        exam = self.object
        committee = exam.committee

        ctx["courses"] = committee.cmt_courses.select_related(
            "lecturer__user", "department", "type"
        ).all()

        selected_qs = (
            CourseQuestionSelected.objects
            .filter(exam=exam)
            .select_related(
                "master",
                "question",
                "question__lecturer__user",
                "question__master",
            )
            .order_by("master__name", "question__name")  
        )

        ctx["selected"] = selected_qs
        ctx["selected_count"] = selected_qs.count()
        return ctx

@login_required
def export_exam_to_moodle_xml_light(request, pk: int):
    """
    Committee-only Moodle XML export for the light app.
    Exports all selected MCQs for this ExamSetup into a <quiz> XML.
    """
    exam = get_object_or_404(ExamSetup, pk=pk)

    if request.user.is_superuser or request.user.is_staff:
        selected = (CourseQuestionSelected.objects
                    .filter(exam=exam)
                    .select_related("question", "master"))
    else:
        selected = (CourseQuestionSelected.objects
                    .filter(exam=exam, question__lecturer__user=request.user)
                    .select_related("question", "master"))

    quiz = ET.Element("quiz")
    cdata_replacements = []

    for sel in selected:
        q = sel.question
        q_elem = ET.SubElement(quiz, "question", type="multichoice")

        name_elem = ET.SubElement(q_elem, "name")
        ET.SubElement(name_elem, "text").text = q.name or f"Q{q.pk}"

        qt_elem = ET.SubElement(q_elem, "questiontext", format="html")
        qt_text = ET.SubElement(qt_elem, "text")

        placeholder = f"__QTEXT_PLACEHOLDER_{q.id}__"
        qt_text.text = placeholder

        stem_html = f"<p>{escape((q.question_text or '').strip())}</p>"

        try:
            pictures_rel = getattr(q, "pictures", None) or getattr(q, "picture_set", None)
            pict_q = pictures_rel.filter(image_type="Q").first() if pictures_rel else None
            if pict_q and pict_q.image and hasattr(pict_q.image, "path"):
                filename = os.path.basename(pict_q.image.name)
                stem_html = f'<p><img src="@@PLUGINFILE@@/{filename}" /></p>' + stem_html

                file_elem = ET.SubElement(qt_elem, "file", name=filename, encoding="base64")
                with open(pict_q.image.path, "rb") as fh:
                    file_elem.text = base64.b64encode(fh.read()).decode("utf-8")
        except Exception:
            pass

        cdata_replacements.append(
            (f"<text>{placeholder}</text>", f"<text><![CDATA[{stem_html}]]></text>")
        )

        choices = [
            ("A", q.answer_1_text),
            ("B", q.answer_2_text),
            ("C", q.answer_3_text),
            ("D", q.answer_4_text),
            ("E", q.answer_5_text),
        ]
        for label, text in choices:
            if not text:
                continue
            fraction = "100" if (getattr(q, "correct_answer", None) == label) else "0"
            ans = ET.SubElement(q_elem, "answer", fraction=fraction)
            ET.SubElement(ans, "text").text = escape(text.strip())
            ET.SubElement(ans, "feedback").text = ""  

    if hasattr(ET, "indent"):
        ET.indent(quiz, space="  ")

    xml_str = ET.tostring(quiz, encoding="unicode")
    for ph, cdata in cdata_replacements:
        xml_str = xml_str.replace(ph, cdata)

    resp = HttpResponse(xml_str, content_type="application/xml")
    resp["Content-Disposition"] = f'attachment; filename="exam_{pk}_moodle.xml"'
    return resp

def _clean_line(s: str) -> str:
    """Aiken sade metin çıktısı için tek satıra indir, boşlukları toparla."""
    if not s:
        return ""
    s = re.sub(r'\s+', ' ', str(s)).strip()
    return s

@login_required
def export_exam_to_aiken_light(request, pk: int):
    """
    Light sürüm için Aiken formatında dışa aktarma.
    - Süperuser/staff: tüm seçili sorular
    - Diğer kullanıcı: yalnızca kendi (lecturer=user) soruları
    Not: Aiken görsele dosya eklemeyi desteklemez.
    """
    exam = get_object_or_404(ExamSetup, pk=pk)

    if request.user.is_superuser or request.user.is_staff:
        selected_qs = (CourseQuestionSelected.objects
                       .filter(exam=exam)
                       .select_related("question", "question__master", "question__lecturer__user"))
    else:
        selected_qs = (CourseQuestionSelected.objects
                       .filter(exam=exam, question__lecturer__user=request.user)
                       .select_related("question", "question__master", "question__lecturer__user"))

    lines = []
    for sel in selected_qs:
        q = sel.question
        qtext = _clean_line(q.question_text)
        if not qtext:
            continue
        lines.append(qtext)

        options = [
            ("A", _clean_line(q.answer_1_text)),
            ("B", _clean_line(q.answer_2_text)),
            ("C", _clean_line(q.answer_3_text)),
            ("D", _clean_line(q.answer_4_text)),
            ("E", _clean_line(q.answer_5_text)),
        ]
        for label, text in options:
            if text:
                lines.append(f"{label}. {text}")

        correct = (q.correct_answer or "").strip().upper()[:1]
        if correct not in ("A", "B", "C", "D", "E"):
            while lines and lines[-1] != qtext:
                lines.pop()
            lines.pop()  
            continue

        lines.append(f"ANSWER: {correct}")

        lines.append("")

    content = "\n".join(lines).rstrip() + "\n"

    resp = HttpResponse(content, content_type="text/plain; charset=utf-8")
    resp["Content-Disposition"] = f'attachment; filename="exam_{pk}_aiken.txt"'
    return resp
