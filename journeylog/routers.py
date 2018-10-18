from rest_framework_nested import routers

from .views import JourneyPhotoViewSet, UserViewSet, JourneyViewSet, PhotoViewSet, LocationViewSet

root_router = routers.DefaultRouter()
# root_router.register(r'users', UserViewSet)
root_router.register(r'journeys', JourneyViewSet)
root_router.register(r'photos', PhotoViewSet)
root_router.register(r'locations', LocationViewSet)

journey_photos_router = routers.NestedSimpleRouter(root_router, r'journeys', lookup='journey')
journey_photos_router.register(r'photos', JourneyPhotoViewSet, base_name='journey-photos')
