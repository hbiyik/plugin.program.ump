from task import manager
import threading
import time
m=manager(10)
def f2(s,i):
	time.sleep(i)
	print s + str(i)

def f(s,i):
	time.sleep(i)
	for i in range(2):
		m.add_queue(f2,("g1 p1 in function",1),1,1)
		m.join(1)
	print s + str(i)

m.add_queue(f,("g2 p2 in function",1),2,2)
m.join()

m.stop()
print [x.name for x in threading.enumerate()]