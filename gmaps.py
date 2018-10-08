import simplejson, urllib.request

def getGmapsDistance(o_lat, o_lon, d_lat, d_lon):
	o_coord = o_lat + ',' + o_lon
	d_coord = d_lat + ',' + d_lon
	url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=driving&language=en-EN&sensor=false&key=AIzaSyD7Ypq1A2P7NWFg3ca8ItPTe61laAq64AU".format(str(o_coord),str(d_coord))
	result = simplejson.load(urllib.request.urlopen(url))
	return result

print(getGmapsDistance('51.213', '4.406', '50.8873', '4.7223'))
