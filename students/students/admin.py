from django.contrib import admin

from .models import Group, Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "year", "group")
    list_filter = ("year",)
    search_fields = ("first_name", "last_name",)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name",)