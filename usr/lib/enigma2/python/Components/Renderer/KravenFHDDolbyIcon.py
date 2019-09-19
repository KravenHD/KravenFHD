# -*- coding: utf-8 -*-

#  Dolby Icon Renderer
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

from Renderer import Renderer 
from enigma import ePixmap
from Tools.Directories import fileExists

class KravenFHDDolbyIcon(Renderer):

	def __init__(self):
		Renderer.__init__(self)
		self.pngname = ''
		self.path = ""

	def applySkin(self, desktop, parent):
		attribs = []
		for (attrib, value,) in self.skinAttributes:
			if attrib == 'path':
				self.path = value
				if value.endswith("/"):
					self.path = value
				else:
					self.path = value + "/"
			else:
				attribs.append((attrib, value))
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	GUI_WIDGET = ePixmap

	def changed(self, what):
		if self.instance:
			if self.path:
				dolbytext = self.source.text
				if dolbytext == "2.0":
					icon = "ico_dolby_20"
				elif dolbytext == "5.1":
					icon = "ico_dolby_51"
				elif dolbytext == "Dolby":
					icon = "ico_dolby_on"
				else:
					icon = "ico_dolby_off"
				pngname = "/usr/share/enigma2/KravenFHD/" + self.path + icon + ".png"
				if fileExists(pngname):
					self.instance.setPixmapFromFile(pngname)
