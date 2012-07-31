from django.contrib import admin
import models


class PostAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        print "wat"
        #if not change:
        #    obj.author = request.user
        #obj.save

admin.site.register(models.Post)
admin.site.register(models.Category)
admin.site.register(models.Tag)
admin.site.register(models.Marker)
admin.site.register(models.Graphic)