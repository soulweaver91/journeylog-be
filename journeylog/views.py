import os

from django.conf import settings
from django.contrib.auth.models import User

# Create your views here.
from django.db.models import Count
from django.http import FileResponse, HttpResponseNotFound
from rest_framework import mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import GenericViewSet

from .filters import PhotoFilter
from .models import Journey, Photo, Location
from .serializers import UserSerializer, JourneySerializer, PhotoSerializer, LocationSerializer


class ReadOnlyViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    pass


class PhotoPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = None


class UserViewSet(ReadOnlyViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class JourneyViewSet(ReadOnlyViewSet):
    queryset = (
        Journey.objects
            .prefetch_related('journal_pages')
            .annotate(
            journal_pages_count=Count('journal_pages', distinct=True),
            photos_count=Count('photos', distinct=True),
        ))
    serializer_class = JourneySerializer


class PhotoViewSet(ReadOnlyViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    pagination_class = PhotoPagination
    filterset_class = PhotoFilter


class LocationViewSet(ReadOnlyViewSet):
    queryset = Location.objects.prefetch_related('names').all()
    serializer_class = LocationSerializer


class JourneyPhotoViewSet(PhotoViewSet):
    def get_queryset(self):
        return Photo.objects.filter(journey=self.kwargs['journey_pk'])


def photo_file_view(request, visibility, kind, journey_id, file):
    print(visibility, kind, journey_id, file)
    if visibility == 'private' and request.user is None:
        return HttpResponseNotFound()

    photo = Photo.objects.filter(journey_id=journey_id, filename=file).first()

    if photo is None:
        return HttpResponseNotFound()

    if (photo.confidentiality > 0 or visibility == 'private') and not photo.hash == request.GET['hash']:
        return HttpResponseNotFound()

    if kind == 'thumb':
        photo.ensure_thumb()

    try:
        file_path = photo.get_storage_file_path(kind)
        return FileResponse(open(file_path, 'rb'))
    except IOError:
        return HttpResponseNotFound()
