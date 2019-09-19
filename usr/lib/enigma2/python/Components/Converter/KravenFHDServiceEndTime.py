# -*- coding: utf-8 -*-

#  Service End Time Converter
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
from Poll import Poll
from enigma import iPlayableService, iPlayableServicePtr, iServiceInformation, eTimer, eLabel
from Components.Element import cached, ElementError
from time import localtime, strftime, time, gmtime, asctime
from Components.Sources.Clock import Clock


class KravenFHDServiceEndTime(Poll, Converter, object):
	TYPE_ENDTIME = 0

	def __init__(self, type):
		Poll.__init__(self)
		Converter.__init__(self, type)

		if type == "EndTime":
			self.type = self.TYPE_ENDTIME

		self.poll_enabled = True
  
        def getSeek(self):
		s = self.source.service
		return s and s.seek()

	@cached
	def getPosition(self):
		seek = self.getSeek()
		if seek is None:
			return None
		pos = seek.getPlayPosition()
		if pos[0]:
			return 0
		return pos[1]
        
        @cached
	def getLength(self):
		seek = self.getSeek()
		if seek is None:
			return None
		length = seek.getLength()
                if length[0]:
			return 0
		return length[1]

		
        @cached
	def getText(self):
                seek = self.getSeek()
		if seek is None:
			return ""
		else:
			if self.type == self.TYPE_ENDTIME:
				e = (self.length / 90000)        
                                s = self.position / 90000
                                return strftime("%H:%M", localtime(time() + (self.length / 90000 - self.position / 90000)))   
        
	range = 10000

	position = property(getPosition)
        length = property(getLength)
	text = property(getText)

	def changed(self, what):
		cutlist_refresh = what[0] != self.CHANGED_SPECIFIC or what[1] in (iPlayableService.evCuesheetChanged,)
		time_refresh = what[0] == self.CHANGED_POLL or what[0] == self.CHANGED_SPECIFIC and what[1] in (iPlayableService.evCuesheetChanged,)

		if time_refresh:
			self.downstream_elements.changed(what)