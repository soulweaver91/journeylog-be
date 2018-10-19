from admirarchy.utils import HierarchicalModelAdmin, AdjacencyList
from django.contrib import admin
from django.utils.html import format_html
from nested_admin.nested import NestedTabularInline, NestedModelAdmin

from .models import *


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


class PrivateOrNotFilter(admin.SimpleListFilter):
    title = "Confidentiality"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'confidentiality'

    def lookups(self, request, model_admin):
        return (
            ('public', 'Public'),
            ('private', 'Private'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'public':
            return queryset.filter(confidentiality=0)
        if self.value() == 'private':
            return queryset.filter(confidentiality__gt=0)


class PhotoAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/photo_admin.css', )
        }

    def image_tag(self, photo):
        return format_html('<div class="journeylog_photo-thumbnail-container">'
                           '<div class="journeylog_photo-thumbnail" style="background-image: url({});"'
                           '</div></div>'
                           .format(photo.get_url_of_kind(None, 'thumb', for_admin=True)))
    image_tag.short_description = ''

    def is_confidential(self, photo):
        return photo.confidentiality > 0
    is_confidential.short_description = 'Private?'
    is_confidential.boolean = True

    list_display = ('image_tag', 'name', 'timestamp', 'timezone', 'dimensions', 'filesize_natural', 'journey',
                    'is_confidential')
    list_filter = ('journey', PrivateOrNotFilter)
    list_select_related = ('journey', )
    list_display_links = ('image_tag', 'name')

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
