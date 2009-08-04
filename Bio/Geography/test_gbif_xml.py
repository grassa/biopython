#!/usr/bin/python
import os
from gbif_xml import GbifXml, ObsRecs
from handyfunctions import fix_ASCII_file


#from geogUtils import readshpfile, summarize_shapefile, point_inside_polygon, shapefile_points_in_poly

#from geogUtils import access_gbif, get_numhits, get_hits, print_xmltree, get_xml_hits, extract_taxonconceptkeys_tofile, extract_taxonconceptkeys_tolist, get_record, get_all_records_by_increment


print ""
print ""
print "Running test_gbif_xml..."
print ""



# =====================================
# Read & parse a GBIF XML file (DarwinCore format)
# =====================================

# Example filename
xml_fn = 'utric_search_v2.xml'

print ""
print "Reading a GBIF XML file (DarwinCore format), parsing it, and extracting lat/longs."
print "Example filename is:", xml_fn


print "Converting XML file to pure ASCII (stops crashes later during print-to-screen etc.)..."
xml_fn_new = fix_ASCII_file(xml_fn)




from xml.etree import ElementTree as ET
#from geogUtils import print_subelements, extract_latlong

# Name of file to output lats/longs to
#outfilename = 'latlongs.txt'

try:
	xmltree = ET.parse(xml_fn_new)
except Exception, inst:
	print "Unexpected error opening %s: %s" % (xml_fn, inst)


# Store results in an object of Class GbifXml:
gbif_recs_xmltree = GbifXml(xmltree)



# ======================
# Testing print_xmltree
# ======================
# Print the object:
#  (also uses gbif_recs_xmltree.print_sublelements)

print ''
print 'Printing the GBIF object xmltree with print_xmltree...'
#gbif_recs_xmltree.print_xmltree()



# ======================
# Testing extract_latlongs
# ======================
# Initiate ObsRecs object, containing gbif_recs_xmltree
recs = ObsRecs(gbif_recs_xmltree)

outstr = recs.gbif_recs_xmltree.extract_latlongs(gbif_recs_xmltree.root)
print outstr

# Make recs object hold all of the observation records
recs.latlongs_to_obj()

print ''
print "Printing first five record objects..."
print recs.obs_recs_list[0:4], '...'



# ========================
# Testing get_hits()
# ========================
params = {'format': 'darwin', 'scientificname': 'Utricularia', 'maxresults' : str(100)}

recs.get_xml_hits(params)
recs.gbif_recs_xmltree.print_xmltree()


# ========================
# Testing get_numhits()
# ========================
recs.get_numhits(params)


# ========================
# Testing get_record
# ========================
key = 175067484
xmlrec = recs.get_record(key)
print xmlrec

# ========================
# Testing getting records by increment
# ========================
inc = 400
x = recs.get_all_records_by_increment(params, inc)
print x

# ========================
# ========================


