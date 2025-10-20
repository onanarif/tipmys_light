from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from ..models.course_question_depot import CourseQuestionDepot
from ..models.course_master import CourseMaster
from ..forms import CourseQuestionDepotForm

def _can_edit(user, obj=None):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if obj and obj.lecturer and obj.lecturer.user_id == user.id:
        return True
    return False

class QuestionBase(LoginRequiredMixin):
    model = CourseQuestionDepot

class QuestionListView(QuestionBase, ListView):
    template_name = "qbank/question_list.html"
    context_object_name = "questions"
    paginate_by = 20

    def _role_scoped_qs(self, qs):
        user = self.request.user
        if getattr(user, "is_superuser", False):
            return qs
        try:
            fp_id = user.facultyprofile.id
        except Exception:
            return qs.none()

        chair_q = Q(master__committee__chair_id=fp_id)
        owner_q = Q(master__lecturer__user_id=user.id)
        return qs.filter(chair_q | owner_q).distinct()

    def get_queryset(self):
        qs = (CourseQuestionDepot.objects
              .select_related("master", "lecturer__user")
              .order_by("-updated_at", "-id"))

        qs = self._role_scoped_qs(qs)
        q = self.request.GET.get("q")
        master_id = self.request.GET.get("master")
        qtype = self.request.GET.get("type")
        active = self.request.GET.get("active")

        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(question_text__icontains=q) |
                Q(tag_1__icontains=q) |
                Q(tag_2__icontains=q)
            )
        if master_id:
            qs = qs.filter(master_id=master_id)
        if qtype:
            qs = qs.filter(type=qtype)
        if active in ("0", "1"):
            qs = qs.filter(active=(active == "1"))

        return qs

    def _role_scoped_masters(self):
        """Masters list for the dropdown must respect the same scope."""
        user = self.request.user
        base = CourseMaster.objects.order_by("name")
        if getattr(user, "is_superuser", False):
            return base
        try:
            fp_id = user.facultyprofile.id
        except Exception:
            return base.none()

        chair_q = Q(committee__chair_id=fp_id)
        owner_q = Q(lecturer__user_id=user.id)
        return base.filter(chair_q | owner_q).distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        selected = self.request.GET.get("master")  
        ctx["selected_master"] = str(selected) if selected else ""
        ctx["masters"] = self._role_scoped_masters()
        return ctx

class QuestionListByMasterView(QuestionListView):
    """Scoped list under a specific CourseMaster."""
    def get_queryset(self):
        self.master_id = self.kwargs.get("master_id")
        self.request.GET = self.request.GET.copy()
        if self.master_id and not self.request.GET.get("master"):
            self.request.GET["master"] = str(self.master_id)
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["path_master_id"] = self.kwargs.get("master_id")
        return ctx

class QuestionDetailView(QuestionBase, DetailView):
    template_name = "qbank/question_detail.html"
    context_object_name = "question"

class QuestionCreateView(QuestionBase, CreateView):
    form_class = CourseQuestionDepotForm
    template_name = "qbank/question_form.html"

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["request"] = self.request
        return kw

    def get_initial(self):
        ini = super().get_initial()
        master_id = self.request.GET.get("master")
        if master_id:
            ini["master"] = master_id
        return ini
  
    def form_valid(self, form):
        obj = form.save()
        messages.success(self.request, "Soru oluşturuldu.")
        next_url = self.request.GET.get("next")
        if next_url:
            return redirect(next_url)
        return redirect(reverse("qbank:question_detail", args=[obj.pk]))    

    def form_invalid(self, form):
        messages.error(self.request, "Lütfen form hatalarını düzeltin.")
        print("QUESTION CREATE ERRORS:", form.errors.as_json())  
        return super().form_invalid(form)

class QuestionUpdateView(QuestionBase, UserPassesTestMixin, UpdateView):
    form_class = CourseQuestionDepotForm
    template_name = "qbank/question_form.html"

    def test_func(self):
        return _can_edit(self.request.user, self.get_object())

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["request"] = self.request
        return kw

    def form_valid(self, form):
        obj = form.save()
        messages.success(self.request, "Soru güncellendi.")
        return redirect(reverse("qbank:question_detail", args=[obj.pk]))

@login_required
@require_POST
def question_delete(request, pk: int):
    obj = get_object_or_404(CourseQuestionDepot, pk=pk)
    if not _can_edit(request.user, obj):
        messages.error(request, "Bu soruyu silme yetkiniz yok.")
        return redirect(reverse("qbank:question_list"))
    obj.delete()
    messages.success(request, "Soru silindi.")
    next_url = request.POST.get("next")
    return redirect(next_url or reverse("qbank:question_list"))
