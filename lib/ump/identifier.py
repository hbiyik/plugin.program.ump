from ump import defs
import json
import md5

class identifier():
    def __init__(self,ump):
        self.ump=ump
        
    def create(self,info=None):
        if not info: info=ump.info
        ptr=[self.ump.content_type,info.get("index","index")]
        mediatype=info.get("mediatype","mediatype")
        ptr.append(mediatype)
        for key in defs.mediapointer.get(mediatype,defs.MT_OTHER):
            ptr.append(info.get(key,key))
        return json.dumps(ptr)
    
    def mediacode(self,id):
        id=json.loads(id)
        contentype=id[0]
        indexer=id[1]
        mediatype=id[2]
        code=id[3]
        return contenttype,indexer,mediatype,code
    
    def createmd5(self,info):
        return md5.new(self.create(info)).hexdigest()