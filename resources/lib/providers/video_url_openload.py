# -*- coding: utf-8 -*-

import re
import urllib2

domain="https://www.openload.co/"

def run(hash,ump,referer=None):
	data=ump.get_page(domain+"embed/"+hash,None)
	
	data = data.replace('\\/', '/') \
		.replace('&amp;', '&') \
		.replace('\xc9', 'E') \
		.replace('&#8211;', '-') \
		.replace('&#038;', '&') \
		.replace('&rsquo;', '\'') \
		.replace('\r', '') \
		.replace('\n', '') \
		.replace('\t', '') \
		.replace('&#039;', "'")

	content = ''

	patron = "<video(?:.|\s)*?<script\s[^>]*?>((?:.|\s)*?)<\/script"
	matches = re.compile(patron, re.IGNORECASE).findall(data)
	if len(matches) > 0:
		from third import aa
		content = aa.AADecoder(matches[0]).decode()

	if not content:
		patron = "(\s*eval\s*\(\s*function(?:.|\s)+?)<\/script>"
		matches = re.compile(patron, re.IGNORECASE).findall(data)
		if len(matches) > 0:
			from third import unpack
			from third import jj
			unpacked = unpack.unpack(matches[0])
			content = jj.JJDecoder(unpacked).decode()

	if content:
		patron = r'window\.vr\s*=\s*"(.*?)\?'
		matches = re.compile(patron, re.IGNORECASE).findall(content.replace('\\', ''))
		if len(matches) > 0:
			headers = { 'User-Agent' : ump.ua }
			req = urllib2.Request(matches[0], None, headers)
			return {"url":{"url":urllib2.urlopen(req).geturl(),"referer":domain+"embed/"+hash}}