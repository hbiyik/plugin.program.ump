import urlparse
import re
import time

domain="http://thevideo.me/"

def run(hash,ump,referer=None):
	src = ump.get_page(domain+hash,"utf8",referer=referer)
	vars=["op","usr_login","id","fname","referer","hash","inhu"]
	data={}
	for var in vars:
		data[var]=re.findall('type="hidden" name="'+var+'" value="(.*?)"',src)[0]
	vars2=["gfk","_vhash"]
	for var in vars2:
		data[var]=re.findall("name: '"+var+"', value: '(.*?)'",src)[0]
	time.sleep(1)
	data["imhuman"]=""
	src = ump.get_page(domain+hash,"utf8",data=data,referer=domain+hash)
	files=re.findall("label: '(.*?)', file: '(.*?)'",src)
	return dict(files)