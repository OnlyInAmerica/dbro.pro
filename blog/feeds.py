from django.contrib.syndication.views import Feed
from models import Post


class LatestEntriesFeed(Feed):
    title = "dbro.pro"
    #description = "hey"
    link = "/blog"

    def items(self):
        return Post.objects.all().order_by('-publish')[:5]

#    def link(self, obj):
#        return obj.get_absolute_url()

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        if item.tease:
            return item.tease
        else:
            return ""
