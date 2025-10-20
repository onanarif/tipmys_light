from django.urls import path, reverse
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.db.models import Prefetch
import logging
from django.contrib import messages
from django.db.models import ProtectedError
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test 


from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone
from faculty.models import Committee
from qbank.models import CourseMaster
from ..forms.committe_depot_f import CommitteeForm
from qbank.forms import CourseMasterForm

class CommitteeListView(ListView):
    model = Committee
    template_name = 'faculty/committee_list.html'
    context_object_name = 'committees'


    def get_queryset(self):
        # Sadece bugünden önce başlayan komiteleri getir
        return Committee.objects.filter(start_date__lte=timezone.now()).order_by('-start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        context['total_committees'] = Committee.objects.count()
        return context


logger = logging.getLogger(__name__)

class CommitteeDetailView(DetailView):
    model = Committee
    template_name = 'faculty/committee_detail.html'
    context_object_name = 'committee'

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related('phase', 'chair')   # ← no 'chair__user'
            .prefetch_related(
                Prefetch(
                    'cmt_courses',
                    queryset=CourseMaster.objects
                        .select_related('lecturer__user', 'department', 'type')
                        .order_by('name')
                )
            )
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['courses'] = self.object.cmt_courses.all()
        return ctx

class CommitteeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Committee
    form_class = CommitteeForm
    template_name = "faculty/committee_form.html"
    def test_func(self): return self.request.user.is_superuser
    def form_valid(self, form):
        messages.success(self.request, "Kurul/Staj oluşturuldu.")
        return super().form_valid(form)
    def get_success_url(self): return reverse("faculty:committee_detail", args=[self.object.pk])

def _is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(_is_superuser)
@require_POST
def committee_delete(request, pk: int):
    """
    POST-only delete, triggered by the Bootstrap modal on the list page.
    Redirects back to the list with a message.
    """
    obj = get_object_or_404(Committee, pk=pk)
    try:
        obj.delete()
        messages.success(request, f'"{obj.name}" başarıyla silindi.')
    except ProtectedError:
        messages.error(request, f'"{obj.name}" silinemedi: bağlı kayıtlar var.')
    return redirect(reverse("faculty:committee_list"))

def _can_edit(user, obj=None):
    return user.is_authenticated and (user.is_superuser or (obj and obj.lecturer and obj.lecturer.user_id == user.id))

class CommitteeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Committee
    form_class = CommitteeForm              # ⬅️ use the form with widgets
    template_name = "faculty/committee_form.html"

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, "Kurul/Staj güncellendi.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("faculty:committee_detail", args=[self.object.pk])

