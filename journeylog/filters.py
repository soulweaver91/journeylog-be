from django_filters.rest_framework import FilterSet, IsoDateTimeFilter, Filter

from .models import Photo


class PhotoFilter(FilterSet):
    after = IsoDateTimeFilter(field_name='timestamp', lookup_expr='gte')
    before = IsoDateTimeFilter(field_name='timestamp', lookup_expr='lt')
    journey = Filter(field_name='journey__slug')


    class Meta:
        model = Photo
        fields = []
