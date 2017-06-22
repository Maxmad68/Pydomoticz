#!/usr/bin/python
# -*- coding: utf-8 -*-

import json,urllib
import datetime,time

def jsonReponse(*args):
	return json.loads(urllib.urlopen(''.join(args)).read())

class Device(object):
	def __init__(self,parent,idx):
		self.parent = self._parent = parent
		self.idx = self._idx = idx
		
	def __getattr__(self, key):
		""" look for a 'save' attribute, or just 
		  return whatever attribute was specified """
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
		reponse = jsonReponse(self._parent._url,'/json.htm?type=devices&rid=%i'%self._idx)['result'][0]
		return reponse.keys()
		
	def __repr__(self):
		return '<Domoticz Device at idx %i>'%self._idx
		
	def on(self):
		return jsonReponse(self._parent._url,'/json.htm?type=command&param=switchlight&idx=%i&switchcmd=On'%self._idx)
		
	def off(self):
		return jsonReponse(self._parent._url,'/json.htm?type=command&param=switchlight&idx=%i&switchcmd=Off'%self._idx)
		
	def setLevel(self,level):
		return jsonReponse(self._parent._url,'/json.htm?type=command&param=switchlight&idx=%i&switchcmd=Set%%20Level&level=%s'%(self._idx,str(level)))
			
	def __call__(self,cmd):
		return jsonReponse(self._parent._url,'/json.htm?type=command&param=switchlight&idx=%i&switchcmd=%s'%(self._idx,cmd))
			

class Domoticz(object):
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
		reponse = jsonReponse(self._url,'/json.htm?type=devices&used=true&filter=all&favorite=1')
		now = datetime.datetime.now()
		self.status = reponse['status']
		self.title = reponse['title']
		self.ServerTime = datetime.datetime.strptime(reponse['ServerTime'],'%Y-%m-%d %H:%M:%S')
		self.sunrise = datetime.datetime(now.year,now.month,now.day,hour=int(reponse['Sunrise'].split(':')[0]),minute=int(reponse['Sunrise'].split(':')[1]),second=0)
		self.sunset = datetime.datetime(now.year,now.month,now.day,hour=int(reponse['Sunset'].split(':')[0]),minute=int(reponse['Sunset'].split(':')[1]),second=0)
		self.actTime = reponse['ActTime']
		self.startupTime = now - datetime.timedelta(seconds=self.actTime)
		devicesJson = reponse['result']
		self.devices = []
		for dev in devicesJson:
			self.devices.append(Device(self,int(dev['idx'])))
			
	def getDevices(self,**kwargs):
		matches = []
		for dev in self.devices:
			canMatch = True
			for arg in kwargs.keys():
				val = kwargs[arg]
				
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
		
		

