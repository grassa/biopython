#!/usr/bin/python
import os
from geogUtils import readshpfile, summarize_shapefile, point_inside_polygon, shapefile_points_in_poly

from geogUtils import access_gbif, get_numhits, get_hits, print_xmltree


print ""
print ""
print "Running _test_functions_wk2.py..."
print ""



# =====================================
# Accessing GBIF
# =====================================
# Inspired by:
# http://www.biopython.org/DIST/docs/api/Bio.Entrez-pysrc.html#efetch


import urllib, time, warnings 
import os.path 
from Bio import File 

email = None 



# Getting a count of the number of hits
params = {'format': 'darwin', 'scientificname': 'Utricularia', 'maxresults' : str(100)}
numhits = get_numhits(params)
print numhits

# Getting the actual hits
xmlfn = get_hits(params)

fh = open(xmlfn, 'r')
for line in fh:
	print line



 