from quality import vid
from third import imsize

#supported formats: flv,mp4
def video(head,dfunc=None,url=None,referer=None):
	m={}
	q=vid.vidqual(url,dfunc,referer)
	if not q=={}:
		m["type"]=q.get("type",-1)
		m["width"]=q.get("width",0)
		m["height"]=q.get("height",0)
		m["size"]=q.get("size",-1)
	else:
		print "Cant get video metadata"
	return m

#supported formats:gif,png,jpg
def image(head,dfunc=None,url=None,referer=None):
	try:
		head=dfunc(url,None,referer=referer,tout=1.5,range=(0,200))
		t,w,h=imsize.get_image_size(head)
	except imsize.NotEnoughData:
		head=dfunc(url,None,referer=referer,tout=1.5)
		t,w,h=imsize.get_image_size(head)
	return {"type":t,"width":w,"height":h}

#not yet audio quality check is supported
def audio(head,dfunc=None,url=None,referer=None):
	return {-1:None}