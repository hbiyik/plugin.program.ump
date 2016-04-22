import xbmc

class Mon(xbmc.Monitor):
    def __init__(self):
        self.ar=False
        
    def onAbortRequested(self):
        self.ar = True
        
    def abortRequested(self):
        return self.ar

class backwards():
    def __init__(self):
        self.m=xbmc.Monitor()
        if not hasattr(self.m,"abortRequested"):
            self.m=Mon()
       
    def abortRequested(self):
        return self.m.abortRequested()          