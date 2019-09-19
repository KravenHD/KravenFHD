# -*- coding: utf-8 -*-

#  Clock To Text Converter
#
#  Coded/Modified/Adapted by Team Kraven
#  Based on VTi and/or OpenATV image source code
#  Based on Clock To Text by Diamondear and plnick
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
from time import localtime, strftime
from Components.Element import cached

class KravenFHDClockToText(Converter, object):
	DEFAULT = 0
	WITH_SECONDS = 1
	IN_MINUTES = 2
	DATE = 3
	FORMAT = 4
	AS_LENGTH = 5
	TIMESTAMP = 6
	ANALOG_SEC = 7
	ANALOG_MIN = 8
	ANALOG_HOUR = 9
	
	# add: date, date as string, weekday, ... 
	# (whatever you need!)
	
	def __init__(self, type):
		Converter.__init__(self, type)
		if type == "WithSeconds":
			self.type = self.WITH_SECONDS
		elif type == "InMinutes":
			self.type = self.IN_MINUTES
		elif type == "Date":
			self.type = self.DATE
		elif type == "AsLength":
			self.type = self.AS_LENGTH
		elif type == "Timestamp":
			self.type = self.TIMESTAMP
		elif str(type).find("Format") != -1:
			self.type = self.FORMAT
			self.fmt_string = type[7:]
		elif type == "AnalogSeconds":
			self.type = self.ANALOG_SEC
		elif type == "AnalogMinutes":
			self.type = self.ANALOG_MIN
		elif type == "AnalogHours":
			self.type = self.ANALOG_HOUR
		else:
			self.type = self.DEFAULT

	@cached
	def getText(self):
		time = self.source.time
		if time is None:
			return ""

		# handle durations
		if self.type == self.IN_MINUTES:
			return "%d min" % (time / 60)
		elif self.type == self.AS_LENGTH:
			return "%d:%02d" % (time / 3600, (time / 60) - ((time / 3600) * 60))
		elif self.type == self.TIMESTAMP:
			return str(time)
		
		t = localtime(time)
		
		if self.type == self.WITH_SECONDS:
			return "%2d:%02d:%02d" % (t.tm_hour, t.tm_min, t.tm_sec)
		elif self.type == self.DEFAULT:
			return "%02d:%02d" % (t.tm_hour, t.tm_min)
		elif self.type == self.DATE:
			return_str = strftime("%A %B %d, %Y", t)
			weekday_long = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
			month_long = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
			str_fmt_values = {
						"%B" : month_long,
						"%A" : weekday_long,
					}
			
			for key in str_fmt_values:
				for value in str_fmt_values[key]:
					r_value = _(value)
					if return_str.find(value) != -1:
						return_str = return_str.replace(value, r_value)
						break
			
			return return_str
		
		elif self.type == self.FORMAT:
			weekday_long = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
			weekday_short = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
			month_long = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
			month_short = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
			str_fmt_values = {
						"%B" : month_long,
						"%b" : month_short,
						"%A" : weekday_long,
						"%a" : weekday_short,
					}
			
			return_str = strftime(self.fmt_string, t)
			
			for key in str_fmt_values:
				if self.fmt_string.find(key) != -1:
					for value in str_fmt_values[key]:
						if key == "%b" and value == "May":
							r_value = _(value)[:3]
						else:
							r_value = _(value)
						if return_str.find(value) != -1:
							return_str = return_str.replace(value, r_value)
							break
			return return_str
		elif self.type == self.ANALOG_SEC:
			return "%02d" % t.tm_sec
		elif self.type == self.ANALOG_MIN:
			return "%02d" % t.tm_min
		elif self.type == self.ANALOG_HOUR:
			ret = (t.tm_hour*5)+(t.tm_min/12);
			return "%02d" % ret
		else:
			return "???"

	text = property(getText)
