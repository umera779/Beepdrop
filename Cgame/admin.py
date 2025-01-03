from django.contrib import admin
from . models import Counter, Mining, TaskList, Boost, Level, CustomUser, ButtonState
admin.site.register(Counter)
admin.site.register(Mining)
admin.site.register(CustomUser)
admin.site.register( Level)
admin.site.register(ButtonState)

# Register your models here.
class TaskListAdmin(admin.ModelAdmin):
    list_display = ('Taskname', 'Taskvalue', 'display_assigned_users')
    search_fields = ('Taskname',)
    list_filter = ('Taskvalue',)
    filter_horizontal = ('assigned_users',)  # Makes user selection easier in admin panel

    def display_assigned_users(self, obj):
        return ", ".join([user.username for user in obj.assigned_users.all()])
        display_assigned_users.short_description = 'Assigned Users'


class BoostListAdmin(admin.ModelAdmin):
    list_display = ('boost_name', 'boost_value', 'display_boosting_users')
    search_fields = ('boost_name',)
    list_filter = ('boost_value',)
    filter_horizontal = ('assigned_users',)

    def display_boosting_users(self, obj):
        return ", ".join([user.username for user in obj.assigned_users.all()])
        display_boosting_users.short_description = "Assigned Users"

admin.site.register(TaskList, TaskListAdmin)
admin.site.register(Boost, BoostListAdmin)
