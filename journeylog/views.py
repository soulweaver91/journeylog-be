from django.contrib.auth.models import User

# Create your views here.
from django.db.models import Count
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
