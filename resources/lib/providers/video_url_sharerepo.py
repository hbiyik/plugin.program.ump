import re

def run(hash,ump):
	src=ump.get_page("http://www.sharerepo.com/"+hash,"utf-8")
	key=re.findall("file: '(.*?)'",src)
	return {"url1":key[0]}