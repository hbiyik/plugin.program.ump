import re
domain="http://www.veterok.tv"
encoding="utf-8"
def run(hash,ump,referer=None):
	page=ump.get_page(domain+"/v/"+hash,encoding,referer=referer)
	files=re.findall("files\[\".*?\"\]\=\"(.*?)\"",page)
	return {"video":files[0]}

