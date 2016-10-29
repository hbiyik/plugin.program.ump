import sys
import os
import xbmc
import xbmcaddon

from ump import teamkodi
from ump import install
install.sideload("script.trakt")
import traktapi

def init_addon(id,dir):
	trakt = xbmcaddon.Addon(id)
	sys.path.append(xbmc.translatePath(os.path.join(trakt.getAddonInfo('path'),dir)))

def run(ump):
	globals()["ump"]=ump
	tapi=traktapi.traktAPI()
	