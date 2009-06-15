#!/usr/bin/python
import os
from geogUtils import readshpfile, summarize_shapefile, point_inside_polygon, shapefile_points_in_poly

from geogUtils import access_gbif, get_numhits, get_hits, print_xmltree, get_xml_hits


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



xmltree = get_xml_hits(params)

print_xmltree(xmltree)







# =====================================
# Point-in-polygon operation
# =====================================

from geogUtils import print_subelements, extract_latlong
import os

print ""
print "2. Point-in-polygon operation."

# Set up polygon
# (long, lat) = x, y
ul = (14, 58)
ur = (15, 58)
ll = (14, 57)
lr = (15, 57)
poly = [ul, ur, ll, lr]

outfilename = 'latlongs.txt'
outfh = open(outfilename, 'w')
for element in xmltree.getroot():
	extract_latlong(element, outfh)
outfh.close()





# 
os.system('head latlongs.txt')
os.system('tail latlongs.txt')







# =====================================
# Classify GBIF records as to whether or not they fall inside region of interest
# =====================================
print ""
print "4. Do the GBIF records fall inside the region of interest?"

from geogUtils import tablefile_points_in_poly

# Open the lat/longs table
outfh = open(outfilename, 'r')

tablefile_points_in_poly(outfh, 0, 1, 2, poly)

outfh.close()



"""
stop

# Getting the actual hits
xmlfn = get_hits(params)

fh = open(xmlfn, 'r')
for line in fh:
	print line

"""


 