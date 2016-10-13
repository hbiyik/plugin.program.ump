import xbmcaddon
import xbmc
from os import path

loglevel=1
addon = xbmcaddon.Addon('plugin.program.ump')
addon_dir = xbmc.translatePath( addon.getAddonInfo('path') )
addon_ldir = path.join(addon_dir,"lib")
addon_pdir = path.join(addon_ldir ,'providers')
addon_bdir = path.join(addon_dir,"resources","backup")
addon_setxml = path.join(addon_dir,"resources","settings.xml")
addon_bsetxml = path.join(addon_bdir,"settings.xml")
addon_ddir = xbmc.translatePath('special://home/userdata/addon_data/plugin.program.ump')
addon_stdir = xbmc.translatePath('special://home/userdata/addon_data/plugin.program.ump/stats')
addon_preffile= path.join(xbmc.translatePath('special://home/userdata/addon_data/plugin.program.ump'),"prefs.json")
addon_cookfile= path.join(xbmc.translatePath('special://home/userdata/addon_data/plugin.program.ump'),"cookie")
kodi_ddir = xbmc.translatePath('special://home/userdata/')
kodi_sdir=xbmc.translatePath('special://skin/')
kodi_setxml = xbmc.translatePath('special://home/userdata/advancedsettings.xml')
kodi_bsetxml = path.join(addon_bdir,"advancedsettings.xml")
kodi_favxml = xbmc.translatePath('special://home/userdata/favourites.xml')
kodi_bfavxml = path.join(addon_bdir,"favourites.xml")
kodi_guixml = xbmc.translatePath('special://home/userdata/guisettings.xml')
arturi = "https://offshoregit.com/boogiepop/dataserver/ump/images/"
#arturi = "http://boogie.us.to/dataserver/ump/images/"
#arturi="D:/projects/git/dataserver/dataserver/ump/images/"
addonsxmluri="http://boogie.us.to/repository.boogie.dist/addons.xml"
#content types
CT_AUDIO, CT_IMAGE, CT_VIDEO, CT_UMP = "audio", "image","video","ump" ##content types
LI_CTS={CT_AUDIO:"music",CT_IMAGE:"pictures",CT_VIDEO:"video",CT_UMP:"video"}
LI_SIS={CT_AUDIO:"audio",CT_IMAGE:"video",CT_VIDEO:"video",CT_UMP:"video"}
WID={CT_AUDIO:10502,CT_IMAGE:10002,CT_VIDEO:10025}
#media types
MT_MOVIE="movie"
MT_TVSHOW,MT_SEASON,MT_EPISODE="tvshow","season","episode",
MT_ANIMEMOVIE="animemovie"
MT_ANIMESHOW,MT_ANIMEEPISODE="animeshow","animeepisode"
MT_ARTIST,MT_MUSICALBUM,MT_MUSIC="artist","musicalbum","song"
MT_MANGA,MT_MANGACHAPTER="mang","mangachapter"
MT_OTHER="other"

mediapointer={
         MT_MOVIE:["code"],
         MT_TVSHOW:["code"],
         MT_SEASON:["code","season"],
         MT_EPISODE:["code","season","episode"],
         MT_ANIMEMOVIE:["code"],
         MT_ANIMESHOW:["code"],
         MT_ANIMEEPISODE:["code","epsiode"],
         MT_ARTIST:["code"],
         MT_MUSICALBUM:["code","album"],
         MT_MUSIC:["code","album","title"],
         MT_MANGA:["code"],
         MT_MANGACHAPTER:["code","episode"],
         MT_OTHER:["code"]
         }

#media type to kodi content categories
media_to_cc={
         MT_MOVIE:"movies",
         MT_TVSHOW:"tvshows",
         MT_SEASON:"albums",
         MT_EPISODE:"episodes",
         MT_ANIMEMOVIE:"movies",
         MT_ANIMESHOW:"tvshows",
         MT_ANIMEEPISODE:"episodes",
         MT_ARTIST:"albums",
         MT_MUSICALBUM:"albums",
         MT_MUSIC:"albums",
         MT_MANGA:"albums",
         MT_MANGACHAPTER:"albums",
         MT_OTHER:"files"      
             }

VIEW_MODES={
	"list":{
        'skin.confluence': 50,
        'skin.aeon.nox': 50,
        'skin.aeon.nox.5': 50,
        'skin.confluence-vertical': 50,
        'skin.jx720': 50,
        'skin.pm3-hd': 50,
        'skin.rapier': 50,
        'skin.simplicity': 50,
        'skin.slik': 50,
        'skin.touched': 50,
        'skin.transparency': 50,
        'skin.xeebo': 50,
		},
	"thumb":{
        'skin.confluence': 500,
        'skin.aeon.nox': 551,
        'skin.aeon.nox.5': 500,
        'skin.confluence-vertical': 500,
        'skin.jx720': 52,
        'skin.pm3-hd': 53,
        'skin.rapier': 50,
        'skin.simplicity': 500,
        'skin.slik': 53,
        'skin.touched': 500,
        'skin.transparency': 53,
        'skin.xeebo': 55,
		},
	}