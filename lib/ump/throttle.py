import os
import xbmcvfs
import urllib
import json
from third import portalocker
import md5

class throttle():
    def __init__(self,path):
        self.path=path
        if not xbmcvfs.exists(path):
            xbmcvfs.mkdir(path)
    
    def check(self,tid):
        fname=os.path.join(self.path,tid,"")
        return xbmcvfs.exists(fname)
    
    def get(self,tid):
        fname=os.path.join(self.path,tid,"data.ascii")
        if xbmcvfs.exists(fname):
            f=xbmcvfs.File(fname,"rb")
            data=f.read()
            f.close()
            return data
    
    def do(self,tid,data):
        fname=os.path.join(self.path,tid,"")
        xbmcvfs.mkdir(fname)
        fname=os.path.join(self.path,tid,"data.ascii")
        f=xbmcvfs.File(fname,"wb")
        f.write(data)
        f.close()
        return True
    
    def id(self,*args,**kwargs):
        idt={"args":json.dumps(args),"kwargs":json.dumps(kwargs)}
        idt=md5.new(json.dumps(idt).encode("base64")[:-1]).hexdigest()
        print idt
        return idt