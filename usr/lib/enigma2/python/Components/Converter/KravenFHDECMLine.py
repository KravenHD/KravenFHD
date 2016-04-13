#
#  ECM LINE Converter
#
#  Coded by tomele and tbx for Kraven Skins
#
#  This code is licensed under the Creative Commons
#  Attribution-NonCommercial-ShareAlike 4.0 International
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/4.0/
#

from enigma import iServiceInformation, iPlayableService
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.config import config
from Poll import Poll
import os, gettext

try:
	from enigma import eDVBCI_UI
	from enigma import eDVBCIInterfaces
	CI = True
except:
	CI = False

from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from Components.Language import language

lang = language.getLanguage()
os.environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("KravenFHD", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/KravenFHD/locale/"))

def _(txt):
	t = gettext.dgettext("KravenFHD", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

class KravenFHDECMLine(Poll, Converter, object):

	SATINFO = 0
	VERYSHORTCAID = 1
	VERYSHORTREADER = 2
	SHORTREADER = 3
	NORMAL = 4
	LONG = 5
	VERYLONG = 6

	FTAINVISIBLE = 0
	FTAVISIBLE = 1

	def __init__(self, type):
		Poll.__init__(self)
		Converter.__init__(self, type)

		args = type.split(',')
		if len(args) != 2:
			raise ElementError("type must contain exactly 2 arguments")

		type = args.pop(0)
		invisible = args.pop(0)

		if type == 'SatInfo':
			self.type = self.SATINFO
		elif type == 'VeryShortCaid':
			self.type = self.VERYSHORTCAID
		elif type == 'VeryShortReader':
			self.type = self.VERYSHORTREADER
		elif type == 'ShortReader':
			self.type = self.SHORTREADER
		elif type == 'Normal':
			self.type = self.NORMAL
		elif type == 'Long':
			self.type = self.LONG
		else:
			self.type = self.VERYLONG

		if invisible == "FTAInvisible":
			self.invisible = self.FTAINVISIBLE
		else:
			self.invisible = self.FTAVISIBLE

		self.poll_interval = 1000
		self.poll_enabled = True

	@cached
	def getText(self):

		if self.IsCrypted():
			try:
				f = open('/tmp/ecm.info', 'r')
				flines = f.readlines()
				f.close()
			except:

				if CI:
					NUM_CI=eDVBCIInterfaces.getInstance().getNumOfSlots()
					if NUM_CI > 0:
						found_caid = False
						service_caids = []
						service_caid_list = []
						caid = '0x0'
						service = self.source.service
						info = service and service.info()
						if info:
							service_caids = info.getInfoObject(iServiceInformation.sCAIDs)
							if service_caids:
								for service_caid in service_caids:
									service_caid_list.append((str(hex(int(service_caid)))))
								for act_slot in range(NUM_CI):
									ci_caids = []
									ci_caid_list = []
									ci_caids = eDVBCIInterfaces.getInstance().readCICaIds(act_slot)
									if ci_caids:
										for ci_caid in ci_caids:
											ci_caid_list.append(str(hex(int(ci_caid))))
										for service_caid in service_caid_list:
											if service_caid in ci_caid_list:
												if int(service_caid,16) > int(caid,16):
													found_caid = True
													caid = service_caid
													appname = eDVBCI_UI.getInstance().getAppName(act_slot)
													slot = act_slot

						if found_caid:
							caid = str(caid)
							caid = caid.lstrip('0x')
							caid = caid.upper()
							caid = caid.zfill(4)
							
							if ((caid>='1800') and (caid<='18FF')):
								system = 'System: NAGRA'
							elif ((caid>='1700') and (caid<='17FF')):
								system = 'System: BETA'
							elif ((caid>='0E00') and (caid<='0EFF')):
								system = 'System: POWERVU'
							elif ((caid>='0D00') and (caid<='0DFF')):
								system = 'System: CWORKS'
							elif ((caid>='0B00') and (caid<='0BFF')):
								system = 'System: CONAX'
							elif ((caid>='0900') and (caid<='09FF')):
								system = 'System: NDS'
							elif ((caid>='0600') and (caid<='06FF')):
								system = 'System: IRDETO'
							elif ((caid>='0500') and (caid<='05FF')):
								system = 'System: VIACCESS'
							elif ((caid>='0100') and (caid<='01FF')):
								system = 'System: SECA'
							else:
								system = _('System: unknown')
								
							caid = 'CAID: ' + str(caid)
							slot = 'Slot: ' + str(slot+1)
							appname = 'CI: ' + str(appname)
						else:
							system = _('System: unknown')
							caid = 'CAID: ' + _('unknown')
							slot = 'Slot: ' + _('unknown')
							appname = 'CI: ' + _('unknown')

						if self.type == self.SATINFO:
							ecmline = caid + ', ' + slot
						elif self.type == self.VERYSHORTCAID:
							ecmline = caid + ' - ' + slot
						elif self.type == self.VERYSHORTREADER:
							ecmline = slot + ' - ' + appname
						elif self.type == self.SHORTREADER:
							ecmline = caid + ' - ' + system + ' - ' + slot
						elif self.type == self.NORMAL:
							ecmline = caid + ' - ' + slot + ' - ' + appname
						elif self.type == self.LONG:
							ecmline = caid + ' - ' + system + ' - ' + slot + ' - ' + appname
						else:
							ecmline = 'CICAM' + ' - ' + caid + ' - ' + system + ' - ' + slot + ' - ' + appname
					else:
						ecmline = _('waiting for information ...')
				else:
					ecmline = _('no information available')

			else:

				camInfo = {}
				for line in flines:
					r = line.split(':', 1)
					if len(r) > 1 :
						camInfo[r[0].strip('\n\r\t ')] = r[1].strip('\n\r\t ')

				caid = camInfo.get('caid','')

				caid = caid.lstrip('0x')
				caid = caid.upper()
				caid = caid.zfill(4)

				if ((caid>='1800') and (caid<='18FF')):
					system = 'System: NAGRA'
				elif ((caid>='1700') and (caid<='17FF')):
					system = 'System: BETA'
				elif ((caid>='0E00') and (caid<='0EFF')):
					system = 'System: POWERVU'
				elif ((caid>='0D00') and (caid<='0DFF')):
					system = 'System: CWORKS'
				elif ((caid>='0B00') and (caid<='0BFF')):
					system = 'System: CONAX'
				elif ((caid>='0900') and (caid<='09FF')):
					system = 'System: NDS'
				elif ((caid>='0600') and (caid<='06FF')):
					system = 'System: IRDETO'
				elif ((caid>='0500') and (caid<='05FF')):
					system = 'System: VIACCESS'
				elif ((caid>='0100') and (caid<='01FF')):
					system = 'System: SECA'
				else:
					system = _('System: unknown')

				caid = 'CAID: ' + str(caid)

				prov = camInfo.get('prov','')
				prov = prov.lstrip("0x")
				prov = prov.upper()
				prov = prov.zfill(6)
				prov = 'Provider: ' + prov

				ecmtime = camInfo.get('ecm time','')
				if ecmtime:
					if "msec" in ecmtime:
						ecmtime = 'ECM: ' + ecmtime
					else:
						ecmtime = 'ECM: ' + ecmtime + ' s'

				hops = 'Hops: ' + str(camInfo.get('hops',''))
				address = 'Server: ' + str(camInfo.get('address',''))
				reader = 'Reader: ' + str(camInfo.get('reader',''))
				source = 'Source: ' + str(camInfo.get('source',''))

				using = str(camInfo.get('using',''))

				active = ''

				if source == 'emu':
					active = 'EMU'
					ecmline = active + ' - ' + caid

				elif using == 'emu':
					active = 'EMU'
					if self.type == self.VERYSHORT:
						ecmline = caid + ', ' + ecmtime
					else:
						ecmline = active + ' - ' + caid + ' - ' + ecmtime

				elif 'system' in camInfo :
					active = 'CCCAM'
					if self.type == self.SATINFO:
						ecmline = caid + ', ' + ecmtime
					elif self.type == self.VERYSHORTCAID:
						ecmline = caid + ' - ' + ecmtime
					elif self.type == self.VERYSHORTREADER:
						ecmline = address + ' - ' + ecmtime
					elif self.type == self.SHORTREADER:
						ecmline = caid + ' - ' + address + ' - ' + ecmtime
					elif self.type == self.NORMAL:
						ecmline = caid + ' - ' + address + ' - ' + hops + ' - ' + ecmtime
					elif self.type == self.LONG:
						ecmline = caid + ' - ' + system + ' - ' + address + ' - ' + hops + ' - ' + ecmtime
					else:
						ecmline = active + ' - ' + caid + ' - ' + system + ' - ' + address + ' - ' + hops + ' - ' + ecmtime

				elif 'reader' in camInfo :
					active = 'OSCAM'
					if self.type == self.SATINFO:
						ecmline = caid + ', ' + ecmtime
					elif self.type == self.VERYSHORTCAID:
						ecmline = caid + ' - ' + ecmtime
					elif self.type == self.VERYSHORTREADER:
						ecmline = reader + ' - ' + ecmtime
					elif self.type == self.SHORTREADER:
						ecmline = caid + ' - ' + reader + ' - ' + ecmtime
					elif self.type == self.NORMAL:
						ecmline = caid + ' - ' + reader + ' - ' + hops + ' - ' + ecmtime
					elif self.type == self.LONG:
						ecmline = caid + ' - ' + system + ' - ' + reader + ' - ' + hops + ' - ' + ecmtime
					else:
						ecmline = active + ' - ' + caid + ' - ' + system + ' - ' + reader + ' - ' + hops + ' - ' + ecmtime

				elif 'prov' in camInfo :
					active = 'MGCAMD'
					if self.type == self.SATINFO:
						ecmline = caid + ', ' + ecmtime
					elif self.type == self.VERYSHORTCAID:
						ecmline = caid + ' - ' + ecmtime
					elif self.type == self.VERYSHORTREADER:
						ecmline = source + ' - ' + ecmtime
					elif self.type == self.SHORTREADER:
						ecmline = caid + ' - ' + source + ' - ' + ecmtime
					elif self.type == self.NORMAL:
						ecmline = caid + ' - ' + source + ' - ' + prov + ' - ' + ecmtime
					elif self.type == self.LONG:
						ecmline = caid + ' - ' + system + ' - ' + source + ' - ' + prov + ' - ' + ecmtime
					else:
						ecmline = active + ' - ' + caid + ' - ' + system + ' - ' + source + ' - ' + prov + ' - ' + ecmtime

				else:
					active = _('unknown')
					ecmline = _('no information available')

		else:
			if self.invisible == self.FTAINVISIBLE:
				ecmline = ''
			else:
				ecmline = _('free to air')

		return ecmline

	text = property(getText)

	@cached
	def IsCrypted(self):
		crypted = 0
		service = self.source.service
		if service:
			info = service and service.info()
			if info:
				crypted = info.getInfo(iServiceInformation.sIsCrypted)
		return crypted

	def get_system_caid(self):
		caidlist = []
		service = self.source.service
		if service:
			info = service and service.info()
			if info:
				caids = info.getInfoObject(iServiceInformation.sCAIDs)
				if caids:
					for caid in caids:
						caidlist.append((str(hex(int(caid)))))
		return caidlist

	def changed(self, what):
		if (what[0] == self.CHANGED_SPECIFIC and what[1] == iPlayableService.evUpdatedInfo) or what[0] == self.CHANGED_POLL:
			Converter.changed(self, what)