#!/var/lib/openshift/537e1a3c5973cadc06000a62/app-root/data/bin/python
import cgi
from Similarity import *
import urllib
print """Content-type: text/html\r\n\n"""

form = cgi.FieldStorage()
recipe = urllib.unquote(form.getvalue('recipe')).strip()
rating = form.getvalue('rating')
user="varun"
print saveRating(user,recipe,int(rating))
