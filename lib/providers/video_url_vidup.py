import re
import time
from third import unpack


domain="http://vidup.me/"
def run(hash,ump,referer=None):
	src = ump.get_page(domain+hash,"utf8",referer=referer)
	return dict(re.findall("\{ label\: '(.*?)', file: '(.*?)'",src))