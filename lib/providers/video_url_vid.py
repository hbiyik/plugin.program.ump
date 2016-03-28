import urlparse
import re
import time
from third import unpack

domain="http://vid.ag/"

def run(hash,ump,referer=None):
	src = ump.get_page(domain+hash,"utf8",referer=referer)
	packed=re.findall("script type='text/javascript'\>(eval\(function\(p.*?)\n</script>",src)
	data= unpack.unpack(packed[0]).encode("ascii","ignore").replace("\\","")
	files=re.findall('file:"([^,]*?)",label:"(.*?)"',data)
	vids={}
	for file in files:
		if not (file[0].endswith(".vtt") or file[0].endswith(".m3u8")):
			vids[file[1]]=file[0]
	return vids