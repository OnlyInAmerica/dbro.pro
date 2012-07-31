import os
import Image
from django import template
from dbro.settings import MEDIA_ROOT

register = template.Library()


@register.filter(name='thumbnail')
def thumbnail(file, size='104x104'):
    #Called on django ImageField, which returns unicode path 
    #loc = MEDIA_ROOT + file
    #file = open(loc)
    # defining the size
    x, y = [int(x) for x in size.split('x')]
    # defining the filename and the miniature filename
    filehead, filetail = os.path.split(file.path)
    #print "filehead: "+ filehead
    #print "filetail: "+ filetail 
    basename, format = os.path.splitext(filetail)
    miniature = basename + '_' + size + format
    filename = file.path
    miniature_filename = os.path.join(filehead, miniature)
    filehead, filetail = os.path.split(file.url)
    miniature_url = filehead + '/' + miniature
    #If a thumb exists but the orig file was modified AFTER the thumb, delete it
    if os.path.exists(miniature_filename) and os.path.getmtime(filename) > os.path.getmtime(miniature_filename):
        os.unlink(miniature_filename)
    # if the image wasn't already resized, resize it
    #print os.path.exists(miniature_filename)
    if not os.path.exists(miniature_filename):
        #print "generating new thumb"
        image = Image.open(filename)
        image.thumbnail([x, y], Image.ANTIALIAS)
        try:
            image.save(miniature_filename, image.format, quality=95)
            #print "saved 1"
        except Exception, e:
            print e
            image.save(miniature_filename, image.format, quality=95)
            #print "saved"

    return miniature_url
