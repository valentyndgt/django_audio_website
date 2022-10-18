from django.contrib import admin

from .models import ContactUs, Track


class ContactUsAdmin(admin.ModelAdmin):
    max_chars = 200
    list_display = ('user', 'email', 'subject', 'message_', 'date')
    date_hierarchy = 'date'

    def message_(self, obj):                # is there a way to apply changes to all fields?
        msg = obj.message
        if len(msg) > self.max_chars:
            return msg[:self.max_chars] + ' ...(CUT)...'
        return msg


class TrackAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'file')


admin.site.register(ContactUs, ContactUsAdmin)
admin.site.register(Track, TrackAdmin)
