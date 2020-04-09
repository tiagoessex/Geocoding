
Version: 0.0.1

# Description
* Given a list of geocoding services (with the respective keys), an address and/or entity name [, city, country], it returns a json containing the geocoding results, with **'status': 'OK'**. In caso, the geocode was impossible by using every available service, then returns a json with **'status': 'UNABLE'**, with all the others fields set to None.
* If no services are available, then an _OutOfServices_ exception will be throwed
* In case of incorrect usage (e.g.: incorrect arguments) or some other catastrophic event, a general _Exception_ will be throwed


# Requirements
* Python 3.7.x
* geopy
* certifi

# Fields
* formatted_address
* latitude
* longitude
* accuracy
* place_id
* type
* postcode
* input_string
* number_of_results
* status
* response
* localidade
* distrito
* concelho
* freguesia	
* service

# Available services
* Google
* TomTom
* Bing
* Here
* Azure
* Nominatum


# Example

```python
import geocode

# list of available services
services = [	
	{"id": "tomtom", "service": "TOMTOM", "key": "xxxxxxxxx"},				
	{"id": "here", "service": "HERE", "key": "", "app_id":"xxxxxxxxx","app_code":"yyyyyyyyyyyy"},
]

# services' names to ignore (optional)
ignore = []

try:
	geo = geocode.Geocode(services, ignore)
	result = geo.geocode(addr = 'rua da boavista, nº 50', local= 'porto', country = "Portugal", saveraw = True)
	print (result)
except geocode.OutOfServices as e:
	print (e)
except Exception as e:	
	print (e)	
```
