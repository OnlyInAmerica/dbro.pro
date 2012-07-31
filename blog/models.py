from dbro.settings import MEDIA_ROOT

from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.db.models.signals import post_save, pre_save

import datetime
import time

#For Graphic processing
from PIL import Image
from PIL.ExifTags import TAGS


class Tag(models.Model):
    slug = models.SlugField(max_length=160, unique=True)
    description = models.CharField(max_length=200, blank=True)
    icon = models.CharField(max_length=150, blank=True)  # filename in {{ STATIC_URL }}/icons

    def __unicode__(self):
        return u'%s' % self.slug


class Category(models.Model):
    slug = models.SlugField(max_length=160, unique=True)
    description = models.CharField(max_length=200, blank=True)
    icon = models.CharField(max_length=150, blank=True)  # filename in {{ STATIC_URL }}/icons
    tags = models.ManyToManyField(Tag, blank=True)

    def __unicode__(self):
        return u'%s' % self.slug


class Marker(models.Model):
    lat = models.FloatField(default=0)
    lon = models.FloatField(default=0)
    elev = models.FloatField(default=0)
    time = models.DateTimeField(default=datetime.datetime.now())
    title = models.CharField(max_length=160)
    descrption = models.TextField(blank=True)

    def __unicode__(self):
        return u'%s' % self.title


class Graphic(models.Model):
    #image = ImageWithThumbsField(upload_to="img/%Y/%m", sizes=((125, 125), (640, 640)))
    image = models.ImageField(upload_to="img/%Y/%m")
    caption = models.CharField(max_length=255, blank=True)
    marker = models.ForeignKey(Marker, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % self.image.name

    def save(self, *args, **kwargs):
        #Save first to ensure image is available for processing
        super(Graphic, self).save(*args, **kwargs)

        if self.image:
            try:  # If Graphic all ready created, don't overwrite marker
                hike = Hike.objects.get(pk=self.pk)
                return super(Graphic, self).save(*args, **kwargs)
            except:
                pass
            try:  # Generate thumbnail and extract GPS EXIF Data if available
                img = Image.open(MEDIA_ROOT + str(self.image.name))
                ret = {}
                exif_data = img._getexif()
                info = img._getexif()
                for tag, value in info.items():
                    decoded = TAGS.get(tag, tag)
                    ret[decoded] = value
                lat = [float(x)/float(y) for x, y in ret['GPSInfo'][2]]
                latref = ret['GPSInfo'][1]
                lon = [float(x)/float(y) for x, y in ret['GPSInfo'][4]]
                lonref = ret['GPSInfo'][3]

                lat = lat[0] + lat[1]/60 + lat[2]/3600
                lon = lon[0] + lon[1]/60 + lon[2]/3600
                if latref == 'S':
                    lat = -lat
                if lonref == 'W':
                    lon = -lon
                marker = Marker.objects.create(lat=lat, lon=lon, title=self.image.name)
                marker.save()
                self.marker = marker
            except Exception, e:
                print str(e) + " while saving image"

        return super(Graphic, self).save(*args, **kwargs)


class Post(models.Model):
    """Post model."""
    STATUS_CHOICES = (
        (1, ('Draft')),
        (2, ('Published')),
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique_for_date='publish', blank=True)
    author = models.ForeignKey(User, blank=True, null=True)
    tease = models.TextField(blank=True)
    body = models.TextField(blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=2)
    allow_comments = models.BooleanField(default=True)
    publish = models.DateTimeField(default=datetime.datetime.now)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, null=True)
    pictures = models.ManyToManyField(Graphic, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % self.title

    def get_absolute_url(self):
        return ('blog_detail', None, {
            'year': self.publish.year,
            'month': self.publish.strftime('%b').lower(),
            'day': self.publish.day,
            'slug': self.slug
        })

    def get_previous_post(self):
        return self.get_previous_by_publish(status__gte=2)

    def get_next_post(self):
        return self.get_next_by_publish(status__gte=2)

    def save(self, *args, **kwargs):
    # For automatic slug generation.
        if not self.slug:
            self.slug = slugify(self.title)[:50]

        return super(Post, self).save(*args, **kwargs)

def Post_pre_save(sender, **kwargs):
    instance = kwargs['instance']
    print "post pre_save"
    if instance.category == None:
        instance.category = Category.objects.get(pk=1)

pre_save.connect(Post_pre_save, sender=Post)


class Hike(Post):
    RATINGS = [(i, i) for i in range(5)]
    gps = models.FileField(upload_to="gps/%Y/%m")
    markers = models.ManyToManyField(Marker, blank=True)
    numMarkers = models.IntegerField(default=0)
    startMarker = models.IntegerField(default=0)
    rating = models.IntegerField(choices=RATINGS, default=0)
    difficulty = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
    # This doesn't yet work
        try:
            hike = Hike.objects.get(pk=self.pk)
            created = True
        except:
            created = False
            print "gpx re-parsing averted!"
        #Parse .gpx file and create Marker Objects
        if not created and self.gps:
            # We have to save the object initially so that we can
            # access the filename of the uploaded .gpx track
            super(Hike, self).save(*args, **kwargs)
            wpt = False
            file = open(MEDIA_ROOT + str(self.gps.name))
            trailhead = False
            for row in file:
                if wpt:
                    if "<elev" in row:
                        elev = row.split(">")[1].split("<")[0]
                    elif "<time" in row:  # 2012-02-19T20:58:56Z
                        thetime = time.strptime(row.split(">")[1].split("<")[0], "%Y-%m-%dT%H:%M:%SZ")
                    elif "<name" in row:
                        # <name><![CDATA[Conservation Corps Camp]]></name>
                        if "CDATA" in row:
                            name = row.split(">")[1].split("[")[2].split("]")[0]
                        else:
                            name = row.split(">")[1].split("<")[0]
                    elif "</wpt>" in row or "</trkpt" in row:
                        if "</trkpt" in row:
                            trailhead = True
                            name = str(self.title) + " Trailhead"
                        marker = Marker.objects.create(lat=lat, lon=lon, title=name, elev=elev)
                        if self.startMarker == 0:
                            self.startMarker = marker.pk
                        self.numMarkers += 1
                        #self.markers.add(mark
                        wpt = False
                #If waypoint, or first trackpoint, create a Marker
                if "<wpt " in row or ((not trailhead) and "<trkpt" in row):
                    wpt = True
                    geodat = row.split("\"")
                    lat = geodat[1]
                    lon = geodat[3]
                    thetime = ""
                    elev = 0
                    name = ""
        return super(Hike, self).save(*args, **kwargs)

#def save_marker(sender, instance, action, reverse, model, pk_set, using, **kwargs):
#    if action == 'pre_add':
#        markers = Marker.objects.all().order_by('-pk')[:instance.numMarkers]
#        for m in markers:
#            print "adding " + str(m)
#            instance.markers.add(m)

#def addMarkers(sender, instance, created, **kwargs):
#    markers = Marker.objects.all().order_by('-pk')[:instance.numMarkers]
#    for m in markers:
#        print "adding " + str(m)
#        instance.markers.add(m)

#m2m_changed.connect(save_marker, sender=Hike.markers.through)

#post_save.connect(addMarkers, sender=Hike)
