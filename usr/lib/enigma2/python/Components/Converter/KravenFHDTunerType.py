# -*- coding: utf-8 -*-

#  Tuner Type Converter
#
#  Coded/Modified/Adapted by Team Kraven
#  Based on VTi and/or OpenATV image source code
#
#  This code is licensed under the Creative Commons 
#  Attribution-NonCommercial-ShareAlike 3.0 Unported 
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/3.0/ 
#  or send a letter to Creative Commons, 559 Nathan 
#  Abbott Way, Stanford, California 94305, USA.
#
#  If you think this license infringes any rights,
#  please contact Team Kraven at info@coolskins.de

from Components.Converter.Converter import Converter
from Components.Element import cached
from Poll import Poll
from enigma import iServiceInformation

class KravenFHDTunerType(Poll, Converter, object):

	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.poll_interval = 1000
		self.poll_enabled = True

	@cached
	def getText(self):
		
		type = ""
		stream = False

		service = self.source.service
		info = service and service.info()

		distro = self.getE2DistroVersion()
		if info:
			if distro == "VTi":
				stream = info.getInfo(iServiceInformation.sIsIPStream) == 1
			else:
				stream = service.streamed() is not None
			
		if stream:
			type = "STREAM"
		elif info:
			tpdata = info.getInfoObject(iServiceInformation.sTransponderData)
			if tpdata:
				type = tpdata.get("tuner_type", "")
			else:
				type = "STREAM"
			
			if type == "DVB-S" and tpdata.get("system", 0) == 1:
				type = "DVB-S2"

		return type

	text = property(getText)

	def getE2DistroVersion(self):
		try:
			from boxbranding import getImageDistro
			if getImageDistro() == "openatv":
				return "openatv"
			elif getImageDistro() == "teamblue":
				return "teamblue"
			elif getImageDistro() == "VTi":
				return "VTi"
		except ImportError:
			return "VTi"
