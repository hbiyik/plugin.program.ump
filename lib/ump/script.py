import sys

for s in sys.argv:
	print s

if len(sys.argv)>1:
	if sys.argv[1]=="addfav":
		from bookmark import add
		add(sys.argv[2].lower()=="true",sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6])
	elif sys.argv[1]=="delfav":
		from bookmark import rem
		rem(sys.argv[2],sys.argv[3],sys.argv[4])
	elif sys.argv[1]=="renfav":
		from bookmark import ren
		ren(sys.argv[2],sys.argv[3],sys.argv[4])