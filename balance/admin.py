from django.contrib import admin

from .models import Record


class RecordAdmin(admin.ModelAdmin):
    list_display = (
        'created_time',
        'reward_type',
        'coin_type',
        'amount',
        'description',
        'user',
    )


admin.site.register(Record, RecordAdmin)
