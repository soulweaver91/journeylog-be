from django.contrib.auth.models import User
from rest_framework.fields import IntegerField, Field
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
    class Meta:
        model = Photo
        fields = ('url', 'name', 'latitude', 'longitude', 'description', 'timestamp', 'timezone', 'filename',
                  'filesize', 'height', 'width', 'hash', 'camera_make', 'camera_model', 'focal_length', 'exposure',
                  'iso_speed', 'f_value', 'flash_fired', 'flash_manual', 'confidentiality')


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

