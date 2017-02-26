#
#  Version Converter
#
#  Coded by tomele and tbx for Kraven Skins
#
#  This code is licensed under the Creative Commons 
#  Attribution-NonCommercial-ShareAlike 3.0 Unported 
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/3.0/ 
#  or send a letter to Creative Commons, 559 Nathan 
#  Abbott Way, Stanford, California 94305, USA.
#

from Components.Converter.Converter import Converter
from Components.Element import cached
import os

class KravenFHDVersInfo(Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)
		self.type = str(type)
	
	@cached
	def getText(self):
		try:
			from boxbranding import getImageDistro
			if getImageDistro() == "openatv":
				version = os.popen("opkg status enigma2-plugin-skins-kravenfhd | grep -e 'Version' | cut -d '+' -f1").read()
				return version.rstrip()
			else:
				version = os.popen("opkg status enigma2-plugin-skin-kravenfhd | grep -e 'Version' | cut -d '+' -f1").read()
				return version.rstrip()
		except ImportError:
			version = os.popen("opkg status enigma2-plugin-skin-kravenfhd | grep -e 'Version' | cut -d '+' -f1").read()
			return version.rstrip()
	
	text = property(getText)
