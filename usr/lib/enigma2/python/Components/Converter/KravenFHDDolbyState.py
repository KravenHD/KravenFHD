# -*- coding: utf-8 -*-

#  Dolby State Converter
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

class KravenFHDDolbyState(Poll, Converter, object):

	Dolby20 = 1
	Dolby51 = 2
	Dolby = 3
	Dolby_off = 4
	
	def __init__(self, type):
	
		Converter.__init__(self, type)
		Poll.__init__(self)

		if type == "Dolby20":
			self.type = self.Dolby20
		elif type == "Dolby51":
			self.type = self.Dolby51
		elif type == "Dolby":
			self.type = self.Dolby
		elif type == "Dolby_off":
			self.type = self.Dolby_off

		self.poll_interval = 5000
		self.poll_enabled = True

	@cached
	def getText(self):

		return self.getDolby()
		
	text = property(getText)

	@cached
	def getBoolean(self):

		dolby = self.getDolby()
		
		if self.type == self.Dolby20 and dolby == "2.0":
			return True
		if self.type == self.Dolby51 and dolby == "5.1":
			return True
		if self.type == self.Dolby and dolby == "Dolby":
			return True
		if self.type == self.Dolby_off and dolby == "NoDolby":
			return True
		return False

	boolean = property(getBoolean)

	def getDolby(self):
	
		service = self.source.service

		if service:
			audio = service.audioTracks()
			if audio:
				n = audio.getNumberOfTracks()
				track = audio.getCurrentTrack()
				if n > 0 and track > -1:
					i = audio.getTrackInfo(track)
					description = i.getDescription()
					language = i.getLanguage()
					info = description + language
					
					if "2.0" in info:
						return "2.0"
					if "5.1" in info:
						return "5.1"
					if "AC3" in info or "AC-3" in info or "DTS" in info or "AAC" in info or "Dolby" in info:
						return "Dolby"
	
		return "NoDolby"

	def changed(self, what):
		if what[0] is self.CHANGED_SPECIFIC:
			Converter.changed(self, what)
		elif what[0] is self.CHANGED_POLL:
			self.downstream_elements.changed(what)
