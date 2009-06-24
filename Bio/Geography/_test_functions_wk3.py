#!/usr/bin/python
import os
from geogUtils import readshpfile, summarize_shapefile, point_inside_polygon, shapefile_points_in_poly

from geogUtils import access_gbif, get_numhits, get_hits, print_xmltree, get_xml_hits, extract_taxonconceptkeys_tofile, extract_taxonconceptkeys_tolist, get_record, get_all_records_by_increment


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






# ===========================================
# Get the taxon keys returned by search
# ===========================================

params = {'format': 'darwin', 'scientificname': 'Utricularia', 'maxresults' : str(100)}

# This returns 100 hits
xmltree = get_xml_hits(params)

fn = 'temp_taxonkeys'
outfh = open(fn, 'w')

for element in xmltree.getroot():
	extract_taxonconceptkeys_tofile(element, outfh)
outfh.close()
#os.system('more ' + fn)
os.system('head ' + fn)
os.system('tail ' + fn)





# ===========================================
# Download each record individually (slow)
# ===========================================

runthis = 0
if runthis == 1:
	# This is slow (about 1 record/second)
	# Go through the keys and extract the records individually
	
	gbifKeys_fn = fn
	fh = open(gbifKeys_fn, 'r')
	for index, line in enumerate(fh):
		words = line.split()
		key = words[0]
		
		print ''
		print "Record #", index
		print key	
		params = {'format': 'darwin', 'scientificname': 'Utricularia', 'key' : key}
		xmltree = get_record(params)
		
	fh.close()


output_list = []
for element in xmltree.getroot():
	gbifKeys_list = extract_taxonconceptkeys_tolist(element, output_list)

# Get first record
xmltree = get_record(gbifKeys_list[0])




# ===========================================
# Get all records by increment
# ===========================================
params = {'format': 'darwin', 'scientificname': 'Utricularia'}
inc = 400
prefix_fn = 'temp_records'
list_of_tempfiles = get_all_records_by_increment(params, inc, prefix_fn)

print list_of_tempfiles


stop

