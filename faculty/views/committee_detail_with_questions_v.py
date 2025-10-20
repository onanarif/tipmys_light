# faculty/views/committee_detail_with_questions.py
from django.views.generic import DetailView
from django.core.paginator import Paginator
from django.db.models import Q
from qbank.models import CourseMaster
from qbank.models import CourseQuestionDepot
from faculty.models import Committee

class CommitteeDetailWithQuestionsView(DetailView):
    model = Committee
    template_name = "faculty/committee_detail_with_questions.html"
    context_object_name = "committee"

    # Detay + alt bölümde sorular
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        committee = self.object

        # ---- Filtre değerleri ----
        req = self.request
        q = (req.GET.get("q") or "").strip()
        master_id = (req.GET.get("master") or "").strip()
        qtype = (req.GET.get("type") or "").strip()
        active = req.GET.get("active")  # "0", "1" ya da None

        # ---- Ana queryset: sadece bu komiteye ait sorular ----
        qs = (CourseQuestionDepot.objects
              .select_related("master", "lecturer__user")
              .filter(master__committee=committee)  # << bağ
              .order_by("-updated_at", "-id"))

        # ---- Filtre uygula ----
        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(question_text__icontains=q) |
                Q(master__name__icontains=q) |
                Q(lecturer__user__first_name__icontains=q) |
                Q(lecturer__user__last_name__icontains=q)
            )
        if master_id:
            qs = qs.filter(master_id=master_id)
        if qtype:
            qs = qs.filter(type=qtype)
        if active in ("0", "1"):
            qs = qs.filter(active=(active == "1"))

        # ---- Sayfalama (DetailView içinde manuel) ----
        page_number = req.GET.get("page") or 1
        paginator = Paginator(qs, 20)
        page_obj = paginator.get_page(page_number)

        # ---- Filtre seçenekleri (sadece bu komiteye ait dersler) ----
        masters = (CourseMaster.objects
                   .filter(committee=committee)
                   .order_by("name"))

        # ---- Context ----
        ctx["questions"] = page_obj.object_list
        ctx["page_obj"] = page_obj
        ctx["paginator"] = paginator
        ctx["is_paginated"] = page_obj.has_other_pages()
        ctx["masters"] = masters

        # Formu geri doldurmak için
        ctx["f_q"] = q
        ctx["f_master"] = master_id
        ctx["f_type"] = qtype
        ctx["f_active"] = active or ""

        return ctx
