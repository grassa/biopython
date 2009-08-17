#!/usr/bin/python
import os

print ""
print ""
print "================================================"
print "Read & parse a GBIF XML file (DarwinCore format)"
print "================================================"
print ""


import os
from GbifXml import GbifXmlTree, GbifSearchResults
#from Bio.Geography.GenUtils import fix_ASCII_file
from GenUtils import fix_ASCII_file




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


# Store results in an object of Class GbifXmlTree:
gbif_recs_xmltree = GbifXmlTree(xmltree)



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
# Initiate GbifSearchResults object, containing gbif_recs_xmltree
recs = GbifSearchResults(gbif_recs_xmltree)

outstr = recs.gbif_recs_xmltree.extract_latlongs(gbif_recs_xmltree.root)
print outstr

# Make recs object hold all of the observation records
recs.latlongs_to_obj()

print ''
print "Printing first five record objects..."
print recs.obs_recs_list[0:4], '...'
recs.print_records()





# ========================
# Testing get_numhits()
# ========================
params = {'format': 'darwin', 'scientificname': 'Utricularia'}
recs2 = GbifSearchResults()
recs2.get_numhits(params)



# ========================
# Testing get_record
# ========================
key = 175067484
recs3 = GbifSearchResults()
xmlrec = recs3.get_record(key)
print xmlrec


