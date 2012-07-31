import urllib2
from bs4 import BeautifulSoup
import re
import sys, os

def parseListings(url='http://sfbay.craigslist.org/bia/'):


    TARGET_URL = url
    try:
        html = urllib2.urlopen(url)
        nextUrl = None
        response={}

        #If we're on a non-standard clist page
        # i.e: no search params, not a second,third page of results etc.
        if "?" in url:
            print '? found'
            #nextUrl = url.rsplit(";",1)[0]
            try:
                #If we're all ready displaying a non-first page of results:
                #UGH sometimes clist uses ; sometimes & to separate s param!
                if ";" in url:
                    if "s=" in url.rsplit(";",1)[1]:
                        nextIndex = (int(url.rsplit(";", 1)[1][2]) + 1) * 100
                        nextUrl = str(url.rsplit(";", 1)[0]) + ';s=' + str(nextIndex)
                    #Else we're on the first page of a query result
                    else:
                        nextIndex=100
                        nextUrl=url + ';s=' + nextIndex
                    print ';Next: ' + str(nextUrl)
                elif "&" in url:
                    if "s=" in url.rsplit("&",1)[1]:
                        nextIndex = (int(url.rsplit("&", 1)[1][2]) + 1) * 100
                        nextUrl = str(url.rsplit("&", 1)[0]) + '&s=' + str(nextIndex)
                    #Else we're on the first page of a query result
                    else:
                        nextIndex=100
                        nextUrl=url + '&s=' + nextIndex
                    print '&Next: ' + str(nextUrl)
            except Exception, e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]      
                print(exc_type, fname, exc_tb.tb_lineno)
                pass
        else: 
            #On a non-first page of a standard result
            #http://sfbay.craigslist.org/bia/index100.html
            if '00.html' in url.rsplit('/',1)[1]:
                nextIndex = ((int(url.rsplit('/'), 1)[1][5]) + 1) * 100
                nextUrl = str(url.rsplit('/', 1)[0]) + '/index' + str(nextIndex) + '.html'
            # On the first page of a standard result
            # Seriously, like there could be more than
            # 4 TYPES OF RESULT PAGES ON CRAIGSLIST
            else:
                nextUrl = url + 'index100.html'
        response['next'] = nextUrl
        #Search queries have separate NEXT page of results behavior
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]      
        print(exc_type, fname, exc_tb.tb_lineno)
        #output.write("Bad URL you dummy.")
        raise Exception("BAD URL","DUMMY")
    soup = BeautifulSoup(html)

    pattern = re.compile("$")

    ps = soup.find_all('p', 'row')

    listings = []
    for p in ps:
        listing = {}
        try:
            #print p
            #image = p.find_all(attrs={'id': re.compile(r".*\bimage\b.*")})
            images = p.find_all(attrs={'class': 'ih'})
            image_url = ""
            for image in images:
                #images:5N45Ia5K33Le3Ff3Hfc3me530f1cc929918aa.jpg
                image_url = str(image['id']).split(":")[1]
                #output.write("<img width=\"500px\" src=\"http://images.craigslist.org/"+image+"\"/>")
            if image_url == "":
                pass
            listing_url = p.find('a')['href']
            text = p.get_text()
            price = text.split("$")
            location = text.split("(")[1].split(")")[0]
            if len(price) == 2:
                description = price[0].split(" ",1)[1].rsplit("-",1)[0]
                location_and_price = price[1].split(" ")
                price = location_and_price[0]
                #location = location_and_price[1]
                #print "location: " + location
                #print "price: $" + price
                #print "description:" + description.rsplit("-",1)[0].strip()
            else:
                price = "?"
                description = price[0].split("-",1)[0]
                location = price[0].split("-",1)[1]
            listing['price'] = price
            listing['location'] = location
            listing['description'] = description
            listing['url'] = listing_url
            listing['image_url'] = image_url
            #output.write("<br>$"+price.encode('utf-8')+"<br>"+description.encode('utf-8')+"<br>"+location.encode('utf-8'))
            #A listing
            #image = p.find(class="ih")
            #print image
            listings.append(listing)
        except Exception, e:
            print e
            pass
    response['listings']=listings
    return response
