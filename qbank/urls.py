from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views.course_master_v import (CourseMasterListView, CourseMasterDetailView, CourseMasterQuestionSelectDetailView,
    CourseMasterCreateView, CourseMasterUpdateView, CourseMasterDeleteView,
)
from .views.course_question_depot_v import(
    QuestionListView, QuestionDetailView, QuestionCreateView, QuestionUpdateView,
    question_delete, QuestionListByMasterView,
)

from .views.examsetup_v import (
    ExamSetupListView, ExamSetupCreateView, ExamSetupUpdateView,
    ExamSetupDetailView, examsetup_delete, export_exam_to_moodle_xml_light, export_exam_to_aiken_light,
)
from .views.examsetup_v import ExamSetupDetailQuestionListView


app_name = "qbank"
 
urlpatterns = [
    path("courses/", CourseMasterListView.as_view(), name="course_master_list"),
    path("courses/committee/<int:committee_id>/",  CourseMasterListView.as_view(), name="course_master_list_by_committee"),
    path("course/<int:pk>/", CourseMasterDetailView.as_view(), name="course_master_detail"),
    path("course/new/", CourseMasterCreateView.as_view(), name="course_master_create"),
    path("course/<int:pk>/edit/", CourseMasterUpdateView.as_view(), name="course_master_update"),
    path("course/<int:pk>/delete/", CourseMasterDeleteView.as_view(), name="course_master_delete"),    


    path("courses/<int:master_id>/questions/", QuestionListByMasterView.as_view(), name="question_list_by_master"),
    path("questions/", QuestionListView.as_view(), name="question_list"),
    path("questions/new/", QuestionCreateView.as_view(), name="question_create"),
    path("questions/<int:pk>/", QuestionDetailView.as_view(), name="question_detail"),
    path("questions/<int:pk>/edit/", QuestionUpdateView.as_view(), name="question_update"),
    path("questions/<int:pk>/delete/", question_delete, name="question_delete"),    

    path("exams/", ExamSetupListView.as_view(), name="examsetup_list"),
    path("exams/new/", ExamSetupCreateView.as_view(), name="examsetup_create"),
    path("exams/<int:pk>/", ExamSetupDetailView.as_view(), name="examsetup_detail"),
    path("exams/<int:pk>/edit/", ExamSetupUpdateView.as_view(), name="examsetup_update"),
    path("exams/<int:pk>/delete/", examsetup_delete, name="examsetup_delete"),   
    path("exams/<int:pk>/questions/", ExamSetupDetailQuestionListView.as_view(), name="examsetup_detail_questions"), 
    path("exams/<int:pk>/export/moodle.xml", export_exam_to_moodle_xml_light, name="export_moodle_xml_light"),
    path("exams/<int:pk>/export/aiken.txt", export_exam_to_aiken_light, name="export_aiken_light"), 


    path("courses/<int:pk>/select-questions/<int:exam_id>/", CourseMasterQuestionSelectDetailView.as_view(), name="course_master_question_select"),




]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)