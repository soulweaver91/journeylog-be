import humanize
from django.db import models
from separatedvaluesfield.models import SeparatedValuesField


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
    name = models.CharField(max_length=200)

    # TODO: convert to GeoDjango later
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True)

    description = models.TextField(blank=True)

    # TODO: is this combinable in a smart way?
    timezone = models.CharField(max_length=50)
    timestamp = models.DateTimeField()

    filename = models.TextField(editable=False)
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

    filesize_natural.admin_order_field = 'filesize'
    filesize_natural.short_description = 'Natural filesize'

    class Meta:
        ordering = ['timestamp', 'name']

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
