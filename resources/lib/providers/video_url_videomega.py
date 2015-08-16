import re
def run(hash,ump):
	src = ump.get_page("http://videomega.tv/view.php?ref="+hash["key"],"utf-8",referer=hash["referer"])
	return {"video":re.findall('<source src="(.*?)" type="video/mp4"/>',src)[0]}