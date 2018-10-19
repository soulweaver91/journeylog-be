from django.contrib.auth.models import User
from rest_framework.fields import IntegerField, Field, SerializerMethodField
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer

from .models import JournalPage, Photo, Journey, Location


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


class JournalPageSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = JournalPage
        fields = ('slug', 'name', 'order_no', 'text', 'date_start', 'date_end')


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


class JourneySerializer(HyperlinkedModelSerializer):
    journal_pages = JournalPageSerializer(many=True)

    photos = HyperlinkedIdentityField(
        view_name='journey-photos-list',
        lookup_url_kwarg='journey_pk'
    )

    journal_pages_count = IntegerField()
    photos_count = IntegerField()

    class Meta:
        model = Journey
        fields = ('url', 'id', 'name', 'slug', 'date_start', 'date_end', 'description', 'background',
                  'journal_pages', 'journal_pages_count', 'photos', 'photos_count')


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

