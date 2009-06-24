#!/usr/bin/python
import os
from geogUtils import readshpfile, summarize_shapefile, point_inside_polygon, shapefile_points_in_poly

print ""
print ""
print "Running _test_shp.py..."
print ""



# =====================================
# Processing shapefiles
# =====================================

print "1. Opening and summarizing shapefiles."

# Get path/name of shapefile
fn = 'placept_shp/placept.shp'

# Get the records
shpRecords = readshpfile(fn)

# now do whatever you want with the resulting data
print "Shapefile name: ", fn
print "Length of shapefile dictionary: ", len(shpRecords)

# print out the first feature in this shapefile
print shpRecords[0]['dbf_data']
for part in shpRecords[0]['shp_data']:
	print part, shpRecords[0]['shp_data'][part]

# get list of coordinates for each feature and print them out
shplist = summarize_shapefile(fn, 'tolist', 'temp.txt')
print shplist

# print coordinates directly to screen
summarize_shapefile(fn, 'toscreen', 'temp.txt')

# print coordinates to file
printfn = summarize_shapefile(fn, 'tofile', 'temp.txt')
os.system('head ' + printfn)






# =====================================
# Point-in-polygon operation
# =====================================

print ""
print "2. Point-in-polygon operation."

# Set up polygon
ul = (-80, 80)
ur = (0, 80)
ll = (-80, 40)
lr = (0, 40)
poly = [ul, ur, ll, lr]

shapefile_points_in_poly(shpRecords, poly)






# =====================================
# Read & parse a GBIF XML file (DarwinCore format)
# =====================================
print ""
print "3. Extracting lat/longs from XML file (DarwinCore format)."

from xml.etree import ElementTree as ET
from geogUtils import print_subelements, extract_latlong
import os

xml_file = 'utric_search_v3.xml'

# Name of file to output lats/longs to
outfilename = 'latlongs.txt'

try:
	xmltree = ET.parse(xml_file)
except Exception, inst:
	print "Unexpected error opening %s: %s" % (xml_file, inst)

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





