import humanize
import os

from PIL import Image
from django.conf import settings
from django.db import models
from separatedvaluesfield.models import SeparatedValuesField

from .util.image import exif_rotate


class TemporalAwareModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Journey(TemporalAwareModel):
    slug = models.SlugField(unique=True, max_length=100)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    background = models.CharField(blank=True, max_length=240)

    date_start = models.DateTimeField(blank=True, null=True)
    date_end = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['date_start', 'name']

    def __str__(self):
        return self.name


class JournalPageModules:
    DESCRIPTION = 1
    PHOTOS = 2
    MAP = 3


class JournalPage(TemporalAwareModel):
    REGULAR = 'REGULAR'
    SPECIAL = 'SPECIAL'

    PageTypes = (
        (REGULAR, 'Regular daily page'),
        (SPECIAL, 'Special page'),
    )

    PageModules = (
        (JournalPageModules.DESCRIPTION, 'Description'),
        (JournalPageModules.PHOTOS, 'Photos'),
        (JournalPageModules.MAP, 'Map'),
    )

    slug = models.SlugField(unique=True, max_length=100)
    name = models.CharField(max_length=100, blank=True)
    order_no = models.SmallIntegerField(default=0)
    text = models.TextField(blank=True)

    date_start = models.DateTimeField(blank=True, null=True)
    date_end = models.DateTimeField(blank=True, null=True)

    journey = models.ForeignKey(Journey, on_delete=models.CASCADE, related_name='journal_pages')

    disabled_modules = SeparatedValuesField(max_length=255, token=',', cast=int, choices=PageModules, blank=True)

    class Meta:
        ordering = ['journey', 'order_no', 'date_start']

    def __str__(self):
        return "{} - {} to {}: {}".format(
            self.journey,
            self.date_start or '(not set)',
            self.date_end or '(not set)',
            self.name or '(no title)'
        )


class Location(TemporalAwareModel):
    AIRPORT = 'AIRPORT'
    ARCADE = 'ARCADE'
    BUILDING = 'BUILDING'
    BUS_STATION = 'BUS_STATION'
    CAFE = 'CAFE'
    HOME = 'HOME'
    HOTEL = 'HOTEL'
    INFO_CENTER = 'INFO_CENTER'
    KARAOKE = 'KARAOKE'
    MONUMENT = 'MONUMENT'
    MUSEUM = 'MUSEUM'
    ONBOARD_AIRPLANE = 'ONBOARD_AIRPLANE'
    ONBOARD_BUS = 'ONBOARD_BUS'
    ONBOARD_SHIP = 'ONBOARD_SHIP'
    PARK = 'PARK'
    PLACE = 'PLACE'
    RAILWAY_STATION = 'RAILWAY_STATION'
    RESTAURANT = 'RESTAURANT'
    SHOP = 'SHOP'
    SHRINE = 'SHRINE'
    SUBWAY_STATION = 'SUBWAY_STATION'

    LocationTypes = (
        ('Buildings', (
            (ARCADE, 'Arcade hall'),
            (CAFE, 'Café'),
            (HOTEL, 'Hotel'),
            (INFO_CENTER, 'Information center'),
            (KARAOKE, 'Karaoke'),
            (MUSEUM, 'Museum'),
            (RESTAURANT, 'Restaurant'),
            (SHOP, 'Shop'),
        )),
        ('Points of interest', (
            (MONUMENT, 'Monument'),
            (MUSEUM, 'Museum'),
            (PARK, 'Park'),
            (SHRINE, 'Shrine'),
        )),
        ('Transit points', (
            (AIRPORT, 'Airport'),
            (BUS_STATION, 'Bus station'),
            (RAILWAY_STATION, 'Railway station'),
            (SUBWAY_STATION, 'Subway station'),
        )),
        ('Traveling', (
            (ONBOARD_AIRPLANE, 'On an airplane'),
            (ONBOARD_BUS, 'On a bus'),
            (ONBOARD_SHIP, 'On a ship'),
        )),
        ('Other', (
            (HOME, 'Home'),
            (BUILDING, 'Other building'),
            (PLACE, 'Other place'),
        )),
    )

    name = models.CharField(max_length=100)

    # TODO: convert to GeoDjango later
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True)

    type = models.CharField(max_length=100, choices=LocationTypes, default=PLACE)

    color = models.CharField(max_length=6, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "{} ({})".format(self.name, self.get_type_display())


class LocationName(TemporalAwareModel):
    lang = models.CharField(max_length=10)
    name = models.CharField(max_length=200)
    sort_key = models.CharField(max_length=200, blank=True, null=True)

    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='names')

    class Meta:
        unique_together = (
            ('location', 'lang')
        )
        ordering = ['sort_key', 'location', 'name']

    def __str__(self):
        return "{} ({} in {})".format(self.name, self.location.name, self.lang)


class Photo(TemporalAwareModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__old_confidentiality = self.confidentiality

    name = models.CharField(max_length=200)

    # TODO: convert to GeoDjango later
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True)

    description = models.TextField(blank=True)

    # TODO: is this combinable in a smart way?
    timezone = models.CharField(max_length=50)
    timestamp = models.DateTimeField()

    filename = models.CharField(max_length=180, editable=False)
    filesize = models.BigIntegerField(editable=False)
    height = models.PositiveIntegerField(editable=False)
    width = models.PositiveIntegerField(editable=False)
    hash = models.CharField(max_length=40, editable=False)

    camera_make = models.CharField(blank=True, null=True, max_length=100)
    camera_model = models.CharField(blank=True, null=True, max_length=100)
    focal_length = models.CharField(blank=True, null=True, max_length=20)
    exposure = models.CharField(blank=True, null=True, max_length=20)
    iso_speed = models.CharField(blank=True, null=True, max_length=20)
    f_value = models.CharField(blank=True, null=True, max_length=20)
    flash_fired = models.BooleanField(default=False)
    flash_manual = models.BooleanField(default=False)

    confidentiality = models.SmallIntegerField(default=0)

    journey = models.ForeignKey(Journey, blank=True, null=True, on_delete=models.SET_NULL, related_name='photos')

    def dimensions(self):
        return "{}×{}".format(self.width, self.height)

    def filesize_natural(self):
        return humanize.naturalsize(self.filesize, binary=True)

    def get_url_of_kind(self, user, kind, for_admin=False):
        if self.confidentiality > 0 or for_admin:
            if user or for_admin:
                return '/image/private/{}/{}/{}?hash={}&refresh={}'.format(
                    kind,
                    self.journey_id,
                    self.filename,
                    self.hash,
                    int(self.modified_at.timestamp())
                )
            else:
                return None

        return '{}/{}/{}/{}?refresh={}'.format(
            settings.JOURNEYLOG['EXTERNAL_PUBLIC_IMAGE_HOST_URL'] or '/image/public',
            kind,
            self.journey_id,
            self.filename,
            int(self.modified_at.timestamp())
        )

    def access_url(self, user=None):
        return self.get_url_of_kind(user, 'photo')

    def thumb_url(self, user=None):
        return self.get_url_of_kind(user, 'thumb')

    def get_storage_file_path(self, kind, confidentiality=None):
        if confidentiality is None:
            confidentiality = self.confidentiality

        visibility = 'private' if confidentiality > 0 else 'public'

        return os.path.join(settings.BASE_DIR, 'storage', visibility, kind, str(self.journey_id),
                            self.filename + ('.th.jpg' if kind == 'thumb' else ''))

    def ensure_thumb(self):
        photo_path = self.get_storage_file_path('photo')
        thumb_path = self.get_storage_file_path('thumb')

        if not os.path.exists(thumb_path) or os.stat(thumb_path).st_mtime < self.modified_at.timestamp():
            thumb_path_dir = os.path.dirname(thumb_path)
            os.makedirs(thumb_path_dir, exist_ok=True)

            thumb_size = settings.JOURNEYLOG['PHOTO_THUMBNAIL_SIZE'] or 200
            ratio = max(thumb_size / self.width, thumb_size / self.height)

            im = Image.open(photo_path)
            im = exif_rotate(im)
            im.thumbnail(
                (self.width * ratio, self.height * ratio), Image.LANCZOS
            )
            im.save(thumb_path, 'jpeg', optimize=True, quality=85)

    def move_storage_file(self, kind):
        # TODO: figure out details regarding import later (the old path is not either private or public)
        old_path = self.get_storage_file_path(kind, confidentiality=self.__old_confidentiality)
        new_path = self.get_storage_file_path(kind)
        new_path_dir = os.path.dirname(new_path)

        if not os.path.exists(old_path):
            return

        os.makedirs(new_path_dir, exist_ok=True)
        os.rename(old_path, new_path)

    def save(self, *args, **kwargs):
        if self.confidentiality != self.__old_confidentiality:
            try:
                self.move_storage_file('photo')
                self.move_storage_file('thumb')

            except IOError:
                return

        super().save(*args, **kwargs)

    filesize_natural.admin_order_field = 'filesize'
    filesize_natural.short_description = 'Natural filesize'

    class Meta:
        ordering = ['timestamp', 'name']
        unique_together = (
            ('journey', 'filename')
        )

    def __str__(self):
        return self.name


class Tag(TemporalAwareModel):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('Tag', blank=True, null=True, on_delete=models.SET_NULL, related_name='children')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class JourneyLocationVisit(TemporalAwareModel):
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE, related_name='location_visits')
    location = models.ForeignKey(Location, blank=True, null=True, on_delete=models.SET_NULL, related_name='visits')
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return "{} visit on {}".format(self.location, self.timestamp)


class JourneyMapPointVisit(TemporalAwareModel):
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE, related_name='map_point_visits')

    # TODO: convert to GeoDjango later
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True)

    timestamp = models.DateTimeField()

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return "({}, {}) visit on {}".format(self.latitude, self.longitude, self.timestamp)


"""
class TransportationLine(models.Model):
    pass


class TransportationLineStop(models.Model):
    pass


class JourneyTransportationLineVisit(models.Model):
    pass
"""
