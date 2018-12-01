from django.contrib.auth.models import User
from rest_framework.fields import IntegerField, Field, SerializerMethodField
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

from .models import JournalPage, Photo, Journey, Location


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


class PhotoSerializer(ModelSerializer):
    access_url = SerializerMethodField()
    thumb_url = SerializerMethodField()

    def get_access_url(self, obj):
        user = self.context['request'].user

        return obj.access_url(user)

    def get_thumb_url(self, obj):
        user = self.context['request'].user

        return obj.thumb_url(user)

    class Meta:
        model = Photo
        fields = ('url', 'name', 'latitude', 'longitude', 'description', 'timestamp', 'timezone', 'filename',
                  'filesize', 'height', 'width', 'hash', 'camera_make', 'camera_model', 'focal_length', 'exposure',
                  'iso_speed', 'f_value', 'flash_fired', 'flash_manual', 'confidentiality', 'access_url', 'thumb_url')


class PhotoLiteSerializer(ModelSerializer):
    thumb_url = SerializerMethodField()

    def get_access_url(self, obj):
        user = self.context['request'].user

        return obj.access_url(user)

    def get_thumb_url(self, obj):
        user = self.context['request'].user

        return obj.thumb_url(user)

    class Meta:
        model = Photo
        fields = ('url', 'name', 'timestamp', 'timezone', 'filename', 'filesize', 'height', 'width',
                  'hash', 'confidentiality', 'access_url', 'thumb_url')


class JournalPageSerializer(HyperlinkedModelSerializer):
    photos = PhotoLiteSerializer(many=True)
    photos_count = IntegerField()

    class Meta:
        model = JournalPage
        fields = ('slug', 'name', 'order_no', 'type', 'text', 'date_start', 'date_end', 'photos', 'photos_count')


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

    journal_pages_count = IntegerField()
    photos_count = IntegerField()

    class Meta:
        model = Journey
        fields = ('url', 'id', 'name', 'slug', 'date_start', 'date_end', 'description', 'background',
                  'journal_pages', 'journal_pages_count', 'photos', 'photos_count')
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


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

