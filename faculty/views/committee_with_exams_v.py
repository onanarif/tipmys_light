# faculty/views/committee_with_exams.py
from django.db.models import Count, OuterRef, Subquery, DateTimeField, Q, Max
from django.utils import timezone
from django.views.generic import ListView
from django.urls import reverse
from qbank.models import ExamSetup
from faculty.models import Committee, Program


class CommitteeWithExamsListView(ListView):
    model = Committee
    template_name = "faculty/committee_with_exams_list.html"
    context_object_name = "committees"
    paginate_by = 20

    def get_queryset(self):
        now = timezone.now()

        next_exam_qs = (ExamSetup.objects
                        .filter(committee_id=OuterRef('pk'), start__gte=now)
                        .order_by('start'))

        qs = (Committee.objects
              .select_related('phase', 'chair')
              .annotate(
                  exam_count=Count('examsetup', distinct=True),
                  last_exam_start=Max('examsetup__start'),
                  next_exam_start=Subquery(next_exam_qs.values('start')[:1], output_field=DateTimeField()),
                  next_exam_id=Subquery(next_exam_qs.values('id')[:1]),
              )
              .order_by('name'))

        # Filters
        q = (self.request.GET.get('q') or '').strip()
        phase = self.request.GET.get('phase')
        has_exams = self.request.GET.get('has_exams')

        if q:
            qs = qs.filter(name__icontains=q)
        if phase:
            qs = qs.filter(phase_id=phase)
        if has_exams in ("0", "1"):
            qs = qs.filter(exam_count__gt=0) if has_exams == "1" else qs.filter(exam_count=0)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["programs"] = Program.objects.order_by("name")
        ctx["f_q"] = (self.request.GET.get('q') or '').strip()
        ctx["f_phase"] = self.request.GET.get('phase') or ""
        ctx["f_has_exams"] = self.request.GET.get('has_exams') or ""

        # Attach inline exams efficiently for committees on current page
        now = timezone.now()
        page_committees = list(ctx["committees"])  # page_obj.object_list
        if page_committees:
            cids = [c.id for c in page_committees]
            # One query for all exams of committees on this page
            all_exams = (ExamSetup.objects
                         .filter(committee_id__in=cids)
                         .only("id", "name", "type", "committee_id", "start", "finish", "locked")
                         .order_by("-start"))

            # Group by committee
            exam_map = {cid: [] for cid in cids}
            for ex in all_exams:
                exam_map[ex.committee_id].append(ex)

            # Split into upcoming/recent (short slices) and attach
            for c in page_committees:
                exams = exam_map.get(c.id, [])
                upcoming = [e for e in exams if e.start and e.start >= now]
                recent = [e for e in exams if e.start and e.start < now]

                # Keep it compact
                c.inline_upcoming = sorted(upcoming, key=lambda e: e.start)[:3]        # nearest 3
                c.inline_recent = sorted(recent, key=lambda e: e.start, reverse=True)[:3]  # last 3

        return ctx

