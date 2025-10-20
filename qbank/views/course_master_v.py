from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from datetime import datetime, time
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from faculty.models import Committee
from ..models import CourseMaster,ExamSetup, CourseQuestionSelected  
from ..forms import CourseMasterForm
from ..views.permissions_v import can_manage_course_questions

class OwnerOrSuperuserMixin(UserPassesTestMixin):
    """Sadece superuser veya dersin sahibi (lecturer.user) düzenleyebilir/silebilir."""
    def test_func(self):
        obj = self.get_object()
        user = self.request.user
        is_owner = bool(obj.lecturer and obj.lecturer.user_id == user.id)
        return user.is_superuser or is_owner

class SuperuserRequiredMixin(UserPassesTestMixin):
    """İsterseniz oluşturma işlemini de superuser ile sınırlayabilirsiniz."""
    def test_func(self):
        return self.request.user.is_superuser

class CourseMasterListView(LoginRequiredMixin, ListView):
    model = CourseMaster
    context_object_name = "courses"
    template_name = "qbank/course_master_list.html"
    paginate_by = 20

    def get_queryset(self):
        qs = (CourseMaster.objects
              .select_related("lecturer__user", "committee", "department", "type")
              .order_by("-id"))

        committee_id   = self.kwargs.get("committee_id")
        committee_name = None if committee_id else self.request.GET.get("committee_name")
        committee_id   = committee_id or (None if committee_name else self.request.GET.get("committee"))
        q       = self.request.GET.get("q")
        active  = self.request.GET.get("active")

        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(lecturer__user__first_name__icontains=q) |
                Q(lecturer__user__last_name__icontains=q)
            )
        if committee_id:
            qs = qs.filter(committee_id=committee_id)
        if committee_name:
            qs = qs.filter(committee__name__icontains=committee_name)
        if active in ("0", "1"):
            qs = qs.filter(active=(active == "1"))

        user = self.request.user
        if user.is_superuser:
            return qs

        try:
            fct = user.facultyprofile
        except ObjectDoesNotExist:
            return qs.none()


        chair_q = Q(committee__chair_id=fct.id) | Q(committee__chair=fct)
        if committee_id:
            if qs.filter(chair_q, committee_id=committee_id).exists():
                return qs
        else:
            if qs.filter(chair_q).exists():
                return qs.filter(chair_q)
            
        lecturer_filter = Q(lecturer=fct)
        return qs.filter(lecturer_filter).distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["path_committee_id"] = self.kwargs.get("committee_id")
        ctx["committees"] = Committee.objects.order_by("name")
        return ctx


class CourseMasterDetailView(LoginRequiredMixin, DetailView):
    model = CourseMaster
    template_name = "qbank/course_master_detail.html"
    context_object_name = "course"

class CourseMasterCreateView(LoginRequiredMixin, SuperuserRequiredMixin, CreateView):
    model = CourseMaster
    form_class = CourseMasterForm
    template_name = "qbank/course_master_form.html"

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.department = obj.lecturer.department if (obj.lecturer and obj.lecturer.department_id) else None
        obj.save()
        messages.success(self.request, "Ders oluşturuldu.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("qbank:course_master_detail", args=[self.object.pk])

def _can_edit(user, obj=None):
    return user.is_authenticated and (user.is_superuser or (obj and obj.lecturer and obj.lecturer.user_id == user.id))

class CourseMasterUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = CourseMaster
    form_class = CourseMasterForm
    template_name = "qbank/course_master_form.html"

    def test_func(self):
        return _can_edit(self.request.user, self.get_object())

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.department = obj.lecturer.department if (obj.lecturer and obj.lecturer.department_id) else None
        obj.save()
        messages.success(self.request, "Ders güncellendi.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("qbank:course_master_detail", args=[self.object.pk])

class CourseMasterDeleteView(LoginRequiredMixin, OwnerOrSuperuserMixin, DeleteView):
    model = CourseMaster
    template_name = "qbank/course_master_confirm_delete.html"
    success_url = reverse_lazy("qbank:course_master_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Ders silindi.")
        return super().delete(request, *args, **kwargs)

class CourseMasterQuestionSelectDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = CourseMaster
    template_name = "qbank/course_master_question_select.html"
    context_object_name = "course"

    def get_exam(self) -> ExamSetup:
        return get_object_or_404(ExamSetup, pk=self.kwargs["exam_id"])

    def test_func(self):
        course = self.get_object()
        exam = self.get_exam()
        return can_manage_course_questions(self.request.user, course, exam)

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
        exam = self.get_exam()
        course = self.object

        questions = (course.questions
                     .select_related("lecturer__user")
                     .order_by("name"))

        selected_ids = set(
            CourseQuestionSelected.objects
            .filter(exam=exam, master=course)
            .values_list("question_id", flat=True)
        )

        required = int(getattr(course, "question_set", 0) or 0)
        selected_count = len(selected_ids)
        remaining = max(required - selected_count, 0)

        exam_upcoming = self._is_upcoming_exam(exam)

        ctx.update(
            exam=exam,
            questions=questions,
            selected_ids=selected_ids,
            required=required,
            selected_count=selected_count,
            remaining=remaining,
            exam_upcoming=exam_upcoming, 
        )
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        exam = self.get_exam()
        course = self.object

        if not self._is_upcoming_exam(exam):
            messages.error(request, "Bu sınav için seçimler kapalı (kilitli ya da tarihi geçmiş).")
            return redirect(reverse("qbank:course_master_question_select",
                                    args=[course.pk, exam.pk]))

        valid_ids = set(course.questions.values_list("id", flat=True))
        current_qs = CourseQuestionSelected.objects.filter(exam=exam, master=course)
        current_ids = set(current_qs.values_list("question_id", flat=True))

        required = int(getattr(course, "question_set", 0) or 0)

        posted_list = request.POST.getlist("qids")
        ordered_desired = []
        for x in posted_list:
            try:
                qid = int(x)
            except (TypeError, ValueError):
                continue
            if qid in valid_ids:
                ordered_desired.append(qid)

        desired_final = set(qid for qid in ordered_desired if qid in current_ids)
        blocked_new = 0
        for qid in ordered_desired:
            if qid in current_ids:
                continue
            if len(desired_final) < required:
                desired_final.add(qid)
            else:
                blocked_new += 1

        to_add = desired_final - current_ids
        to_remove = current_ids - desired_final

        if to_add:
            CourseQuestionSelected.objects.bulk_create(
                [CourseQuestionSelected(master=course, exam=exam, question_id=qid) for qid in to_add],
                ignore_conflicts=True
            )
        if to_remove:
            CourseQuestionSelected.objects.filter(
                exam=exam, master=course, question_id__in=to_remove
            ).delete()

        base_msg = f"{course.name}: {len(to_add)} eklendi, {len(to_remove)} kaldırıldı."
        if blocked_new:
            base_msg += f" {blocked_new} seçim gereksinimi aştığı için kaydedilmedi (gereken: {required})."
            messages.warning(request, base_msg)
        else:
            messages.success(request, base_msg)

        return redirect(reverse("qbank:course_master_question_select",
                                args=[course.pk, exam.pk]))
