
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),   
    path('faculty/', include('faculty.urls')),  
    path('qbank/', include('qbank.urls')),  
    path('accounts/', include('authentication.urls')),
    path("select2/", include("django_select2.urls")),

]
