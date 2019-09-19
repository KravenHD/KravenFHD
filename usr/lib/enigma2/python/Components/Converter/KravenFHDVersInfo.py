# -*- coding: utf-8 -*-

#  Version Info Converter
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

class KravenFHDVersInfo(Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)
		self.type = str(type)
	
	@cached
	def getText(self):
		versFile = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/version"
		pFile = open(versFile,"r")
		for line in pFile:
			return line.rstrip()
		pFile.close()
	
	text = property(getText)
