from django.shortcuts import render

from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from models import Post, Category, Hike, Marker


def home(request):
    dic = {}
    # Entry.objects.all()[:5]
    dic["posts"] = Post.objects.order_by('-publish').filter(status=2)[:10]
    print dic["posts"]
    dic["cats"] = Category.objects.all()
    return render_to_response('blog.html', dic, context_instance=RequestContext(request))


def filter(request, cat):
    dic = {}
    dic["cats"] = Category.objects.all()
    try:
        thecat = Category.objects.get(slug=cat)
    except:
        raise Http404
    dic["posts"] = thecat.post_set.filter(status=2).order_by('-publish')[:10]
    dic["thecat"] = cat
    return render_to_response('blog.html', dic, context_instance=RequestContext(request))


def article(request, slug):
    dic = {}
    dic["cats"] = Category.objects.all()
    try:
        post = Post.objects.get(slug=slug)
    except:
        raise Http404
    dic["thecat"] = post.category.slug.lower()
    if dic["thecat"] == "earth":
        post = Hike.objects.get(slug=post.slug)
        dic["scale"] = range(5)
        dic["rating"] = Hike.objects.get(slug=post.slug).rating
        print dic["rating"]
        if not (len(post.markers.all()) == post.numMarkers):
            #relate M2M markers
            print "adding markers"
            markers = Marker.objects.filter(pk__gt=post.startMarker - 1)
            markers = markers[:post.numMarkers + 1]

            for m in markers:
                print "adding " + str(m)
                post.markers.add(m)
            post.save()
    dic["posts"] = [post]
    # store in array so article template can extend blog which iterates over posts
    return render_to_response('article.html', dic, context_instance=RequestContext(request))
