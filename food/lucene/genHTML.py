from Similarity import *
import os
import cPickle
import sys
import re
directory = "./indexHTML/"
if not os.path.exists(directory):
    os.makedirs(directory)

obj = cPickle.load(open("dataset.pkl"))
i =0
for value in obj.recipes:
	try:
		f = open(directory+	value+".html","w")
		out= [value]
		out.extend(get_recipe(value))
		f.write(open("recipe.html").read() %tuple(out))
		f.close()
		i +=1
		print i
	except Exception as e:
		sys.stderr.write(e.__str__())