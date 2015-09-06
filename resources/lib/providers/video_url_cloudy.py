import urlparse
import re

def run(hash,ump,referer=None):
	src = ump.get_page("https://www.cloudy.ec/embed.php?id="+hash,"utf8")
	keys={}
	keys["file"]=re.findall('file: ?"(.*?)"',src)[0]
	keys["key"]=re.findall('key: ?"(.*?)"',src)[0]
	src = ump.get_page("https://www.cloudy.ec/api/player.api.php","utf8",query=keys)
	keys=urlparse.parse_qs(src)
	return {keys["title"][0]:keys["url"][0]}