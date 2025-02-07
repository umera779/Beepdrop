from django.contrib import admin
from . models import Counter, TaskList, CustomUser, Referral
admin.site.register(Counter)
admin.site.register(CustomUser)
admin.site.register(Referral)

# Register your models here.
class TaskListAdmin(admin.ModelAdmin):
    list_display = ('Taskname', 'Taskvalue', 'display_assigned_users')
    search_fields = ('Taskname',)
    list_filter = ('Taskvalue',)
    filter_horizontal = ('assigned_users',)  # Makes user selection easier in admin panel

    def display_assigned_users(self, obj):
        return ", ".join([user.username for user in obj.assigned_users.all()])
        display_assigned_users.short_description = 'Assigned Users'



admin.site.register(TaskList, TaskListAdmin)
