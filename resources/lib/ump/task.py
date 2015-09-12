import threading
import Queue
from operator import itemgetter
import uuid
import time
import inspect
import traceback
import xbmcgui

#simple task manager but quite handy one
#can monitor different task groups and wait them to finish seperately
#can also priotrize the tasks  
#concurrentcy may be set to CPU count however my app heavily uses network stuff so i use more than 10 or more.
#dont mess with thread names

class killbill(Exception):
	pass
	
class manager(object):
	def __init__(self, concurrent=4):
		self.c = concurrent #concurrency count, runtime changable
		self.s = threading.Event() #stop flag
		self.q = [] #queue for the function when concurrency is not available
		self.p = [] #processed tasks
		self.g = [] #group ids

	def task(self,func,args):
		try:
			val=func(*args)
		except killbill:
			self.q=[]
			self.s.set()
			return None
		except Exception,e:
			frm = inspect.trace()[-1]
			mod = inspect.getmodule(frm[0])
			modname = mod.__name__ if mod else frm[1]
			errtype= e.__class__.__name__
			print traceback.format_exc()
			val=None

		if threading.activeCount()-1<=self.c and len(self.q)>0 and not self.s.isSet(): 
			self.q=sorted(self.q,key=itemgetter(1),reverse=True)
			t=self.q.pop(0)
			self.p.append(t)
			t[2].start()
		return val

	
	def add_queue(self,target,args,gid=0,pri=0):
		if not self.s.isSet():
			args=(target,args)
			t=threading.Thread(target=self.task,args=args)
			g=self.g
			g.append(gid)
			self.g=list(set(g))
			q,a,p=self.stats(gid)
			if a<=self.c:
				t.start()
				self.p.append((gid,pri,t))
				return t.name
			else:
				self.q.append((gid,pri,t))
				return t.name
		else:
			return None

	def stop(self):
		self.s.set()
		self.q=[]
		while True:
			self.join()
			break
				

	def join(self,gid=None,cnt=0,noblock=0):
		if cnt>0:
			dialog = xbmcgui.DialogProgress()
			dialog.create('UMP', 'Shutting Down Task Manager')
		while True:
			q,a,p=self.stats(gid)
			if cnt>0 and not q+a==0:
				dialog.update(100-100*(q+a)/cnt,"Shutting Down Tasks %d of %d"%(cnt-q-a,cnt))
			if (self.s.isSet() or q==0) and a<=noblock:
				break
			time.sleep(1)
		if cnt>0:
			dialog.close()
		return q,a,p
	
	def	create_gid(self):
		return uuid.uuid4().hex
		
	def stats(self,gid=None):
		q=0 #on queue
		p=0	#already processed
		a=0 #active thread
		ps= self.p
		qs= self.q
		t=[x.name for x in threading.enumerate()] #all active thread names
		for p1 in ps:
			if not p1[2].name in t and (gid is None and p1[0] in self.g or gid==p1[0]):
				p+=1
			if p1[2].name in t and (gid is None and p1[0] in self.g or gid==p1[0]):
				a+=1
		for q1 in qs:
			if gid is None and q1[0] in self.g or gid==q1[0]:
				q+=1
		return q,a,p