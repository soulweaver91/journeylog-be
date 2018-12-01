import rest_framework
from django.conf import settings
from django.contrib.auth.models import User

# Create your views here.
from django.db.models import Count
from django.http import FileResponse, HttpResponseNotFound
from rest_framework import mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ViewSet

from .filters import PhotoFilter
from .models import Journey, Photo, Location, JournalPage
from .serializers import UserSerializer, JourneySerializer, PhotoSerializer, LocationSerializer, JournalPageSerializer


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
            .prefetch_related('journal_pages', 'photos')
            .annotate(
            journal_pages_count=Count('journal_pages', distinct=True),
            photos_count=Count('photos', distinct=True),
        ))
    serializer_class = JourneySerializer
    lookup_field = 'slug'


class PhotoViewSet(ReadOnlyViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    pagination_class = PhotoPagination
    filterset_class = PhotoFilter


class JournalPageViewSet(ReadOnlyViewSet):
    queryset = JournalPage.objects.all()
    serializer_class = JournalPageSerializer


class LocationViewSet(ReadOnlyViewSet):
    queryset = Location.objects.prefetch_related('names').all()
    serializer_class = LocationSerializer


class JourneyPhotoViewSet(PhotoViewSet):
    def get_queryset(self):
        return Photo.objects.filter(journey__slug=self.kwargs['journey_slug'])


class JourneyJournalPageViewSet(JournalPageViewSet):
    lookup_field = 'slug'

    def get_queryset(self):
        return JournalPage.objects.filter(journey__slug=self.kwargs['journey_slug'])


class ServerInformationViewSet(ViewSet):
    permission_classes = [AllowAny]

    def list(self, request, format=None):
        return Response({
            "online": True,
            "version": "0.1.0",
            # TODO: include last Git branch and commit hash somehow
        })


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
