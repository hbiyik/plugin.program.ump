# -*- coding: utf-8 -*-

import urllib2
import base64
import math
import re
from third import png
domain="https://www.openload.co/"
encoding="utf-8"
def run(hash,ump,referer=None):
	url=domain+"embed/"+hash
	HTTP_HEADER = {
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
		'Accept-Encoding': 'none',
		'Accept-Language': 'en-US,en;q=0.8',
		'Referer': url}  # 'Connection': 'keep-alive'

	data = ump.get_page(url, encoding,header=HTTP_HEADER)

	# If you want to use the code for openload please at least put the info from were you take it:
	# for example: "Code take from plugin IPTVPlayer: "https://gitlab.com/iptvplayer-for-e2/iptvplayer-for-e2/"
	# It will be very nice if you send also email to me samsamsam@o2.pl and inform were this code will be used

	# get image data
	imageData = re.search('''<img[^>]*?id="linkimg"[^>]*?src="([^"]+?)"''', data, re.IGNORECASE).group(1)

	imageData = base64.b64decode(imageData.split('base64,')[-1])
	_x, _y, pixel, _meta = png.Reader(bytes=imageData).read()

	imageData = None
	imageStr = ''
	try:
		for item in pixel:
			for p in item:
				# common.log_utils.log_notice('openload resolve : 1.7 %s' % p)
				imageStr += chr(p)
	except:
		pass

	# split image data
	imageTabs = []
	i = -1
	for idx in range(len(imageStr)):
		if imageStr[idx] == '\0':
			break
		if 0 == (idx % (12 * 20)):
			imageTabs.append([])
			i += 1
			j = -1
		if 0 == (idx % (20)):
			imageTabs[i].append([])
			j += 1
		imageTabs[i][j].append(imageStr[idx])

	# get signature data
	# sts, data = self.cm.getPage('https://openload.co/assets/js/obfuscator/numbers.js', {'header': HTTP_HEADER})
	data = ump.get_page('https://openload.co/assets/js/obfuscator/n.js',encoding, header=HTTP_HEADER)

	signStr = re.search('''['"]([^"^']+?)['"]''', data, re.IGNORECASE).group(1)

	# split signature data
	signTabs = []
	i = -1
	for idx in range(len(signStr)):
		if signStr[idx] == '\0':
			break
		if 0 == (idx % (11 * 26)):
			signTabs.append([])
			i += 1
			j = -1
		if 0 == (idx % (26)):
			signTabs[i].append([])
			j += 1
		signTabs[i][j].append(signStr[idx])

	# get link data
	linkData = {}
	for i in [2, 3, 5, 7]:
		linkData[i] = []
		tmp = ord('c')
		for j in range(len(signTabs[i])):
			for k in range(len(signTabs[i][j])):
				if tmp > 122:
					tmp = ord('b')
				if signTabs[i][j][k] == chr(int(math.floor(tmp))):
					if len(linkData[i]) > j:
						continue
					tmp += 2.5
					if k < len(imageTabs[i][j]):
						linkData[i].append(imageTabs[i][j][k])
	res = []
	for idx in linkData:
		res.append(''.join(linkData[idx]).replace(',', ''))

	res = res[3] + '~' + res[1] + '~' + res[2] + '~' + res[0]
	videoUrl = 'https://openload.co/stream/{0}?mime=true'.format(res)
	dtext = videoUrl.replace('https', 'http')
	request = urllib2.Request(dtext, None, HTTP_HEADER)
	response = urllib2.urlopen(request)
	url = response.geturl()
	response.close()
	return {"url":url,"referer":url}