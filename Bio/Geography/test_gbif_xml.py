#!/usr/bin/python
import os
from gbif_xml import GbifXml
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
gbifobj = GbifXml(xmltree)





# ======================
# Testing print_xmltree
# ======================
# Print the object:
#  (also uses gbifobj.print_sublelements)

"""
print ''
print 'Printing the GBIF object xmltree with print_xmltree...'
gbifobj.print_xmltree()
"""




# ======================
# Testing element_items_to_dictionary
# ======================
"""
items = gbifobj.root.items()
items_dict = gbifobj.element_items_to_dictionary(items)
print ''
print 'Printing element_items_to_dictionary(items)...'
print items_dict
"""


# ======================
# Testing extract_latlong
# ======================

outstr = gbifobj.extract_latlongs(gbifobj.root)

print outstr

