
import geocode


services = [	
				{"id": "tomtom", "service": "TOMTOM", "key": "xxxxxxxxxxxxxxxx"},				
				{"id": "here", "service": "HERE", "key": "", "app_id":"xxxxxxxxxxxxx","app_code":"yyyyyyyyyyyy"},
				{"id": "bing", "service": "BING", "key": "xxxxxxxxxxxxxxxxxxx"},				
				{"id": "google", "service": "GOOGLE", "key": "xxxxxxxxxxxxxxxxxxxx"},
			]
ignore = []


#print (geocode.__version__)
#print (geocode.__doc__)

geo = geocode.Geocode(services, ignore)
try:
	result = geo.geocode(addr = 'rua da boavista, nº 50', local= 'porto', country = "Portugal", saveraw = True)
	#result = geo.geocode(addr = 123, local= 'porto', country = "Portugal", saveraw = True)
	print (result)
except geocode.OutOfServices as e:
	print (e)
except Exception as e:	
	print (e)	


