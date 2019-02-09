import httplib2
import json
import os

def getGeocodeLocation(inputString):
    GOOGLE_KEY = os.environ.get('GOOGLE_KEY')
    locationString = inputString.replace(" ","+")
    url = ('https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s' % (locationString, GOOGLE_KEY))
    h = httplib2.Http()
    response, content = h.request(url,'GET')
    result = json.loads(content)
    return result

