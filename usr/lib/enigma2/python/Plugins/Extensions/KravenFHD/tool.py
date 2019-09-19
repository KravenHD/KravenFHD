# -*- coding: utf-8 -*-

#  Kraven Tool
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

from enigma import eTimer
from Screens.InfoBar import InfoBar

class KravenTool:

	def __init__(self):
		self.fb_proc_path = '/proc/stb/vmpeg'
		self.fb_info = ['dst_width',
		 'dst_height',
		 'dst_left',
		 'dst_top']
		self.new_fb_size_pos = None
		self.decoder = None
		self.delayTimer = None
		self.is_PiG = False
		return

	def getFBSize(self, decoder = 0):
		ret = []
		for val in self.fb_info:
			f = open('%s/%d/%s' % (self.fb_proc_path, decoder, val), 'r')
			fb_val = f.read().strip()
			ret.append(fb_val)
			f.close()

		if len(ret) == 4:
			return ret
		else:
			return None

	def setFBSize(self, fb_size_pos, decoder = 0, force = False):
		if self.delayTimer:
			self.delayTimer.stop()
		if InfoBar.instance and InfoBar.instance.session.pipshown or force:
			if fb_size_pos and len(fb_size_pos) >= 4:
				i = 0
				for val in self.fb_info:
					try:
						f = open('%s/%d/%s' % (self.fb_proc_path, decoder, val), 'w')
						fb_val = fb_size_pos[i]
						f.write(fb_val)
						f.close()
					except IOError:
						pass

					i += 1

				for val in ('00000001', '00000000'):
					try:
						f = open('%s/%d/%s' % (self.fb_proc_path, decoder, 'dst_apply'), 'w')
						f.write(val)
						f.close()
					except IOError:
						pass

	def delayTimerFinished(self):
		fb_size_pos = self.new_fb_size_pos
		decoder = self.decoder
		self.new_fb_size_pos = None
		self.decoder = None
		if not self.is_PiG:
			self.setFBSize(fb_size_pos, decoder)
		return

	def setFBSize_delayed(self, fb_size_pos, decoder = 0, delay = 1000):
		if fb_size_pos and len(fb_size_pos) >= 4:
			self.new_fb_size_pos = fb_size_pos
			self.decoder = decoder
			self.delayTimer = eTimer()
			self.delayTimer.callback.append(self.delayTimerFinished)
			self.delayTimer.start(delay)