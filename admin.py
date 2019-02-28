from django.contrib import admin

from .models import Control, Implementation, Team, Certification, ControlOrigination

admin.site.register(Control)
admin.site.register(Implementation)
admin.site.register(Team)
admin.site.register(Certification)
admin.site.register(ControlOrigination)
