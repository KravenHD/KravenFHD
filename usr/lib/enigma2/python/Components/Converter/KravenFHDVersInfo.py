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
