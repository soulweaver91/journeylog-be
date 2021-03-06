from datetime import timedelta
import humanize
import logging
import os

from PIL import Image
from django.conf import settings
from django.db import models

from .util.model import FixedSeparatedValuesField
from .util.image import exif_rotate
from .validators import validate_language_code_list, validate_language_code

logger = logging.getLogger(__name__)

THUMBNAIL_EXTENSION = '.th.jpg'


class TemporalAwareModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def journey_background_image_path(journey, filename):
    return 'public/cover/{}_{}'.format(journey.id, filename)


class Journey(TemporalAwareModel):
    slug = models.SlugField(unique=True, max_length=100)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    background = models.ImageField(upload_to=journey_background_image_path, blank=True, max_length=240)
    languages = models.CharField(max_length=200, validators=[validate_language_code_list], blank=True,
                                 help_text="A comma-separated list of locale codes like en_GB. Use proper casing.")

    date_start = models.DateTimeField(blank=True, null=True)
    date_end = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['date_start', 'name']

    def save(self, *args, **kwargs):
        try:
            this = Journey.objects.get(id=self.id)
            if this.background != self.background:
                this.background.delete(save=False)
        except:
            logger.warning(r"Couldn't remove the old cover image of a journey.", exc_info=1)

        super(Journey, self).save(*args, **kwargs)

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
    type = models.CharField(max_length=100, choices=PageTypes, default=REGULAR)

    date_start = models.DateTimeField(blank=True, null=True)
    date_end = models.DateTimeField(blank=True, null=True)
    timezone_start = models.CharField(max_length=50, blank=True, null=True)
    timezone_end = models.CharField(max_length=50, blank=True, null=True)

    def effective_date_end(self):
        if self.date_start and not self.date_end:
            return self.date_start + timedelta(days=1) - timedelta(seconds=1)
        else:
            return self.date_end

    def effective_timezone_start(self):
        return self.timezone_start if self.timezone_start else 'UTC'

    def effective_timezone_end(self):
        if self.date_end is None:
            return self.effective_timezone_start()

        return self.timezone_end if self.timezone_end else 'UTC'

    journey = models.ForeignKey(Journey, on_delete=models.CASCADE, related_name='journal_pages')

    disabled_modules = FixedSeparatedValuesField(max_length=255, token=',', cast=int, choices=PageModules, blank=True)

    def photos(self):
        if self.date_start is None and self.date_end is None:
            if self.type == JournalPage.REGULAR:
                return list(self.journey.photos.all())
            else:
                return []

        if self.date_start is not None:
            timestamp_gte = self.date_start
            timestamp_lte = self.effective_date_end()
        else:
            timestamp_gte = float('-inf')
            timestamp_lte = self.date_end

        return [photo for photo in self.journey.photos.all()
                if timestamp_gte <= photo.timestamp <= timestamp_lte]

    def photos_count(self):
        return len(self.photos())

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
    AMUSEMENT_PARK = 'AMUSEMENT_PARK'
    ARCADE = 'ARCADE'
    BAR = 'BAR'
    BEACH = 'BEACH'
    BICYCLING = 'BICYCLING'
    BUILDING = 'BUILDING'
    BUS_STATION = 'BUS_STATION'
    CAFE = 'CAFE'
    CAMPING = 'CAMPING'
    CHURCH = 'CHURCH'
    ESCAPE_ROOM = 'ESCAPE_ROOM'
    GAS_STATION = 'GAS_STATION'
    HOME = 'HOME'
    HOSPITAL = 'HOSPITAL'
    HOTEL = 'HOTEL'
    INFO_CENTER = 'INFO_CENTER'
    KARAOKE = 'KARAOKE'
    MARKETPLACE = 'MARKETPLACE'
    MONUMENT = 'MONUMENT'
    MOVIE_THEATER = 'MOVIE_THEATER'
    MUSEUM = 'MUSEUM'
    ONBOARD_AIRPLANE = 'ONBOARD_AIRPLANE'
    ONBOARD_BUS = 'ONBOARD_BUS'
    ONBOARD_SHIP = 'ONBOARD_SHIP'
    ONBOARD_TAXI = 'ONBOARD_TAXI'
    PARK = 'PARK'
    PLACE = 'PLACE'
    RAILWAY_STATION = 'RAILWAY_STATION'
    RESTAURANT = 'RESTAURANT'
    SPA = 'SPA'
    SHOP = 'SHOP'
    SHRINE = 'SHRINE'
    SHIP_TERMINAL = 'SHIP_TERMINAL'
    SPORTS_CENTER = 'SPORTS_CENTER'
    SUBWAY_STATION = 'SUBWAY_STATION'
    THEATER = 'THEATER'
    ZOO = 'ZOO'

    LocationTypes = (
        ('Buildings', (
            (ARCADE, 'Arcade hall'),
            (BAR, 'Bar'),
            (CAFE, 'Café'),
            (CHURCH, 'Church'),
            (ESCAPE_ROOM, 'Escape room'),
            (GAS_STATION, 'Gas station'),
            (HOSPITAL, 'Hospital'),
            (HOTEL, 'Hotel'),
            (INFO_CENTER, 'Information center'),
            (KARAOKE, 'Karaoke'),
            (MOVIE_THEATER, 'Movie theater'),
            (MUSEUM, 'Museum'),
            (RESTAURANT, 'Restaurant'),
            (SPA, 'Spa'),
            (SHOP, 'Shop'),
            (THEATER, 'Theater'),
        )),
        ('Points of interest', (
            (AMUSEMENT_PARK, 'Amusement park'),
            (BEACH, 'Beach'),
            (CAMPING, 'Camping grounds'),
            (MARKETPLACE, 'Marketplace'),
            (MONUMENT, 'Monument'),
            (MUSEUM, 'Museum'),
            (PARK, 'Park'),
            (SHRINE, 'Shrine'),
            (SPORTS_CENTER, 'Sports center'),
            (ZOO, 'Zoo')
        )),
        ('Transit points', (
            (AIRPORT, 'Airport'),
            (BUS_STATION, 'Bus station'),
            (RAILWAY_STATION, 'Railway station'),
            (SHIP_TERMINAL, 'Ship or ferry terminal'),
            (SUBWAY_STATION, 'Subway station'),
        )),
        ('Traveling', (
            (ONBOARD_AIRPLANE, 'On an airplane'),
            (ONBOARD_BUS, 'On a bus'),
            (ONBOARD_SHIP, 'On a ship'),
            (ONBOARD_TAXI, 'In a taxi'),
            (BICYCLING, 'Riding a bicycle'),
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
    lang = models.CharField(max_length=10, validators=[validate_language_code])
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
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

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
                    # thumbnail extension is added by the backend endpoint
                    self.hash,
                    int(self.modified_at.timestamp())
                )
            else:
                return None

        return '{}{}/{}/{}{}?refresh={}'.format(
            settings.JOURNEYLOG['EXTERNAL_PUBLIC_IMAGE_HOST_URL'] or '/image/public/',
            kind,
            self.journey_id,
            self.filename,
            THUMBNAIL_EXTENSION if kind == 'thumb' else '',
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
                            self.filename + (THUMBNAIL_EXTENSION if kind == 'thumb' else ''))

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

            return thumb_path

        return True

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

