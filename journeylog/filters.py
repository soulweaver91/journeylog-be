from django_filters.rest_framework import FilterSet, IsoDateTimeFilter

from .models import Photo


class PhotoFilter(FilterSet):
    timestamp__gt = IsoDateTimeFilter(field_name='timestamp', lookup_expr='gt')
    timestamp__lt = IsoDateTimeFilter(field_name='timestamp', lookup_expr='lt')

    class Meta:
        model = Photo
        fields = []
