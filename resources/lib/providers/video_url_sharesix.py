import re

def run(hash,ump):
	src=ump.get_page("http://sharesix.com/"+hash,"utf-8",data={"method_free":"Free"})
	key=re.findall("lnk1 = '(.*?)'",src)
	return {"url1":key[0]}