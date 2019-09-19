# -*- coding: utf-8 -*-

#  Service Icon Renderer
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

class KravenFHDServiceIcon(Renderer):

	def __init__(self):
		Renderer.__init__(self)
		self.pngname = ""
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
			elif attrib == "options":
				self.option = value
			else:
				attribs.append((attrib, value))
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	GUI_WIDGET = ePixmap

	def changed(self, what):
		if self.instance:
			if self.path:
			
				icon = ""
				
				if self.option == "VideoHeight":
					value = self.source.value
					if value > 1080:
						icon = "ico_uhd"
					elif value > 719:
						icon = "ico_hd_on"
					elif value > 0:
						icon = "ico_sd"
					else:
						icon = "ico_hd_off"
						
				elif self.option == "IsCrypted":
					bool = self.source.boolean
					if bool:
						icon = "ico_crypt_on"
					else:
						icon = "ico_crypt_off"
				
				elif self.option == "HasTelext":
					bool = self.source.boolean
					if bool:
						icon = "ico_txt_on"
					else:
						icon = "ico_txt_off"
				
				elif self.option == "HasHBBTV":
					bool = self.source.boolean
					if bool:
						icon = "ico_hbbtv_on"
					else:
						icon = "ico_hbbtv_off"
				
				elif self.option == "SubtitlesAvailable":
					bool = self.source.boolean
					if bool:
						icon = "ico_sub_on"
					else:
						icon = "ico_sub_off"
				
				elif self.option == "IsWidescreen":
					bool = self.source.boolean
					if bool:
						icon = "ico_format_on"
					else:
						icon = "ico_format_off"
				
				pngname = "/usr/share/enigma2/KravenFHD/" + self.path + icon + ".png"
				if fileExists(pngname):
					self.instance.setPixmapFromFile(pngname)
