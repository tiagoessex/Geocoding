#import pandas as pd
#import logging
#import time
#import re
#import random
import csv



from geopy.geocoders import GoogleV3
from geopy.geocoders import TomTom
from geopy.geocoders import Nominatim
from geopy.geocoders import Bing
from geopy.geocoders import Here
from geopy.geocoders import AzureMaps

from geopy.exc import (
    GeocoderQueryError,
    GeocoderQuotaExceeded,
    ConfigurationError,
    GeocoderParseError,
    GeocoderAuthenticationFailure,
    GeocoderInsufficientPrivileges,
    GeocoderTimedOut,
    GeocoderServiceError,
    GeocoderUnavailable,
    GeocoderNotFound
)


import ssl
import certifi
import geopy.geocoders
ctx = ssl.create_default_context(cafile=certifi.where())
geopy.geocoders.options.default_ssl_context = ctx



############ logging ############

#logger = logging.getLogger("root")
#logger.setLevel(logging.DEBUG)
# create console handler
#ch = logging.StreamHandler()
#ch.setLevel(logging.DEBUG)
#logger.addHandler(ch)


############ ERRORS ############

class OutOfServices(Exception): 
	# Constructor or Initializer 
	def __init__(self, value): 
		self.value = value 
  
	# __str__ is to print() the value 
	def __str__(self): 
		return(repr(self.value)) 


class UnableToGeocode(Exception): 
	# Constructor or Initializer 
	def __init__(self, value): 
		self.value = value 
  
	# __str__ is to print() the value 
	def __str__(self): 
		return(repr(self.value)) 
		
class Geocode():

	#SERVICES = []

	#IGNORE = []

	CURRENT_SERVICE = 0


	geolocator_google = None
	geolocator_here = None
	geolocator_bing = None
	geolocator_tomtom = None
	geolocator_azure = None
	geolocator_nominatum = None

	#SHOW_ERRORS = True



	def __init__(self, services = None, ignore = None):
		self.SERVICES = services
		self.IGNORE = ignore





	############ SERVICES ############

	def initOutput(self):
		output={}
		output["formatted_address"] = None
		output["latitude"] = None
		output["longitude"] = None
		output["accuracy"] = None
		output["place_id"] = None
		output["type"] = None
		output["postcode"] = None
		output["input_string"] = None
		output["number_of_results"] = None
		output["status"] = None
		output["response"] = None
		output["localidade"] = None
		output["distrito"] = None
		output["concelho"] = None
		output["freguesia"] = None	
		output["service"] = self.SERVICES[self.CURRENT_SERVICE]['service']
		return output
		
		

	def google(self, addr, local, country, saveraw):
		
		output=self.initOutput()		
		address = "" if addr is None else addr
		address = address + ("" if local is None else "," + local)
		address = address + ("" if country is None else "," + country)
		
		# init service if not init yet
		if not self.geolocator_google:		
			self.geolocator_google = GoogleV3(api_key=self.SERVICES[self.CURRENT_SERVICE]['key'])
		
		# geocode address
		location = self.geolocator_google.geocode(address,exactly_one=False) #, components={"country": "PT"})
		if location is not None:
			answer = location[0].raw

			output['status'] = "OK"		
			output["formatted_address"] = location[0].address
			output["latitude"] = location[0].latitude
			output["longitude"] = location[0].longitude
			output["accuracy"] = answer.get('geometry').get('location_type')
			output["place_id"] = answer.get("place_id")
			output["type"] = ",".join(answer.get('types'))
			output["postcode"] = ",".join([x['long_name'] for x in answer.get('address_components') 
									  if 'postal_code' in x.get('types')])
			output["input_string"] = address
			output["number_of_results"] = len(location)
			output["localidade"] = ",".join([x['long_name'] for x in answer.get('address_components') 
									  if 'locality' in x.get('types')]).split(',')[0]
			
			
			output["service"] = self.SERVICES[self.CURRENT_SERVICE]['service']
			
			if saveraw:
				output["response"] = location[0].raw		
			
		else:
			output['status'] = "ZERO_RESULTS"
		
		return output


	def tomtom(self, addr, local, country, saveraw):
		output=self.initOutput()	
		# create query	
		address = "" if addr is None else addr
		address = address + ("" if local is None else "," + local)
		address = address + ("" if country is None else "," + country)
		# init service if not init yet
		if not self.geolocator_tomtom:		
			self.geolocator_tomtom = TomTom(api_key=self.SERVICES[self.CURRENT_SERVICE]['key'])#,default_scheme = 'https')

		# geocode address
		location = self.geolocator_tomtom.geocode(address, exactly_one=False) #, components={"country": "PT"})
		if location is not None:
			answer = location[0].raw
			
			output['status'] = "OK"
			output["latitude"] = location[0].latitude
			output["longitude"] = location[0].longitude
			
			output["accuracy"] = answer.get('score')
			output["input_string"] = address
			output["number_of_results"] = len(location)#answer.get("numResults")
			output["place_id"] = answer.get("id")
			
			if  answer.get("address"):
				output["distrito"] = answer.get("address").get("countrySubdivision")
				# maybe?
				output["concelho"] = answer.get("address").get("municipality")
				output["freguesia"] = answer.get("address").get("municipalitySubdivision")
				output["formatted_address"] = answer.get('address').get('freeformAddress')
				CPext = answer.get("address").get('extendedPostalCode')
				CP = answer.get("address").get('postalCode')
				if CPext:
					CPext = CPext.split(',')[0]
					CPext = CPext[:4] + '-' + CPext[4:]
					output["postcode"] = CPext
				elif CP:
					output["postcode"] = CP.split(',')[0]
				
				
				
			output["type"] = answer.get('type')
			#output["query_type"] = answer.get("queryType")
			
			# maybe?
			#output["localidade"] = answer.get("address").get("municipality")
			
			
			
			
			output["service"] = self.SERVICES[self.CURRENT_SERVICE]['service']
			
			if saveraw:
				output["response"] = location[0].raw	

		else:
			output['status'] = "ZERO_RESULTS"
		
		return output


	def nominatim(self, addr, local, country, saveraw):
		output=self.initOutput()	
		
		# create query	
		address = "" if addr is None else addr
		address = address + ("" if local is None else "," + local)
		address = address + ("" if country is None else "," + country)
		
		'''
		query = {	'street': data[1],
					'city':data[2],
					'country': 'Portugal'
				}
		'''
		
		# init service if not init yet
		if not self.geolocator_nominatum:		
			self.geolocator_nominatum = Nominatim(user_agent="tests_1")
		
		
		# geocode address
		location = self.geolocator_nominatum.geocode(address, exactly_one=False,  addressdetails=True)
		if location is not None:
			answer = location[0].raw
			
			output['status'] = "OK"
			output["latitude"] = location[0].latitude
			output["longitude"] = location[0].longitude
			output["number_of_results"] = len(location)
			#output["accuracy"] = answer.get('importance')
			output["place_id"] = answer.get("osm_id")
			output["input_string"] = address
			if answer.get("address"):
				output["postcode"] = re.sub('[^0-9-]+', '', answer.get("address").get("postcode")) ###???
				output["freguesia"] = answer.get("address").get("suburb")
				output["localidade"] = answer.get("address").get("city")
				if not output["localidade"]:
					output["localidade"] = answer.get("address").get("town")
				output["formatted_address"] = answer.get('address').get('display_name')
				
			output["type"] = answer.get('osm_type')
			
			output["service"] = self.SERVICES[self.CURRENT_SERVICE]['service']
			
			if saveraw:
				output["response"] = location[0].raw		

		else:
			output['status'] = "ZERO_RESULTS"
		
		return output
		
		

	def bing(self, addr, local, country, saveraw):
		output=self.initOutput()	
		
		# create query	
		address = "" if addr is None else addr
		address = address + ("" if local is None else "," + local)
		address = address + ("" if country is None else "," + country)
		
		# init service if not init yet
		if not self.geolocator_bing:		
			self.geolocator_bing = Bing(api_key=self.SERVICES[self.CURRENT_SERVICE]['key'])


		# geocode address
		location = self.geolocator_bing.geocode(address,  exactly_one=False) #culture='PT',  include_neighborhood=True,
		if location is not None:
			answer = location[0].raw
			
			output['status'] = "OK"
			output["latitude"] = location[0].latitude
			output["longitude"] = location[0].longitude
			output["number_of_results"] = len(location)
			
			
			if answer.get("address"):
				output["formatted_address"] = answer.get('address').get('formattedAddress')
				output["localidade"] = answer.get("address").get("locality")
				output["distrito"] = answer.get("address").get("adminDistrict")
				output["concelho"] = answer.get("address").get("adminDistrict2")
				output["freguesia"] = answer.get("address").get("neighborhood")		
				output["postcode"] = answer.get("address").get("postalCode")
			
			output["accuracy"] = answer.get('confidence')
			
			output["input_string"] = address
			
			
			output["service"] = self.SERVICES[self.CURRENT_SERVICE]['service']
			

			if saveraw:
				output["response"] = location[0].raw	

		else:
			output['status'] = "ZERO_RESULTS"
		
		return output






	def here(self, addr, local, country, saveraw):
		output=self.initOutput()	
		
		# create query	
		address = "" if addr is None else addr
		address = address + ("" if local is None else "," + local)
		address = address + ("" if country is None else "," + country)
		

		
		# init service if not init yet
		if not self.geolocator_here:		
			self.geolocator_here = Here(app_id=self.SERVICES[self.CURRENT_SERVICE]['app_id'], app_code=self.SERVICES[self.CURRENT_SERVICE]['app_code'])


		# geocode address
		location = self.geolocator_here.geocode(address, exactly_one=False,language="pt-PT")
		if location is not None:
			answer = location[0].raw
			
			output['status'] = "OK"
			output["latitude"] = location[0].latitude
			output["longitude"] = location[0].longitude
			output["number_of_results"] = len(location)
			
			output["input_string"] = address
			
			output["accuracy"] = answer.get('Relevance')
			
			if answer.get("Location"):
				output["formatted_address"] = answer.get("Location").get('Address').get('Label')
				output["place_id"] = answer.get("Location").get("LocationId")
				
			
			if answer.get("Location"):
				if answer.get("Location").get("Address"):
					output["postcode"] = answer.get("Location").get("Address").get("PostalCode")	
					# all 4 are not tghrustworthy
					output["freguesia"] = answer.get("Location").get("Address").get("District")		
					output["distrito"] = answer.get("Location").get("Address").get("County")
					output["concelho"] = answer.get("Location").get("Address").get("City")
					output["localidade"] = answer.get("Location").get("Address").get("City")		
			

			
			output["service"] = self.SERVICES[self.CURRENT_SERVICE]['service']
			

			if saveraw:
				output["response"] = location[0].raw

		else:
			output['status'] = "ZERO_RESULTS"
		
		return output




	###

	def azure(self, addr, local, country, saveraw):
		output=self.initOutput()	
		
		# create query	
		address = "" if addr is None else addr
		address = address + ("" if local is None else "," + local)
		address = address + ("" if country is None else "," + country)
		
		
		# init service if not init yet
		if not self.geolocator_azure:		
			self.geolocator_azure = AzureMaps(subscription_key=self.SERVICES[self.CURRENT_SERVICE]['key'])


		# geocode address
		location = self.geolocator_azure.geocode(address, exactly_one=False,language="pt-PT")
		if location is not None:
			answer = location[0].raw
			
			output['status'] = "OK"
			output["latitude"] = location[0].latitude
			output["longitude"] = location[0].longitude
			output["number_of_results"] = len(location)
			
			output["input_string"] = address
			
			output["accuracy"] = answer.get('score')
			
			output["place_id"] = answer.get("id")
			
			if answer.get("address"):
				output["formatted_address"] = answer.get('address').get('freeformAddress')
				output["distrito"] = answer.get("address").get("countrySubdivision")
				# maybe?
				output["concelho"] = answer.get("address").get("municipality")
				output["freguesia"] = answer.get("address").get("municipalitySubdivision")
				CPext = answer.get("address").get('extendedPostalCode')
				CP = answer.get("address").get('postalCode')
				if CPext:
					CPext = CPext.split(',')[0]
					CPext = CPext[:4] + '-' + CPext[4:]
					output["postcode"] = CPext
				elif CP:
					output["postcode"] = CP.split(',')[0]
			
			output["type"] = answer.get('type')			

			output["service"] = self.SERVICES[self.CURRENT_SERVICE]['service']			

			if saveraw:				
				output["response"] = location[0].raw		

		else:
			output['status'] = "ZERO_RESULTS"
		
		return output






	############ PROCESS FILE ############

	def getService(self):
		
		
		if  self.CURRENT_SERVICE >= len(self.SERVICES):
			raise UnableToGeocode("Unable to geocode entity.")

		if  len(self.IGNORE) >= len(self.SERVICES):
			raise OutOfServices("No service available.")
		
		for i in self.SERVICES:
			if self.SERVICES[self.CURRENT_SERVICE]['service'] in self.IGNORE:
				self.CURRENT_SERVICE = self.CURRENT_SERVICE + 1
				if  self.CURRENT_SERVICE >= len(self.SERVICES):
					raise UnableToGeocode("Unable to geocode entity.")
			else:
				break
		

		
		if "GOOGLE" in self.SERVICES[self.CURRENT_SERVICE]['service']:
			return self.google
		elif "TOMTOM" in self.SERVICES[self.CURRENT_SERVICE]['service']:
			return self.tomtom
		elif "NOMINATUM" in self.SERVICES[self.CURRENT_SERVICE]['service']:
			return self.nominatim
		elif "BING" in self.SERVICES[self.CURRENT_SERVICE]['service']:
			return self.bing
		elif "HERE" in self.SERVICES[self.CURRENT_SERVICE]['service']:
			return self.here	
		elif "AZURE" in self.SERVICES[self.CURRENT_SERVICE]['service']:
			return self.azure	
			
			
		return None
		
			

	# service = None => all available
	def geocode(self, addr = None, local= None, country = "Portugal", saveraw = True, service = None):	
		geocoded = False
		self.CURRENT_SERVICE = 0
		geocode_result = None
		
		if service:
			for s in self.SERVICES:
				if s['service'] != service:
					self.IGNORE.append(s['service'])

		while not geocoded:
			try:				
				serv = self.getService()	
				geocode_result = serv(addr, local, country, saveraw)
				if geocode_result['status'] == "OK":
					geocoded = True
					break
				else:
					self.CURRENT_SERVICE = self.CURRENT_SERVICE + 1
				'''
						else:
							if DEBUG:
								logger.error ('\n--------------------------------------------------------------------')
								logger.error ('ERROR: no addr/name for id_localization [{}].'.format(address.split('|')[0]))
								logger.error ('Passing to next address.')
								logger.error ('--------------------------------------------------------------------')
							CURRENT_SERVICE = 0
							geocode_result = initOutput()
							geocode_result['id_localization'] = address.split('|')[0]
							geocode_result['status'] = "NO_DATA"				
							break	
				'''
			except UnableToGeocode as e:
				if self.SHOW_ERRORS:
					pass
					#logger.error ('\n--------------------------------------------------------------------')
					#logger.error ('ERROR: Unable to geocode addr [{}].'.format(addr))
					#logger.error ('Passing to next address.')
					#logger.error ('--------------------------------------------------------------------')
				self.CURRENT_SERVICE = 0
				geocode_result = self.initOutput()
				geocode_result['status'] = "UNABLE"
				geocode_result['service'] = "ALL"
				break
			except OutOfServices as e:
				#if self.SHOW_ERRORS:
				#	logger.error ('\n--------------------------------------------------------------------')
				#	logger.error ('ERROR: you reached the limit on all services. No more services available.')
				#	logger.error ('Saving the all sucessuful results and exiting the application.')
				#	logger.error ('--------------------------------------------------------------------')
				raise
				#return None
			except (GeocoderQueryError,GeocoderAuthenticationFailure,GeocoderInsufficientPrivileges,ConfigurationError):
				#if self.SHOW_ERRORS:
				#	logger.error ('\n--------------------------------------------------------------------')
				#	logger.error ('ERROR: something wrong with either the service or the query.')
				#	logger.error ('Check service: [{}]'.format(self.SERVICES[self.CURRENT_SERVICE]['id']))
				#	logger.error ('Passing to the next service.')
				#	logger.error ('--------------------------------------------------------------------')
				self.IGNORE.append(self.SERVICES[self.CURRENT_SERVICE]['service'])
			except GeocoderQuotaExceeded:
				#if self.SHOW_ERRORS:
				#	logger.error ('\n--------------------------------------------------------------------')
				#	logger.error ('ERROR: you have reached the end of your quota for service [{}].'.format(self.SERVICES[self.CURRENT_SERVICE]['id']))
				#	logger.error ('Passing to the next service.')
				#	logger.error ('--------------------------------------------------------------------')
				self.IGNORE.append(self.SERVICES[self.CURRENT_SERVICE]['service'])
			except GeocoderTimedOut:
				#if self.SHOW_ERRORS:
				#	logger.error ('\n--------------------------------------------------------------------')
				#	logger.error ('TIMEOUT: something went wrong with the geocoding the address: [{}].'.format(addr))
				#	logger.error ('while using service [{}].'.format(self.SERVICES[self.CURRENT_SERVICE]['id']))
				#	logger.error ('Passing to the next service.')
				#	logger.error ('--------------------------------------------------------------------')
				self.IGNORE.append(self.SERVICES[self.CURRENT_SERVICE]['service'])
			except (GeocoderServiceError,GeocoderUnavailable):
				#if self.SHOW_ERRORS:
				#	logger.error ('\n--------------------------------------------------------------------')
				#	logger.error ('ERROR: service unavailable or unknown error for service [{}].'.format(self.SERVICES[self.CURRENT_SERVICE]['id']))
				#	logger.error ('Passing to the next service.')
				#	logger.error ('--------------------------------------------------------------------')
				self.IGNORE.append(self.SERVICES[self.CURRENT_SERVICE]['service'])
			except GeocoderNotFound:
				#if self.SHOW_ERRORS:
				#	logger.error ('\n--------------------------------------------------------------------')
				#	logger.error ('ERROR: unknown service > [{}].'.format(self.SERVICES[self.CURRENT_SERVICE]['id']))				
				#	logger.error ('check if this service still exists!')
				#	logger.error ('Passing to the next service.')
				#	logger.error ('--------------------------------------------------------------------')
				self.IGNORE.append(self.SERVICES[self.CURRENT_SERVICE]['service'])
			except Exception as e:				
				#logger.error ('\n--------------------------------------------------------------------')
				#logger.error("Unknown catastrophic error while processing address: {}".format(addr))
				#logger.error('while using service > [{}].'.format(self.SERVICES[self.CURRENT_SERVICE]['id']))	
				#logger.error("Check the error and correct it before restart the application.")
				#logger.error(str(e))
				#logger.error('--------------------------------------------------------------------')
				raise
				#return None

		
		return geocode_result
		
		


