import rest_framework
from django.conf import settings
from django.contrib.auth.models import User
from constance import config

# Create your views here.
from django.db.models import Count, Subquery, OuterRef
from django.http import FileResponse, HttpResponseNotFound, HttpResponseForbidden, JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ViewSet

from .filters import PhotoFilter, LocationFilter
from .models import Journey, Photo, Location, JournalPage, JourneyLocationVisit
from .serializers import UserSerializer, JourneySerializer, PhotoSerializer, LocationSerializer, JournalPageSerializer, \
    LocationVisitSerializer


class ReadOnlyViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    pass


class PhotoPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = None

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'perPage': self.page_size,
            'totalPages': self.page.paginator.num_pages,
            'results': data
        })


class UserViewSet(ReadOnlyViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class JourneyViewSet(ReadOnlyViewSet):
    sq_base = Journey.objects.filter(id=OuterRef('pk')).order_by()
    pages_sq = sq_base.annotate(c=Count('journal_pages')).values('c')
    photos_sq = sq_base.annotate(c=Count('photos')).values('c')
    locations_sq = sq_base.annotate(c=Count('location_visits__location', distinct=True)).values('c')

    queryset = (
        Journey.objects.prefetch_related('journal_pages', 'photos', 'location_visits').annotate(
            journal_pages_count=Subquery(pages_sq),
            photos_count=Subquery(photos_sq),
            visited_locations_count=Subquery(locations_sq),
        ))
    serializer_class = JourneySerializer
    lookup_field = 'slug'


class PhotoViewSet(ReadOnlyViewSet):
    queryset = Photo.objects.select_related('journey')
    serializer_class = PhotoSerializer
    pagination_class = PhotoPagination
    filterset_class = PhotoFilter
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ('filename', 'name', 'description')
    ordering_fields = ('timestamp', 'filesize', 'filename', 'name')

    def get_serializer_context(self):
        context = super(PhotoViewSet, self).get_serializer_context()
        context.update({
            'EXPOSE_GPS': config.EXPOSE_GPS
        })
        return context


class JournalPageViewSet(ReadOnlyViewSet):
    queryset = JournalPage.objects.all()
    serializer_class = JournalPageSerializer


class LocationViewSet(ReadOnlyViewSet):
    queryset = Location.objects.prefetch_related('names').all()
    serializer_class = LocationSerializer
    filterset_class = LocationFilter
    filter_backends = (DjangoFilterBackend,)


class JourneyPhotoViewSet(PhotoViewSet):
    lookup_field = 'filename'
    lookup_value_regex = '[^/]+'

    def get_queryset(self):
        return Photo.objects.select_related('journey').filter(journey__slug=self.kwargs['journey_slug'])


class JourneyLocationVisitViewSet(ReadOnlyViewSet):
    serializer_class = LocationVisitSerializer

    def get_queryset(self):
        return JourneyLocationVisit.objects.select_related('journey').filter(journey__slug=self.kwargs['journey_slug'])


class JourneyJournalPageViewSet(JournalPageViewSet):
    lookup_field = 'slug'

    def get_queryset(self):
        return JournalPage.objects.select_related('journey').filter(journey__slug=self.kwargs['journey_slug'])


class ServerInformationViewSet(ViewSet):
    permission_classes = [AllowAny]

    def list(self, request, format=None):
        return Response({
            "online": True,
            "version": "0.1.0",
            "settings": {
                "HOME_TIMEZONE": config.HOME_TIMEZONE
            }
            # TODO: include last Git branch and commit hash somehow
        })


def photo_file_view(request, visibility, kind, journey_id, file):
    if visibility == 'private' and not request.user.is_authenticated:
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


def generate_missing_thumbs_view(request):
    if request.user.is_staff:
        photos = Photo.objects.all()

        count = 0

        for photo in photos:
            path = photo.ensure_thumb()
            if path is not True:
                count = count + 1

        return JsonResponse({
            "status": "OK",
            "generated": count
        })
    else:
        return HttpResponseForbidden()
