#!/var/lib/openshift/537e1a3c5973cadc06000a62/app-root/data/bin/python
import cgi
import subprocess
import os
import sys
import urllib
from Similarity import *
print """Content-type: text/html\r\n\n"""

form = cgi.FieldStorage()
query = urllib.unquote(form.getvalue('q'))
my_env = os.environ.copy()
my_env["CLASSPATH"] ='''.;D:/Apache/cgi-bin/food/lucene-core-5.0-SNAPSHOT.jar;D:/Apache/cgi-bin/food/lucene-analyzers-common-5.0-SNAPSHOT.jar;D:/Apache/cgi-bin/food/lucene-queryparser-5.0-SNAPSHOT.jar;'''
p = subprocess.Popen(["C:/Program Files/Java/jdk1.7.0_55/bin/java.exe","org.apache.lucene.demo.SearchFiles", "-index","D:/Apache/cgi-bin/food/lucene/searchIndex" ,"-query",'"'+query+'"'],env=my_env,stdout=subprocess.PIPE)
out,err = p.communicate()
if err != None:
	print "NO results found !"
else:
	out = out.split("\n")
	if len(out) < 3:
		print "No Results found exception"
		sys.exit(0)
	out = out[2:]
	print open("template.html").read() %(get_search(out),)
