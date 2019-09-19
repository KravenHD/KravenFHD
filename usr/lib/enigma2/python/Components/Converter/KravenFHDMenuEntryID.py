# -*- coding: utf-8 -*-

#  Menu Entry ID Converter
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

class KravenFHDMenuEntryID(Poll,Converter,object):
	def __init__(self, type):
		Poll.__init__(self)
		Converter.__init__(self, type)
		self.poll_interval = 100
		self.poll_enabled = True
		self.type = str(type)
	
	@cached
	def getText(self):
		cur = self.source.current
		if cur and len(cur) > 2:
			return "Menu: " + cur[2]
		return ""	
	
	text = property(getText)
