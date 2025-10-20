# faculty/views/committee_detail_courses.py
from django.views.generic import DetailView
from django.db.models import Prefetch
from faculty.models import Committee
from qbank.models import CourseMaster

class CommitteeDetailWithCoursesView(DetailView):
    """
    Committee detail page that shows Committee info
    and a list of related CourseMaster records directly below.
    """
    model = Committee
    template_name = "faculty/committee_detail_with_courses.html"
    context_object_name = "committee"

    def get_queryset(self):
        # Pull committee + its courses in one shot
        return (
            Committee.objects
            .select_related("phase", "chair")  # chair.user string may be used in template
            .prefetch_related(
                Prefetch(
                    "cmt_courses",
                    queryset=CourseMaster.objects
                        .select_related("lecturer__user", "department", "type")
                        .order_by("name")
                )
            )
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        courses = self.object.cmt_courses.all()  # thanks to related_name on CourseMaster
        ctx["courses"] = courses
        ctx["course_count"] = courses.count()
        return ctx
