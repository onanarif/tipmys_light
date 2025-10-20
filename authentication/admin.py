from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ('id','username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'password')  # Specify the fields you want to include
    def before_import_row(self, row, **kwargs):
        row['password'] = make_password(row['password'])
class UserAdmin(ImportExportModelAdmin, BaseUserAdmin):
    resource_class = UserResource
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
