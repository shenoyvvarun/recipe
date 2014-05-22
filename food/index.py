#!/var/lib/openshift/537e1a3c5973cadc06000a62/app-root/data/bin/python
import cgi
import urllib
from Similarity import *

r = recommend_recipes("varun",5)
out = []
for x in r:
	out.append(x[0])
	out.append(x[1])
out.extend([x[0] for x in r])
print """Content-type: text/html\r\n\n"""
print open("i.html").read() %tuple(out)
