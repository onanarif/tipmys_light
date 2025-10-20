from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views.committee_v import CommitteeListView, CommitteeDetailView, CommitteeCreateView, CommitteeUpdateView, committee_delete
from .views.committee_with_exams_v import CommitteeWithExamsListView
from .views.committee_detail_with_questions_v import CommitteeDetailWithQuestionsView
from .views.committee_detail_courses_v import CommitteeDetailWithCoursesView
from .views.committee_eventlist_light_v import (committee_detail_eventlist_view, committee_detail_eventlist_view, course_event_create,
                    course_event_edit, course_event_delete)
from qbank.views import CourseMasterDetailView

app_name = 'faculty'

urlpatterns = [
    path('committees/', CommitteeListView.as_view(), name='committee_list'),  # valid
    path('committee/<int:pk>/', CommitteeDetailView.as_view(), name='committee_detail'),
    path("committee/<int:pk>/edit/", CommitteeUpdateView.as_view(), name="committee_update"),
    path("committees/new/", CommitteeCreateView.as_view(), name="committee_create"),
    path("committee/<int:pk>/delete/", committee_delete, name="committee_delete"),

    path("course/<int:pk>/", CourseMasterDetailView.as_view(), name="course_master_detail"),

    path("committees-with-exams/", CommitteeWithExamsListView.as_view(), name="committee_with_exams_list"),
    path("committee/<int:pk>/detail-with-questions/", CommitteeDetailWithQuestionsView.as_view(), name="committee_detail_with_questions"),    
    path("committee/<int:pk>/detail/", CommitteeDetailWithCoursesView.as_view(), name="committee_detail_with_courses"),

    path("committee/<int:committee_id>/events/", committee_detail_eventlist_view, name="committee_eventlist"),
    path("events/new/course/<int:committee_id>/", course_event_create, name="course_event_create"),
    path("events/course/<int:pk>/edit/", course_event_edit, name="course_event_edit"),
    path("events/course/<int:pk>/delete/", course_event_delete, name="course_event_delete"),    
    ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
