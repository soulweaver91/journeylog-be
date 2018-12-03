from django.contrib.auth.models import User
from rest_framework.fields import IntegerField, Field, SerializerMethodField, FloatField
from rest_framework.relations import HyperlinkedIdentityField, PrimaryKeyRelatedField
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

from .models import JournalPage, Photo, Journey, Location, JourneyLocationVisit


# https://github.com/alanjds/drf-nested-routers/issues/119
class FixedNestedHyperlinkedModelSerializer(NestedHyperlinkedModelSerializer):
    def build_url_field(self, field_name, model_class):
        field_class, field_kwargs = super().build_url_field(
            field_name, model_class)
        if hasattr(self, 'url_view_name'):
            field_kwargs['view_name'] = self.url_view_name
        return field_class, field_kwargs


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


# noinspection PyAbstractClass
class LocationNameDictSerializer(Field):
    def to_representation(self, instance):
        return {n.lang: {
            'name': n.name,
            'sort_key': n.sort_key
        } for n in instance.all()}


class LocationSerializer(ModelSerializer):
    names = LocationNameDictSerializer()

    class Meta:
        model = Location
        fields = ('url', 'id', 'name', 'latitude', 'longitude', 'color', 'type', 'names')


class PhotoSerializer(ModelSerializer):
    access_url = SerializerMethodField()
    thumb_url = SerializerMethodField()
    journey_slug = SerializerMethodField()
    latitude = FloatField()
    longitude = FloatField()

    def get_access_url(self, obj):
        user = self.context['request'].user

        return obj.access_url(user)

    def get_thumb_url(self, obj):
        user = self.context['request'].user

        return obj.thumb_url(user)

    def get_journey_slug(self, obj):
        return obj.journey.slug

    class Meta:
        model = Photo
        fields = ('url', 'id', 'name', 'latitude', 'longitude', 'description', 'timestamp', 'timezone', 'filename',
                  'filesize', 'height', 'width', 'hash', 'camera_make', 'camera_model', 'focal_length', 'exposure',
                  'iso_speed', 'f_value', 'flash_fired', 'flash_manual', 'confidentiality', 'access_url', 'thumb_url',
                  'journey_slug')


class PhotoLiteSerializer(ModelSerializer):
    access_url = SerializerMethodField()
    thumb_url = SerializerMethodField()
    journey_slug = SerializerMethodField()

    def get_access_url(self, obj):
        user = self.context['request'].user

        return obj.access_url(user)

    def get_thumb_url(self, obj):
        user = self.context['request'].user

        return obj.thumb_url(user)

    def get_journey_slug(self, obj):
        return obj.journey.slug

    class Meta:
        model = Photo
        fields = ('url', 'name', 'timestamp', 'timezone', 'filename', 'filesize', 'height', 'width',
                  'hash', 'confidentiality', 'access_url', 'thumb_url', 'journey_slug')


class LocationVisitSerializer(ModelSerializer):
    location = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = JourneyLocationVisit
        fields = ('id', 'location', 'timestamp')


class JournalPageSerializer(HyperlinkedModelSerializer):
    photos = PhotoLiteSerializer(many=True)
    photos_count = IntegerField()
    disabled_modules = SerializerMethodField()

    def get_disabled_modules(self, obj):
        return [] if obj.disabled_modules is None else obj.disabled_modules

    class Meta:
        model = JournalPage
        fields = ('slug', 'name', 'order_no', 'type', 'text', 'date_start', 'date_end', 'photos', 'photos_count',
                  'disabled_modules')


class JourneyJournalPageSerializer(FixedNestedHyperlinkedModelSerializer):
    url_view_name = 'journey-journal-pages-detail'
    parent_lookup_kwargs = {'journey_slug': 'journey__slug'}

    photos_count = IntegerField()

    class Meta:
        model = JournalPage
        fields = ('url', 'slug', 'name', 'order_no', 'type', 'date_start', 'date_end', 'photos_count')
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class JourneySerializer(HyperlinkedModelSerializer):
    journal_pages = JourneyJournalPageSerializer(many=True, read_only=True)

    photos = HyperlinkedIdentityField(
        view_name='journey-photos-list',
        lookup_url_kwarg='journey_slug',
        lookup_field='slug'
    )

    location_visits = HyperlinkedIdentityField(
        view_name='journey-location-visits-list',
        lookup_url_kwarg='journey_slug',
        lookup_field='slug'
    )

    journal_pages_count = IntegerField()
    photos_count = IntegerField()

    class Meta:
        model = Journey
        fields = ('url', 'id', 'name', 'slug', 'date_start', 'date_end', 'description', 'background',
                  'journal_pages', 'journal_pages_count', 'photos', 'photos_count', 'location_visits')
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }

