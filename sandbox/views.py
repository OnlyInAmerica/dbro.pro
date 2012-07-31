from django.shortcuts import render_to_response
from django.http import HttpResponse
import craigslist
from forms import UrlForm
from django.template import RequestContext

def photocraig(request):
    if request.method == 'POST':
        form = UrlForm(request.POST)
        if form.is_valid():
            try:
                if not("craigslist.org" in str(request.POST['url'])):
                    return HttpResonse("Bad url")
                response = craigslist.parseListings(request.POST['url'])
                form = UrlForm()
                print 'NEXT: ' + str(response['next'])
                return render_to_response('janklist.html', {'form': form, 'listings': response['listings'], 'next': response['next']},  context_instance=RequestContext(request))
            except Exception, e:
                print e
                return HttpResponse("Bad url")
        else:
            return HttpResponse("Bad form data")
    else:
        form = UrlForm()
        #return HttpResponse("test")
        #Include Request Context for CSRF Protection
        return render_to_response('janklist.html', {'form': form, },  context_instance=RequestContext(request) )
