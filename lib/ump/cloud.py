from third import dropbox
import xbmcgui

def upload(content,name,overwrite=True):
    dropbox.client.DropboxClient("oDWx2zTSXZAAAAAAAAAACCD5aQr2FgS-fe33WMr7moiZr9aHAp0gpuvUyXtiDHX5").put_file("/%s"%name, content,overwrite=overwrite)
    
def upload_log(head,msg,name,locals,errlog,kodilog,umplog):
    dialog = xbmcgui.Dialog()
    if(dialog.yesno(head,msg)):
        content="LOCAL INFO:\r\n%s\r\nERROR LOG:\r\n%s\r\nKODI LOG:\r\n%s\r\nUMP LOG:\r\n%s"%(locals,errlog,kodilog,umplog)
        upload(content,name)
    else:
        print errlog
        
def collect_log(logtype,head,msg,umplog,e=None):
    errlog=""
    fname=logtype
    umplog=umplog.split("\n")
    umplog="\r\n".join(umplog[::-1])
    if not e is None:
        import inspect
        import traceback
        frm = inspect.trace()[-1]
        mod = inspect.getmodule(frm[0])
        modname = mod.__name__ if mod else frm[1]
        errtype= e.__class__.__name__
        fname+="_"+errtype
        errlog=errtype+"\r\n"+traceback.format_exc().replace("\n","\r\n")
    import os
    from third import logviewer
    logmodule=logviewer.Logmodule()
    kodilog=logmodule.getcontent()
    from datetime import datetime
    fname+="_"+datetime.utcnow().strftime("%Y%m%d+%H%M%S")
    import platform
    localdata="PLATFORM        : "+os.name
    fname+="_"+os.name
    localdata+="\r\nRELEASE         : "+platform.release()
    fname+="_"+platform.release()
    localdata+="\r\nENVIRONMENT     : "+str(os.environ)
    import xbmc
    localdata+="\r\nXBMC VERSION    : "+xbmc.getInfoLabel( "System.BuildVersion" )
    fname+="_"+xbmc.getInfoLabel( "System.BuildVersion" )
    localdata+="\r\nPYTHON VERSION  : "+platform.python_version()
    fname+="_"+platform.python_version()
    localdata+="\r\n"
    fname=fname.replace(" ","_").replace("/","-").replace(":","-").replace("?","-").replace(".","-")
    fname+=".log"
    upload_log(head,msg,fname,localdata,errlog,kodilog,umplog)