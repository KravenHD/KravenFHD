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

		audio = service.audioTracks()

		if self.type == self.Dolby20:
			if audio:
				try:
					track = audio.getCurrentTrack()
					info = audio.getTrackInfo(track)
					language = info.getLanguage()
					if "2.0" in language:
						return True
					else:
						return False
				except:
					return False

		elif self.type == self.Dolby51:
			if audio:
				try:
					track = audio.getCurrentTrack()
					info = audio.getTrackInfo(track)
					language = info.getLanguage()
					if "5.1" in language:
						return True
					else:
						return False
				except:
					return False

		elif self.type == self.Dolby:
			if audio:
				try:
					track = audio.getCurrentTrack()
					info = audio.getTrackInfo(track)
					language = info.getLanguage()
					description = info.getDescription()
					if not "5.1" in language and not "2.0" in language:
						if "AC3" in description or "AC-3" in description or "DTS" in description or "AAC" in description or "Dolby" in description:
							return True
						else:
							return False
					else:
						return False
				except:
					return False

		elif self.type == self.Dolby_off:
			if audio:
				try:
					track = audio.getCurrentTrack()
					info = audio.getTrackInfo(track)
					language = info.getLanguage()
					description = info.getDescription()
					if not "5.1" in language and not "2.0" in language:
						if "AC3" in description or "AC-3" in description or "DTS" in description or "AAC" in description or "Dolby" in description:
							return False
						else:
							return True
					else:
						return False
				except:
					return False

	boolean = property(getBoolean)

	def changed(self, what):
		if what[0] is self.CHANGED_SPECIFIC:
			Converter.changed(self, what)
		elif what[0] is self.CHANGED_POLL:
			self.downstream_elements.changed(what)
