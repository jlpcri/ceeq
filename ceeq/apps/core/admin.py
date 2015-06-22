from django.contrib import admin

from ceeq.apps.users.models import UserSettings


class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'bug')

admin.site.register(UserSettings)
