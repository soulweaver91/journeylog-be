import humanize
from admirarchy.utils import HierarchicalModelAdmin, AdjacencyList
from django.contrib import admin
from nested_admin.nested import NestedTabularInline, NestedModelAdmin

from .models import *


def photo_dimensions(photo):
    return "{}×{}".format(photo.width, photo.height)


def photo_filesize(photo):
    return humanize.naturalsize(photo.filesize, binary=True)


photo_dimensions.short_description = "Dimensions"
photo_filesize.short_description = "File size"


class JourneyAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_start', 'date_end')

    prepopulated_fields = {
        'slug': ('name', )
    }

    search_fields = ('name', 'journalpage__name')


class JournalPageAdmin(admin.ModelAdmin):
    list_display = ('name', 'journey', 'date_start', 'date_end', 'order_no')
    list_filter = ('journey', )
    list_select_related = ('journey', )

    prepopulated_fields = {
        'slug': ('name', )
    }

    search_fields = ('name', 'journey__name')
    autocomplete_fields = ['journey']


class PhotoAdmin(admin.ModelAdmin):
    list_display = ('name', 'timestamp', 'timezone', photo_dimensions, photo_filesize, 'journey')
    list_filter = ('journey', )
    list_select_related = ('journey', )

    date_hierarchy = 'timestamp'

    search_fields = ('name', 'filename')
    autocomplete_fields = ['journey']


class LocationNameInline(NestedTabularInline):
    model = LocationName
    extra = 1


class LocationAdmin(NestedModelAdmin):
    inlines = [
        LocationNameInline
    ]

    list_display = ('name', 'type')
    list_filter = ['type']

    search_fields = ('name', 'locationname__name')


class LocationNameAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'lang', 'sort_key')
    list_editable = ['sort_key']

    list_filter = ['lang']

    search_fields = ('name', 'sort_key', 'location__name')


class TagAdmin(HierarchicalModelAdmin):
    list_display = ('name', )
    hierarchy = AdjacencyList('parent')

    search_fields = ('name', )


class JourneyLocationVisitAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'location', 'journey')
    list_filter = ('journey', )
    list_select_related = ('journey', 'location')

    search_fields = ('journey__name', 'location__name')
    autocomplete_fields = ['journey', 'location']


class JourneyMapPointVisitAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'latitude', 'longitude', 'journey')
    list_filter = ('journey', )
    list_select_related = ('journey', )

    search_fields = ('journey__name', )
    autocomplete_fields = ['journey']


admin.site.register(Journey, JourneyAdmin)
admin.site.register(JournalPage, JournalPageAdmin)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(LocationName, LocationNameAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(JourneyLocationVisit, JourneyLocationVisitAdmin)
admin.site.register(JourneyMapPointVisit, JourneyMapPointVisitAdmin)

admin.site.site_header = 'JourneyLog administration'
admin.site.site_title = 'JourneyLog administration'
