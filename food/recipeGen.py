#!/var/lib/openshift/537e1a3c5973cadc06000a62/app-root/data/bin/python
import cgi
import urllib
from Similarity import *
import sys
print """Content-type: text/html\r\n\n"""

form = cgi.FieldStorage()
value = urllib.unquote(form.getvalue('recipe'))
out= [value]
out.extend(get_recipe(value))
print open("recipe.html").read() %tuple(out)
