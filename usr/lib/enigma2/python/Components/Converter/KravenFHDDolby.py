from Components.Converter.Converter import Converter
from Components.Element import cached
from Poll import Poll

class KravenFHDDolby(Poll, Converter, object):
	Dolby20 = 1
	Dolby51 = 2
	Dolby = 3
	Dolby_off = 4
	
	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)

		if type == "Dolby20":
			self.type = self.Dolby20
		elif type == "Dolby51":
			self.type = self.Dolby51
		elif type == "Dolby":
			self.type = self.Dolby
		elif type == "Dolby_off":
			self.type = self.Dolby_off

		self.poll_interval = 5000
		self.poll_enabled = True

	@cached
	def getBoolean(self):
		service = self.source.service
		if not service:
			return False
			
		if self.type in (self.Dolby20, self.Dolby51, self.Dolby, self.Dolby_off):
			audio = service.audioTracks()
			if audio:
				n = audio.getNumberOfTracks()
				track = audio.getCurrentTrack()
				if n > 0 and track > -1:
					i = audio.getTrackInfo(track)
					description = i.getDescription()
					language = i.getLanguage()
					info = description + language
					
					if self.type == self.Dolby20:
						if "2.0" in info:
							return True
						else:
							return False
							
					elif self.type == self.Dolby51:
						if "5.1" in info:
							return True
						else:
							return False
							
					elif self.type == self.Dolby:
						if not "5.1" in info and not "2.0" in info:
							if "AC3" in info or "AC-3" in info or "DTS" in info or "AAC" in info or "Dolby" in info:
								return True
							else:
								return False
						else:
							return False
							
					elif self.type == self.Dolby_off:
						if not "5.1" in info and not "2.0" in info:
							if "AC3" in info or "AC-3" in info or "DTS" in info or "AAC" in info or "Dolby" in info:
								return False
							else:
								return True
						else:
							return False
							
				return True
			return False

	boolean = property(getBoolean)

	def changed(self, what):
		if what[0] is self.CHANGED_SPECIFIC:
			Converter.changed(self, what)
		elif what[0] is self.CHANGED_POLL:
			self.downstream_elements.changed(what)
