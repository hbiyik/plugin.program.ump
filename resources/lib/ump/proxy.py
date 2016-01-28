from xml.dom import minidom
from third.socksipy import socks
import socket
import xbmc

def get_set(genset,n):
	nd=genset.getElementsByTagName(n)[0]
	if nd.lastChild is None:
		return nd.lastChild
	else:
		return nd.lastChild.data

def getsocket():
	try:
		gen_set=minidom.parse(xbmc.translatePath('special://home/userdata/guisettings.xml'))
		if not get_set(gen_set,"usehttpproxy").lower() == "false":
			s=[3,1,1,2,2][int(get_set(gen_set,"httpproxytype"))]
			socks.setdefaultproxy(s, get_set(gen_set,"httpproxyserver"), int(get_set(gen_set,"httpproxyport")),int(get_set(gen_set,"httpproxytype"))==4,get_set(gen_set,"httpproxyusername"),get_set(gen_set,"httpproxypassword"))
			return socks.socksocket
		else:
			return socket.socket
	except:
		return socket.socket