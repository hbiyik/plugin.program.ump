import json
import re
import video_url_vk

def run(hash,ump):
	[hash,ref]=json.loads(hash)
	src=ump.get_page(hash,"iso-8859-9")
	vk_link=re.findall('getJSON\("(.*?)"',src)
	return video_url_vk.run(vk_link[0],ump)