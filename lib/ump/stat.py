import os
import md5
import time
import defs

def mkdir(*paths):
    path=os.path.join(*paths)
    if not os.path.exists(path):os.makedirs(path)

class stats(ump):
    def __init(self,ump):
        self.ump=ump
        self.watchedids=[] #cache wacthed ids in ram on each run to make it faster
        mkdir(ump.defs.addon_stdir)
        
    def _checkid(self,id):
        return id in self.watchedids or os.path.exists(os.path.join(defs.addon_stdir,id))
        
    def markwatched(self,info=None):
        if not info:info=self.ump.info
        id=ump.identifier.createmd5()
        mkdir(ump.defs.addon_stdir,id)
        f = open(os.path.join(ump.defs.addon_stdir,id,"timestamp"),'w')
        f.write(str(time.time()))
        f.close()
        self.watchedids.append(id)
        
    def iswatched(self,info=None):
        if not info:info=self.ump.info
        mediatype=info.get("mediatype",defs.MT_OTHER)
        if mediatype==defs.MT_OTHER:return 0
        for i in range(len(defs.mediapointer["mediatype"])):
            nestedinfo=info[:i+1]
            nestedid=ump.identifier.createmd5(nestedinfo)
            if self._checkid(nestedid):
                self.watchedids.append(id)
                return 1