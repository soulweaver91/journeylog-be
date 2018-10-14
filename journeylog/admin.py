from django.contrib import admin
from .models import *

admin.site.register(Journey)
admin.site.register(JournalPage)
admin.site.register(Photo)
admin.site.register(Location)
admin.site.register(LocationName)
admin.site.register(JourneyLocationVisit)
admin.site.register(JourneyMapPointVisit)
