# -*- coding: utf-8 -*-

import urllib2
import base64
import math
import re
from third import png
from third.jj import JJDecoder
from third.aa import AADecoder
import urllib
from HTMLParser import HTMLParser

domain="https://openload.co/"
encoding="utf-8"

def caesar_shift(s, shift=13):
    s2 = ''
    for c in s:
        if c.isalpha():
            limit = 90 if c <= 'Z' else 122
            new_code = ord(c) + shift
            if new_code > limit:
                new_code -= 26
            s2 += chr(new_code)
        else:
            s2 += c
    return s2

def unpack(html):
    strings = re.findall('{\s*var\s+a\s*=\s*"([^"]+)', html)
    shifts = re.findall('\)\);}\((\d+)\)', html)
    for s, shift in zip(strings, shifts):
        s = caesar_shift(s, int(shift))
        s = urllib.unquote(s)
        for i, replace in enumerate(['j', '_', '__', '___']):
            s = s.replace(str(i), replace)
        html += '<script>%s</script>' % (s)
    return html

def run(hash,ump,referer=None):
	url=domain+"embed/"+hash
	html = ump.get_page(url, None)
	try: html = html.encode('utf-8')
	except: pass
	html = unpack(html) 
	
	decodes = []
	hidden_id = ''
	for match in re.finditer('<script[^>]*>(.*?)</script>', html, re.DOTALL):
		decode = ''
		encoded = match.group(1)
		match = re.search("(ﾟωﾟﾉ.*?\('_'\);)", encoded, re.DOTALL)
		if match:
			print 1
			decode = AADecoder(match.group(1)).decode()
			decodes.append(decode)
			
		match = re.search('(.=~\[\].*\(\);)', encoded, re.DOTALL)
		if match:
			print 2
			decode = JJDecoder(match.group(1)).decode()
			decodes.append(decode)
		
		match = re.search(r'=\s*\$\("#([^"]+)"', decode, re.DOTALL | re.IGNORECASE)
		if match:
			print 3
			hidden_id = match.group(1)
	
	match = re.search(r'<span[^>]+id\s*="%s"[^>]*>([^<]+)' % (hidden_id), html, re.DOTALL | re.IGNORECASE)
	hidden_url = match.group(1)
	hiddenurl = HTMLParser().unescape(hidden_url)
	magic_number = 0
	for decode in decodes:
		match = re.search('charCodeAt\(\d+\)\s*\+\s*(\d+)\)', decode, re.DOTALL | re.I)
		if match:
			magic_number = match.group(1)
			break

	s = []
	for idx, i in enumerate(hiddenurl):
		j = ord(i)
		if (j >= 33 & j <= 126):
			j = 33 + ((j + 14) % 94)
			
		if idx == len(hiddenurl) - 1:
			j += int(magic_number)
		s.append(chr(j))
	res = ''.join(s)
	
	videoUrl = 'https://openload.co/stream/{0}?mime=true'.format(res)
	dtext = videoUrl.replace('https', 'http')
	return {"url":dtext,"referer":url}