#!/usr/bin/python
# -*- coding: utf-8 -*-

import json,urllib
import datetime,time

#  Copyright 2017 Maxime MADRAU

__doc__ = """
	Simple wrapper for domoticz in Python.
	Pydomoticz enables to control a domoticz server and its devices
"""

__author__ = "Maxime Madrau (maxime@madrau.com)"

RFY = 'RFY'
TEMP = 'Temp'
HUMIDITY = 'Humidity'
BARO = 'Baro'
RAIN = 'Rain'
WIND = 'Wind'
LIGHT = SWITCH = 'Light/Switch'

def jsonReponse(*args):
	return json.loads(urllib.urlopen(''.join(args)).read())

class Device(object):
	"""
		Defines a Device object, that represents a domoticz device.
		A Device object can be controlled, and its values can be retrieved.
		Device objects are initialized by a Domoticz instance, and are got with domoticz_instance.getDevices() or domoticz_instance.devices
		
		Arguments:
			parent (Pydomoticz.Domoticz) : The parent Domoticz instance, representing the server of this device
			idx (int) : The domoticz IDX of this device
			name (basestring) : The name of this device
			xxx (object) : Every value defined from the domoticz server
	"""
	def __init__(self,parent,idx):
		self.parent = self._parent = parent
		self.idx = self._idx = idx
		self.type = map(str,jsonReponse(self._parent._url,'/json.htm?type=devices&rid=%i'%self._idx)['result'][0]['Type'].replace('Light/','').split(' + '))
		self.name = jsonReponse(self._parent._url,'/json.htm?type=devices&rid=%i'%self._idx)['result'][0]['Name']
		
	def __getattr__(self, key):
		key = key.replace('_','')
		reponse = jsonReponse(self._parent._url,'/json.htm?type=devices&rid=%i'%self._idx)['result'][0]
		for keyToTest in reponse.keys():
			low = keyToTest.lower()
			if low == key.lower():
				return reponse[keyToTest]
		
		return None
			
	def __getitem__(self,item):
		reponse = jsonReponse(self._parent._url,'/json.htm?type=devices&rid=%i'%self._idx)['result'][0]
		return reponse[item]
		
	def keys(self):
		"""
			Provide a list of every arguments available for this device
		"""
		reponse = jsonReponse(self._parent._url,'/json.htm?type=devices&rid=%i'%self._idx)['result'][0]
		return reponse.keys()
		
	def __repr__(self):
		return '<Domoticz Device %i>'%self._idx
		
	def on(self):
		"""
			Turn the device on
		"""
		return jsonReponse(self._parent._url,'/json.htm?type=command&param=switchlight&idx=%i&switchcmd=On'%self._idx)
		
	def off(self):
		"""
			Turn the device off
		"""
		return jsonReponse(self._parent._url,'/json.htm?type=command&param=switchlight&idx=%i&switchcmd=Off'%self._idx)
		
	def setLevel(self,level):
		"""
			Set a fixed level for the device
			Parameters:
				level (object) : The level to set
		"""
		return jsonReponse(self._parent._url,'/json.htm?type=command&param=switchlight&idx=%i&switchcmd=Set%%20Level&level=%s'%(self._idx,str(level)))
			
	def __call__(self,cmd):
		"""
			Call a Domoticz function for this device
			Paramteres:
				cmd (basestring) = The function
		"""
		return jsonReponse(self._parent._url,'/json.htm?type=command&param=switchlight&idx=%i&switchcmd=%s'%(self._idx,cmd))
			

class Domoticz(object):
	"""
		Defines a Domoticz object, that represents a domoticz server.
		A Domoticz object has devices that can be controlled.
		
		Parameters:
			- ip (basestring) : The IP address of the server
			- **user (basestring) : The username
			- **password (basestring) : The password
			
		Arguments:
			- user (basestring) : The username (r)
			- password (basestring) : The password
			- ip (basestring) : The IP address of the server
			- status (basestring) : The status of the server
			- ServerTime (datetime.datetime) : The date and the time of the server
			- sunrise (datetime.time) : The time of the today's sunrise
			- sunset (datetime.time) : The time of the today's sunset
			- devices ([Pydomoticz.Device, Pydomoticz.Device, ...]) : List of devices that can be controlled
			
	"""
	
	def __init__(self,ip,**kwargs):
		user = kwargs.get('user','')
		password = kwargs.get('password',None)
		fullUser = user if not password else user+':'+password
		self.user = user
		self.password = password
		self._fullUser = fullUser
		self.ip = ip
		self._url = 'http://%s@%s'%(fullUser,ip)
		self.connect()
		
	def connect(self):
		"""
			Connect to the Domoticz server with parameters used to create the Domoticz
		"""
		reponse = jsonReponse(self._url,'/json.htm?type=devices&used=true&filter=all&favorite=1')
		now = datetime.datetime.now()
		self.status = reponse['status']
		self.title = reponse['title']
		self.ServerTime = datetime.datetime.strptime(reponse['ServerTime'],'%Y-%m-%d %H:%M:%S')
		self.sunrise = datetime.time(hour=int(reponse['Sunrise'].split(':')[0]),minute=int(reponse['Sunrise'].split(':')[1]),second=0)
		self.sunset = datetime.time(hour=int(reponse['Sunset'].split(':')[0]),minute=int(reponse['Sunset'].split(':')[1]),second=0)
		self.actTime = reponse['ActTime']
		self.startupTime = now - datetime.timedelta(seconds=self.actTime)
		devicesJson = reponse['result']
		self.devices = []
		for dev in devicesJson:
			self.devices.append(Device(self,int(dev['idx'])))
			
	def getDevices(self,**kwargs):
		"""
			Get devices from their characteristics
			Parameters:
				** xxx (object) : Device instance argument
			
			Returns:
				[Pydomoticz.Device, Pydomoticz.Device, ...] : List of devices which arguments xxx is equal to its value
				
			Example:
				server.getDevices(name="MyStore")[0].name
				>>> "MyStore"
				
				server.getDevices(type=[Pydomoticz.HUMIDITY,Pydomoticz.BARO])[0].type
				>>> ['Temp', 'Humidity', 'Baro']
			
		"""
		matches = []
		for dev in self.devices:
			canMatch = True
			for arg in kwargs.keys():
				val = kwargs[arg]
				
				if arg == 'type':
					if isinstance(val, list):
						for v in val:
							if str(v) not in str(dev.__getattr__(arg)):
								canMatch = False
								break
					else:
						if str(val) not in str(dev.__getattr__(arg)):
							canMatch = False
							break
					
				else:
					if str(dev.__getattr__(arg)) != str(val):
						canMatch = False
						break
					
			if canMatch:
				matches.append(dev)
			else:
				continue
				
		return matches
			
				
			
	def __call__(**kwargs):
		str_ = ""
		for argument in kwargs:
			str_ += '&%s=%s'%argument
		return jsonReponse(self._url,str_)
	
	def __repr__(self):
		return '<Domoticz Server at "%s">'%self.ip
		
		

