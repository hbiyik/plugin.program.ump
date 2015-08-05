import re

domain="http://mangafox.me"
encoding="utf-8"

def run(hash,ump):
	pg=ump.get_page(domain+hash,encoding)
	img=re.findall('src="(.*?)" onerror',pg)
	return {"img":img[0]}
	