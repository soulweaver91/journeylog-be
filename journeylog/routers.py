from rest_framework_nested import routers

from .views import JourneyPhotoViewSet, UserViewSet, JourneyViewSet, PhotoViewSet, \
    LocationViewSet, ServerInformationViewSet, JourneyJournalPageViewSet, JourneyLocationVisitViewSet

root_router = routers.DefaultRouter()
# root_router.register(r'users', UserViewSet)
root_router.register(r'journeys', JourneyViewSet)
root_router.register(r'photos', PhotoViewSet)
root_router.register(r'locations', LocationViewSet)
root_router.register(r'status', ServerInformationViewSet, basename='status')

journey_router = routers.NestedSimpleRouter(root_router, r'journeys', lookup='journey')
journey_router.register(r'photos', JourneyPhotoViewSet, basename='journey-photos')
journey_router.register(r'journal-pages', JourneyJournalPageViewSet, basename='journey-journal-pages')
journey_router.register(r'location-visits', JourneyLocationVisitViewSet, basename='journey-location-visits')
