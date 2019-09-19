# -*- coding: utf-8 -*-

#  Event Time Converter
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

from Converter import Converter
from Poll import Poll
from time import time
from Components.Element import cached, ElementError

class KravenFHDEventTime(Poll, Converter, object):
	STARTTIME = 0
	ENDTIME = 1
	REMAINING = 2
	PROGRESS = 3
	DURATION = 4
	RUNTIME = 5

	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		if type == "EndTime":
			self.type = self.ENDTIME
		elif type == "Remaining":
			self.type = self.REMAINING
			self.poll_interval = 60*1000
			self.poll_enabled = True
		elif type == "StartTime":
			self.type = self.STARTTIME
		elif type == "Duration":
			self.type = self.DURATION
		elif type == "Progress":
			self.type = self.PROGRESS
			self.poll_interval = 30*1000
			self.poll_enabled = True
		elif type == "RunTime":
			self.type = self.RUNTIME
			self.poll_interval = 1*1000
			self.poll_enabled = True
		else:
			raise ElementError("'%s' is not <StartTime|EndTime|Remaining|Duration|Progress|Runtime> for fenrisEventTime converter" % type)

	@cached
	def getTime(self):
		assert self.type != self.PROGRESS

		event = self.source.event
		if event is None:
			return None
			
		if self.type == self.STARTTIME:
			return event.getBeginTime()
		elif self.type == self.ENDTIME:
			return event.getBeginTime() + event.getDuration()
		elif self.type == self.DURATION:
			return event.getDuration()
		elif self.type == self.REMAINING:
			now = int(time())
			start_time = event.getBeginTime()
			duration = event.getDuration()
			end_time = start_time + duration
			if start_time <= now <= end_time:
				return (duration, end_time - now)
			else:
				return (duration, None)
		elif self.type == self.RUNTIME:
			now = int(time())
			duration = event.getDuration()
			start_time = event.getBeginTime()
			end_time = start_time + duration
			if start_time <= now <= end_time:
				return (duration, now - start_time)
			else:
				return (duration, None)
				

	@cached
	def getValue(self):
		assert self.type == self.PROGRESS

		event = self.source.event
		if event is None:
			return None

		now = int(time())
		start_time = event.getBeginTime()
		duration = event.getDuration()
		if start_time <= now <= (start_time + duration) and duration > 0:
			return (now - start_time) * 1000 / duration
		else:
			return None

	time = property(getTime)
	value = property(getValue)
	range = 1000

	def changed(self, what):
		Converter.changed(self, what)
		if self.type == self.PROGRESS and len(self.downstream_elements):
			if not self.source.event and self.downstream_elements[0].visible:
				self.downstream_elements[0].visible = False
			elif self.source.event and not self.downstream_elements[0].visible:
				self.downstream_elements[0].visible = True
