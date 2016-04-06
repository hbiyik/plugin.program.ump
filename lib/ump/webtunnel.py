import random
import re
from urllib import urlencode
import urlparse

import xbmcaddon


addon = xbmcaddon.Addon('plugin.program.ump')

class tunnel():
	def __init__(self):
		self.mode="disabled"
		tunnels=["proxyduck"]
		self.entunnels=[]
		for tunnel in tunnels:
			if addon.getSetting("entn_%s"%tunnel)=="true":
				self.entunnels.append(tunnel)

	def set_tunnel(self,mode):
		if not mode=="random" and addon.getSetting("entn_%s"%mode)=="true":
			self.mode=mode
		elif len(self.entunnels):
			self.mode="random"
		else:
			self.mode="disabled"

		if self.mode=="random":
			self.mode=random.choice(self.entunnels)

	def pre(self,request):
		if self.mode == "disabled":
			return request
		if self.mode == "proxyduck":
			r="norefer"
			if request.has_header("Referer"):
				r=request.get_header("Referer")
			request._Request__original="http://proxyduck.net/proxy/browse.php?%s"%urlencode({"u":request.get_full_url(),"f":r})
			return request

	def post(self,stream):
		if self.mode == "disabled":
			return stream
		
		if self.mode == "proxyduck":
			stream=re.sub("\n.*?ginf={url:'http://proxyduck.net/proxy'.*?</script>","",stream)
			stream=re.sub('\n.*?<script type="text/javascript" src="http://proxyduck.net/proxy/includes.*?</script>',"",stream)
			stream=re.sub('\s*?<!-- PopAds.net Popunder Code for proxyduck.net -->.*?<!-- PopAds.net Popunder Code End -->',"\n",stream,flags=re.DOTALL)
			def clean(match):
				return match.group(1)+urlparse.parse_qs(match.group(2))["u"][0]+match.group(3)
			stream=re.sub("(\"|\')\/proxy\/browse\.php\?(.*?)(\"|\')", clean, stream)
			return stream