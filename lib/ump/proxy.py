import socket
from xml.dom import minidom

import xbmc

from third.socksipy import socks


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
			ret= socks.socksocket
		else:
			ret= socket.socket
	except:
		ret= socket.socket
	if gen_set:
		gen_set.unlink()
	return ret