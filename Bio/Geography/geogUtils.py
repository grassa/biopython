import shpUtils
import dbfUtils
from Bio import Entrez as Entrez
from xml.etree import ElementTree as ET
import unicodedata
from AsciiDammit import asciiDammit
import re, htmlentitydefs

# These libraries come from the lagrange package:
"""
http://code.google.com/p/lagrange/
Lagrange is a Python package implementing likelihood models for geographic range evolution on phylogenetic trees, with methods for inferring rates of dispersal and local extinction and ancestral ranges.

This software implements methods described in Ree, R H and S A Smith. 2008. Maximum likelihood inference of geographic range evolution by dispersal, local extinction, and cladogenesis. Systematic Biology 57(1):4-14. 

GNU General Public License v2
"""
import lagrange_newick
import lagrange_phylo
import lagrange_tree
import lagrange_ascii

def readshpfile(fn):
	
	# Get the filename
	# fn = shapefilename
	
	# Try to open the file, print error if error	
	try:
		f = open(fn)
	# some code here
	except IOError, reason:
		print "couldn't open file, because of", reason
		return

	# load the shapefile, populating a list of dictionaries
	shpRecords = shpUtils.loadShapefile(fn)
	
	return shpRecords
	

def summarize_shapefile(fn, output_option, outfn):
	shpRecords = readshpfile(fn)
	
	if output_option == 'toscreen':
		print "Feature#	Name	X	Y"
		
		for index, record in enumerate(shpRecords):
			
			# Make an output string
			
			# consecutive ount
			pt1 = str(index+1)
			
			# Feature name
			pt2 = str(record['dbf_data']['NAME'])
			
			# X & Y coords
			pt3 = str(record['shp_data']['x'])
			pt4 = str(record['shp_data']['y'])
	
			printstr = '	'.join([pt1, pt2, pt3, pt4])
			print printstr
		
		return "printed string to screen"
			

	elif output_option == 'tofile':
		outfile = open(outfn, 'w')
		
		header_str = '	'.join(['Feature#', 'Name', 'X', 'Y'])
		outfile.write(header_str)

		
		for index, record in enumerate(shpRecords):
			
			# Make an output string
			
			# consecutive ount
			pt1 = str(index+1)
			
			# Feature name
			pt2 = str(record['dbf_data']['NAME'])
			
			# X & Y coords
			pt3 = str(record['shp_data']['x'])
			pt4 = str(record['shp_data']['y'])
	
			printstr = '	'.join([pt1, pt2, pt3, pt4])
			outfile.write(printstr)
		
		outfile.close()
		return outfn


	elif output_option == 'tolist':
		
		# Create blank list
		outlist = []
		
		# Determine header row
		header_row = ['Feature#', 'Name', 'X', 'Y']
		outlist.append(header_row)
		
		for index, record in enumerate(shpRecords):
			
			# Make an output string
			
			# consecutive ount
			pt1 = str(index+1)
			
			# Feature name
			pt2 = str(record['dbf_data']['NAME'])
			
			# X & Y coords
			pt3 = str(record['shp_data']['x'])
			pt4 = str(record['shp_data']['y'])
	
			line = [pt1, pt2, pt3, pt4]
			outlist.append(line)
		
		return outlist

	return



def point_inside_polygon(x,y,poly):
	"""
	# Code from here:
	# http://www.ariel.com.au/a/python-point-int-poly.html
	#
	# NOTE: does not presently deal with the case of polygons that
	# cross the international dateline!
	#
	# determine if a point is inside a given polygon or not
	#
	# Polygon is a list of (x,y) pairs.
	"""
	n = len(poly)
	inside = False

	p1x,p1y = poly[0]
	for i in range(n+1):
		p2x,p2y = poly[i % n]
		if y > min(p1y,p2y):
			if y <= max(p1y,p2y):
				if x <= max(p1x,p2x):
					if p1y != p2y:
						xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
					if p1x == p2x or x <= xinters:
						inside = not inside
		p1x,p1y = p2x,p2y

	return inside



def shapefile_points_in_poly(pt_records, poly):
	num_inside = 0
	for index,pt in enumerate(pt_records):
		x = pt['shp_data']['x']
		y = pt['shp_data']['y']
		inside = point_inside_polygon(x, y, poly)
		
		if inside == True:
			num_inside = num_inside + 1
		print index +1, inside
	
	print num_inside, " out of ", len(pt_records), " inside specified polygon."
	return



def tablefile_points_in_poly(fh, ycol, xcol, namecol, poly):
	num_inside = 0
	for index,line in enumerate(fh):
		words = line.split()
		
		if len(words) < 3:
			continue
		
		x = float(words[xcol])
		y = float(words[ycol])
		inside = point_inside_polygon(x, y, poly)
		
		if inside == True:
			num_inside = num_inside + 1
		
		if len(words) > 3:
			name = words[namecol] + ' ' + words[namecol+1]
		else:
			name = words[namecol]
		print index +1, name, inside
	
	print num_inside, " out of ", index+1, " inside specified polygon."
	return







def print_subelements(element):
	"""
	Takes an element from an XML tree and prints the subelements tag & text, and
	the within-tag items (key/value or whatnot)
	"""	
	if element.__len__() == 0:
		# Print the text beginning the tag header, and between the tags
		print element.tag, element.text

		# Check for any key/value pairs included in the tag header,
		# and print them if they exist
		if len(element.items()) > 0:
			print "Encoded items: ", element.items()
		return
	elif element.__len__() > 0:
		print element.tag, element.text, "#subelements =", element.__len__()
		if len(element.items()) > 0:
			print "Encoded items: ", element.items()

		for subelement in element.getchildren():
			print_subelements(subelement)
		return


def element_items_to_dictionary(element_items):
	"""
	If the XML tree element has items encoded in the tag, e.g. key/value or whatever,
	this function puts them in a python dictionary and returns them.
	"""	
	for item in element_items:
		temp_dict[item[0][1]] = item[1][1]
	"""
	temp_dict = element_items_to_dictionary(element.keys())
	for key in temp_dict.keys():
		print key, ": ", temp_dict[key]
		# Check if there is more than a key/value pair
		if len(element.keys()) > 2:
			print "There is more than a key/value pair encoded in this element"
			print element.items()
	"""
	return temp_dict


def extract_latlong(element, outfh):
	"""
	Searches an element in an XML tree for lat/long information, and the 
	complete name. Searches recursively, if there are subelements.
	"""
	if element.__len__() == 0:
		return (element.tag, element.text)
	elif element.__len__() > 0:
		#print element.tag, element.text, "#subelements =", element.__len__()
		for subelement in element.getchildren():
			temptuple = extract_latlong(subelement, outfh)
			if temptuple[0].endswith('decimalLatitude'):
				outfh.write(temptuple[1] + '\t')
			elif temptuple[0].endswith('decimalLongitude'):
				outfh.write(temptuple[1] + '\t')
			elif temptuple[0].endswith('nameComplete'):
				#if temptuple[1] != '':
				outfh.write(temptuple[1] + '\n')
		return ('tag: parent subelement', 'text: multiple subelements')





def access_gbif(url, params):
	"""
	# Helper function to access various GBIF services
	# 
	# choose the URL ("url") from here:
	# http://data.gbif.org/ws/rest/occurrence
	#
	# params are a dictionary of key/value pairs
	#
	# "_open" is from Bio.Entrez._open, online here: 
	# http://www.biopython.org/DIST/docs/api/Bio.Entrez-pysrc.html#_open
	#
	# Get the handle of results
	# (looks like e.g.: <addinfourl at 75575128 whose fp = <socket._fileobject object at 0x48117f0>> )
	
	# (open with results_handle.read() )
	"""
	print 'Accessing GBIF with access_gbif...'
	

	results_handle = Entrez._open(url, params)
	return results_handle


def get_hits(params):
	"""
	Get the actual hits that are be returned by a given search
	(this allows parsing & gradual downloading of searches larger 
	than e.g. 1000 records)

	It will return the LAST non-none instance (in a standard search result there
	should be only one, anyway).
	"""
	
	print ''
	print 'Running get_hits(params)...'

	# URL for the count utility
	# instructions: http://data.gbif.org/ws/rest/occurrence
	url = 'http://data.gbif.org/ws/rest/occurrence/list'

	cmd = url + paramsdict_to_string(params)
	results_handle = access_gbif(url, params)
	
	xmlstring = results_handle.read()
	
	# Save to a tempfile
	fn ='tempxml_unfixed.xml'
	fh = open(fn, 'w')
	fh.write(xmlstring)
	fh.close()


	
	"""
	new_fn = fix_ASCII(fn)
	
	#
	"""
	
	print 'XML search results saved in: ', fn
	
	return fn



def get_xml_hits(params):
	"""
	Returns hits like get_hits, but returns a parsed XML tree.
	"""
	
	print ''
	print 'Running get_xml_hits(params)...'

	# URL for the count utility
	# instructions: http://data.gbif.org/ws/rest/occurrence
	url = 'http://data.gbif.org/ws/rest/occurrence/list'

	cmd = url + paramsdict_to_string(params)
	results_handle = access_gbif(url, params)
	
	xmlstring = results_handle.read()
	
	
	# Save to a tempfile
	fn_unfixed ='tempxml_unfixed.xml'
	fh = open(fn_unfixed, 'w')
	fh.write(xmlstring)
	fh.close()

	fn = fix_ASCII(fn_unfixed)

	# make sure the file is findable
	try:
		xmltree = ET.parse(fn)
	except Exception, inst:
		print "Unexpected error opening %s: %s" % (fn, inst)

	print fn
	#xmltree = ET.parse(fn)
	
	#print_xmltree(xmltree)
	
	return xmltree


def fix_ASCII(fn_unfixed):
	"""
	# Search-replace to fix annoying 
	# non-ASCII characters in search results
	# 
	# inspiration:
	# http://www.amk.ca/python/howto/unicode
	# http://www.peterbe.com/plog/unicode-to-ascii
	"""
	fn_fixed = fn_unfixed.replace('unfixed', 'fixed')
	fh = open(fn_unfixed, 'r')
	fh_fixed = open(fn_fixed, 'w')
	for line in fh:
		
		# library from here: http://effbot.org/zone/re-sub.htm#unescape-html
		ascii_content2 = unescape(line)
		
		# inspiration: http://www.amk.ca/python/howto/unicode
		ascii_content = unicodedata.normalize('NFKD', unicode(ascii_content2)).encode('ascii','ignore')
		
		ascii_content = fix_ampersand(ascii_content)
		
		#print ascii_content		
		fh_fixed.write(ascii_content)

	fh_fixed.close()
	fh.close()
	return fn_fixed


def fix_ampersand(line):
	return line.replace('&', '&amp;')


def paramsdict_to_string(params):
	"""
	# Converts the python dictionary of search parameters into a text 
	# string for submission to GBIF
	"""
	temp_outstring_list = []
	for key in params.keys():
		temp_outstring_list.append(key + '=' + params[key])
	outstring = '&'.join(temp_outstring_list)
	return outstring


def extract_taxonconceptkeys_tofile(element, outfh):
	"""
	Searches an element in an XML tree for TaxonOccurrence gbifKeys, and the complete 
	sname. Searches recursively, if there are subelements.  Returns file at outfh.
	"""
	
	#print ''
	#print 'Running extract_taxonoccurrencekeys_tofile(element, outfh)'
	
	if element.__len__() == 0:
		if element.tag.endswith('TaxonOccurrence'):
			#print element.tag, element.text
			for item in element.items():
				if item[0] == 'gbifKey':
					print item[0], item[1]
					outfh.write(item[1] + '\n')
					return item[1]
	elif element.__len__() > 0:
		if element.tag.endswith('TaxonOccurrence'):
			#print element.tag, element.text
			for item in element.items():
				if item[0] == 'gbifKey':
					print item[0], item[1]
					outfh.write(item[1] + '\n')
					return item[1]
		else:
			for subelement in element.getchildren():
				#print_subelements(subelement)
				returned_item = extract_taxonconceptkeys_tofile(subelement, outfh)
		
		return ('Error: no TaxonOccurrence gbifKey found')


def extract_taxonconceptkeys_tolist(element, output_list):
	"""
	Searches an element in an XML tree for TaxonOccurrence gbifKeys, and the complete 
	name. Searches recursively, if there are subelements.  Returns list.
	"""
	
	#print ''
	#print 'Running extract_taxonoccurrencekeys_tolist(element, outfh)'

	# Error trap
	#if output_list == None:
	#	output_list = []
	
	#print len(output_list)
	
	if element.__len__() == 0:
		if element.tag.endswith('TaxonOccurrence'):
			#print element.tag, element.text
			for item in element.items():
				if item[0] == 'gbifKey':
					print item[0], item[1]
					output_list.append(item[1])
					return output_list
	elif element.__len__() > 0:
		if element.tag.endswith('TaxonOccurrence'):
			#print element.tag, element.text
			for item in element.items():
				if item[0] == 'gbifKey':
					print item[0], item[1]
					output_list.append(item[1])
					return output_list
		else:
			for subelement in element.getchildren():
				#print_subelements(subelement)
				templist = extract_taxonconceptkeys_tolist(subelement, output_list)
				
				if templist == None:
					#print "3" 
					pass
				elif len(templist) > 0:
					output_list = templist
					#print "4"
					pass
				else:
					#print "5"
					pass
			return output_list
		
		return ('Error: no TaxonOccurrence output_list returned')



def extract_occurrence_elements(element, output_list):
	"""
	Returns a list of the elements, picking elements by TaxonOccurrence; this should 
	return a list of elements equal to the number of hits.
	"""
	
	print ''
	print 'Running extract_taxonoccurrencekeys_tolist(element, outfh)'
	
	
	if element.__len__() == 0:
		if element.tag.endswith('TaxonOccurrence'):
			output_list.append(element)
			return output_list
	elif element.__len__() > 0:
		if element.tag.endswith('TaxonOccurrence'):
			output_list.append(element)
			return output_list
		else:
			for subelement in element.getchildren():
				#print_subelements(subelement)
				output_list = extract_occurrence_elements(subelement, output_list)
				return output_list
		
		return ('Error: no output_list of XML elements returned')





def get_all_records_by_increment(params, inc, prefix_fn):
	"""
	Download all of the records in stages, store in list of elements.
	Increments of e.g. 100 to not overload server
	"""
	print ''
	print "Running get_all_records_by_increment(params, inc)"
	
	numhits = get_numhits(params)
	print "#hits = ", numhits
	
	#list_of_records_as_elements = []
	
	
	# download them by increment
	
	list_of_chunks = range(0, numhits-1, inc)
	
	outfn_list = []
	for index, startindex in enumerate(list_of_chunks):
	
		if startindex + inc - 1 > numhits:
			print "Downloading records# ", startindex, numhits
		else:
			print "Downloading records# ", startindex, startindex+inc-1
		params['startindex'] = str(startindex)
		params['maxresults'] = str(inc)

		fn = prefix_fn + str(index+1) + '.xml'
		outfn_list.append(fn)
		# URL for the count utility
		# instructions: http://data.gbif.org/ws/rest/occurrence
		url = 'http://data.gbif.org/ws/rest/occurrence/list'
		
		results_handle = access_gbif(url, params)
	
		xmlstring = results_handle.read()
	
		# Save to a tempfile
		fh = open(fn, 'w')
		fh.write(xmlstring)
		fh.close()
		
		results_handle.close()
		
		"""
		xmltree = get_xml_hits(params)
		
		for element in xmltree.getroot():
			output_list = extract_occurrence_elements(element, output_list)
			list_of_records_as_elements.extend(output_list)
		"""
		
	return outfn_list


def get_record(key):
	"""
	Get a single record, return xmltree for it.
	"""
	
	print ''
	print 'Running get_record(params)...'

	# URL for the record utility
	# instructions: http://data.gbif.org/ws/rest/occurrence
	url = 'http://data.gbif.org/ws/rest/occurrence/get'

	params = {'format': 'darwin', 'key' : key}

	cmd = url + paramsdict_to_string(params)
	results_handle = access_gbif(url, params)
	
	#print results_handle.read()
	xmlstring = results_handle.read()
	
	# Save to a tempfile
	fn_unfixed ='tempxml_unfixed2.xml'
	fh = open(fn_unfixed, 'w')
	fh.write(xmlstring)
	fh.close()

	fn = fix_ASCII(fn_unfixed)

	fh = open(fn, 'r')
	xmlstring2 = fh.read()
	fh.close()
	
	print ''
	print 'xmlstring2'
	print xmlstring2
	
	xmltree = xmlstring_to_xmltree(xmlstring2)
	print_xmltree(xmltree)
	
	return xmltree





def get_numhits(params):
	"""
	Get the number of hits that will be returned by a given search
	(this allows parsing & gradual downloading of searches larger 
	than e.g. 1000 records)

	It will return the LAST non-none instance (in a standard search result there
	should be only one, anyway).
	"""
	
	print ''
	print 'Running get_numhits(params)...'

	# URL for the count utility
	# instructions: http://data.gbif.org/ws/rest/occurrence
	url = 'http://data.gbif.org/ws/rest/occurrence/count'

	cmd = url + paramsdict_to_string(params)
	results_handle = access_gbif(url, params)
	
	xmlstring = results_handle.read()
	xmltree = xmlstring_to_xmltree(xmlstring)
	#print_xmltree(xmltree)
	
	
	for element in xmltree.getroot():
		temp_numhits = extract_numhits(element)
		if temp_numhits != None:
			numhits = temp_numhits
	
	print "numhits = ", numhits
	return numhits






def extract_numhits(element):
	"""
	# Search an element of a parsed XML string and find the 
	# number of hits, if it exists.  Recursively searches, 
	# if there are subelements.
	# 
	"""
	# print "Running extract_numhits(element)..."
	if element.__len__() == 0:
		if len(element.items()) > 0:
			for item in element.items():
				for index, tupleitem in enumerate(item):
					if tupleitem == 'totalMatched':
						#print item
						#print int(item[index+1])
						return int(item[index+1])
					else:
						temp_return_item = None
	elif element.__len__() > 0:
		#print element.tag, element.text, "#subelements =", element.__len__()
		for subelement in element.getchildren():
			temp_return_item = extract_numhits(subelement)
		if temp_return_item != None:
			return_item = temp_return_item
			return return_item
		else:
			return return_item
			


	

def xmlstring_to_xmltree(xmlstring):
	"""
	Take the text string returned by GBIF and parse to an XML tree using ElementTree.  
	Requires the intermediate step of saving to a temporary file (required to make
	ElementTree.parse work, apparently)
	"""
	tempfn = 'tempxml.xml'
	fh = open(tempfn, 'w')
	fh.write(xmlstring)
	fh.close()
	
	# instructions for ElementTree:
	# http://docs.python.org/library/xml.etree.elementtree.html

	# make sure the file is findable
	try:
		xmltree = ET.parse(tempfn)
	except Exception, inst:
		print "Unexpected error opening %s: %s" % (tempfn, inst)

	# make sure the file is parsable
	try:
		xmltree.getroot()
	except Exception, inst:
		print "Unexpected error running getroot() on text in file %s: %s" % (tempfn, inst)

	return xmltree



def element_items_to_string(items):
	"""
	Input a list of items, get string back
	"""
	s = ""
	for item in items:
		s = s + " " + str(item)
		s = s.strip()
	
	return s

def element_text_to_string(txt):
	if txt == None:
		txt = ""
	return str(txt).strip()



def get_str_subset(start, end, seq):
	
	index1 = start-1
	index2 = end
	
	newstring = str()
	
	for i in range(index1, index2):
		newstring = newstring + seq[i]
	
	#print 'len(newstring)=', str(len(newstring))
	#print 'start - stop', str(end - start + 1) 
	
	return newstring



def find_to_elements_w_ancs(xmltree, el_tag, anc_el_tag):
	"""
	Burrow into XML to get an element with tag el_tag, return only those el_tags underneath a particular parent element parent_el_tag
	"""
	
	match_el_list = []

	for element in xmltree.getroot():
		
		match_el_list = xml_recursive_search_w_anc(xmltree, element, el_tag, anc_el_tag, match_el_list)
	
	
	# How many different ancs found?
	list_ancs = []
	for tupitem in match_el_list:
		list_ancs.append(tupitem[0])
	
	unique_ancs = unique(list_ancs)
	print unique_ancs
	
	print ""
	print "Number of elements found: " + str(len(list_ancs)) + " in " + str(len(unique_ancs)) + " XML 'ancestor' (higher group) categories."
	
	for unique_anc in unique_ancs:
		print ""
		print "Anc: " + str(unique_anc)
		for tupitem in match_el_list:
			if tupitem[0] == unique_anc:
				print "	el: " + str(tupitem[1])
	
	return match_el_list



def create_sub_xmltree(element):
	"""
	Create a subset xmltree (to avoid going back to irrelevant parents)
	"""
	
	xmltree = ET.ElementTree(element)
	
	return xmltree




def xml_recursive_search_w_anc(xmltree, element, el_tag, anc_el_tag, match_el_list):
	"""
	Recursively burrows down to find whatever elements with el_tag exist inside a parent_el_tag.
	"""
	
	
	# If the element matches the tag you are looking for...
	if element.tag == el_tag:

		# Then check if the ancestor matches
		found_anc = None
		ancestor = xml_burrow_up(xmltree, element, anc_el_tag, found_anc)
		
		if ancestor == None:
			pass
		else:
			if ancestor.tag == anc_el_tag:
				match_el = element
				match_el_list.append((ancestor, match_el))

	else:
		for child in element.getchildren():
			match_el_list = xml_recursive_search_w_anc(xmltree, child, el_tag, anc_el_tag, match_el_list)
			
	return match_el_list
		
		

def xml_burrow_up(xmltree, element, anc_el_tag, found_anc):
	"""
	Burrow up xml to find anc_el_tag
	"""
	
	if found_anc == None:
		# Just get the direct parent of child_to_search_for
		child_to_search_for = element
		parent_element = return_parent_in_xmltree(xmltree, child_to_search_for)
		
		if parent_element == None:
			return found_anc
		
		# Does the parent match the searched-for ancestor?		
		if parent_element.tag == anc_el_tag:
			found_anc = parent_element
		else:
			# Move a level up and search again, return if found

			found_anc = xml_burrow_up(xmltree, parent_element, anc_el_tag, found_anc)

		return found_anc
		
	else:
		return found_anc
		


def xml_burrow_up_cousin(xmltree, element, cousin_el_tag, found_cousin):
	"""
	Burrow up from element of interest, until a cousin is found with cousin_el_tag
	"""
	
	if found_cousin == None:
		# Just get the direct parent of child_to_search_for
		child_to_search_for = element
		parent_element = return_parent_in_xmltree(xmltree, child_to_search_for)
		
		if parent_element == None:
			return found_cousin
		
		grandparent_element = return_parent_in_xmltree(xmltree, parent_element)
		if grandparent_element == None:
			return found_cousin
		
		# Does the parent or any cousins match the searched-for ancestor?		
		for aunt in grandparent_element.getchildren():
			if aunt.tag == cousin_el_tag:
				found_cousin = aunt
				return found_cousin
		
		if found_cousin == None:
			# Move a level up and search again, return if found
			found_cousin = xml_burrow_up_cousin(xmltree, parent_element, cousin_el_tag, found_cousin)

		return found_cousin
		
	else:
		return found_cousin
	


def return_parent_in_xmltree(xmltree, child_to_search_for):
	"""
	Search through an xmltree to get the parent of child_to_search_for
	"""
	
	returned_parent = None
	for element in xmltree.getroot():
		
		potential_parent = element
		
		returned_parent = return_parent_in_element(potential_parent, child_to_search_for, returned_parent)
		
		return returned_parent
		
				
	
def return_parent_in_element(potential_parent, child_to_search_for, returned_parent):
	"""
	Search through an XML element to return parent of child_to_search_for
	"""
	
	if returned_parent == None:
		children = potential_parent.getchildren()
		if len(children) > 0:
			for child in potential_parent.getchildren():
				if child == child_to_search_for:
					returned_parent = potential_parent
	
				# If not found at this level, go down a level
				else:
					returned_parent = return_parent_in_element(child, child_to_search_for, returned_parent)
						
		return returned_parent
	else:
		return returned_parent
		

def find_1st_matching_element(element, el_tag, return_element):
	"""
	Burrow down into the XML tree, retrieve the first element with the matching tag
	"""
	if return_element == None:
		if element.tag == el_tag:
			return_element = element
		else:
			children = element.getchildren()
			if len(children) > 0:
				for child in children:
					return_element = find_1st_matching_element(child, el_tag, return_element)
		return return_element	
	else:
		return return_element
	





def print_xmltree(xmltree):
	"""
	Prints all the elements & subelements of the xmltree to screen (may require 
	fix_ASCII to input file to succeed)
	"""
	for element in xmltree.getroot():
		print element
		print_subelements(element)


def read_ultrametric_Newick(newickstr):
	"""
	Read a Newick file into a tree object (a series of node objects links to parent and daughter nodes), also reading node ages and node labels if any. 
	"""
	phylo_obj = lagrange_newick.parse(newickstr)
	return phylo_obj


def list_leaves(phylo_obj):
	"""
	Print out all of the leaves in above a node object
	"""
	for leaf in phylo_obj.leaves():
		print leaf.label
	return len(phylo_obj.leaves())


def treelength(node):
	"""
	Gets the total branchlength above a given node by recursively adding through tree.
	"""
	PD = 0
	PD = addup_PD(node, PD)
	
	return PD
	

def phylodistance(node1, node2):
	"""
	Get the phylogenetic distance (branch length) between two nodes.
	"""
	
	anc_list = []
	anc_list1 = get_ancestors_list(node1, anc_list)

	anc_list = []
	anc_list2 = get_ancestors_list(node2, anc_list)
	
	mrca = find_1st_match(anc_list1, anc_list2)
	
	print ""
	print "Most recent common ancestor of ", node1, node2, " is:", mrca


	print ""
	print "PD between ", node1, "and", node2, " is:"
	
	PD = 0
	PD1 = get_PD_to_mrca(node1, mrca, PD)
	print PD1

	PD = 0
	PD2 = get_PD_to_mrca(node2, mrca, PD)
	print PD2
	
	PD = PD1 + PD2
	#print "Total =", PD
	return PD


def get_distance_matrix(phylo_obj):
	"""
	Get a matrix of all of the pairwise distances between the tips of a tree. 
	"""
	
	# Get the array of mrcas between leaves
	mrca_array = get_mrca_array(phylo_obj)
	
	leaves = phylo_obj.leaves()
	
	# Get the PD between leaves for each pair
	nleaves = len(leaves)
	dist_array = make_None_list_array(nleaves, nleaves)
	
	for index1 in range(0, nleaves):
		temp_array = [None] * nleaves
		for index2 in range(index1, nleaves):
			mrca = mrca_array[index1][index2]
			if mrca == None:
				continue
			else:
				PD = 0
				PD1 = get_PD_to_mrca(leaves[index1], mrca, PD)
				PD2 = get_PD_to_mrca(leaves[index2], mrca, PD)
				PD = PD1 + PD2
				#print "Total =", PD
				
				temp_array[index2] = PD
		dist_array[index1] = temp_array

	return dist_array


def get_mrca_array(phylo_obj):
	"""
	Get a square list of lists (array) listing the mrca of each pair of leaves
	(half-diagonal matrix)
	"""
	
	nleaves = len(phylo_obj.leaves())
	
	# Create empty array
	mrca_array = make_None_list_array(nleaves, nleaves)
	#print mrca_array


	# Get the ancestor lists for each leaf
	list_anc_lists = []
	for leaf in phylo_obj.leaves():
		anc_list = []
		anc_list = get_ancestors_list(leaf, anc_list)
		list_anc_lists.append(anc_list)

	
	# Get the common ancestor node for each leaf pair
	for index1 in range(0, nleaves):
		temp_array = [None] * nleaves
		for index2 in range(index1, nleaves):
			#print index1, index2
			#x=find_1st_match(list_anc_lists[index1], list_anc_lists[index2])
			#print x
			temp_array[index2] = find_1st_match(list_anc_lists[index1], 			list_anc_lists[index2])
		mrca_array[index1] = temp_array
	return mrca_array



def subset_tree(phylo_obj, list_to_keep):
	"""
	Given a list of tips and a tree, remove all other tips and resulting redundant nodes to produce a new smaller tree.
	"""
	
	result = phylo_obj.subtree_mapping(list_to_keep)
	temproot = result['newroot']
	
	temproot2 = prune_single_desc_nodes(temproot)
	
	newroot = find_new_root(temproot2)
	
	
	return newroot
	


def prune_single_desc_nodes(node):
	"""
	Follow a tree from the bottom up, pruning any nodes with only one descendent
	"""
	if node.nchildren == 1:
		child = node.children[0]
		grandchildren = child.children
		if child.nchildren == 0:
			print "This shouldn't happen"
			pass
		elif child.nchildren > 0:
			node.children = child.children
			node.nchildren = len(node.children)
			node.data = child.data.update(node.data)
			node.istip = child.istip
			node.label = str(node.label) + ';' + str(child.label)
			node.length = node.length + child.length
			node.excluded_dists = node.excluded_dists.extend(child.excluded_dists)
			
			for grandchild in grandchildren:
				grandchild.parent = node
				prune_single_desc_nodes(grandchild)
				
	elif node.nchildren > 1:
		for child in node.children:
			prune_single_desc_nodes(child)
	else:
		# No children, node tip
		pass
	
	return node
	

def find_new_root(node):
	"""
	Search up tree from root and make new root at first divergence
	"""
	if node.nchildren == 1:
		root_node = node.children[0]
		newroot = find_new_root(root_node)
		return newroot
	elif node.nchildren > 1:
		node.isroot = True
		return node
	else:
		return None

def make_None_list_array(xdim, ydim):
	"""
	Make a list of lists ("array") with the specified dimensions
	"""
	
	# Create empty array
	temp_row_array = [None] * xdim
	temp_cols_array = []
	for i in range(0, ydim):
		temp_cols_array.append(temp_row_array)
	
	return temp_cols_array
	
	
	

def get_PD_to_mrca(node, mrca, PD):
	"""
	Add up the phylogenetic distance from a node to the specified ancestor (mrca).  Find mrca with find_1st_match.
	"""
	
	PD = node.length + PD 
	if node.parent == mrca:
		return PD
	else:
		PD = get_PD_to_mrca(node.parent, mrca, PD)
		return PD


def find_1st_match(list1, list2):
	"""
	Find the first match in two ordered lists.
	"""
	anc_list1 = list1
	anc_list2 = list2
	
	for anc1 in anc_list1:
		for anc2 in anc_list2:
			if anc1==anc2:
				return(anc1)
	
	return None
	

def get_ancestors_list(node, anc_list):
	"""
	Get the list of ancestors of a given node
	"""
	if node.parent is not None:
		anc_list.append(node.parent)
		get_ancestors_list(node.parent, anc_list)
	
	return anc_list
	


def addup_PD(node, PD):
	"""
	Adds the branchlength of the current node to the total PD measure.
	"""
	PD = PD + node.length
	#print "PD =", str(PD)
	
	if node.nchildren > 0:
		for child in node.children:
			PD = addup_PD(child, PD)
	
	return(PD)
	
	
def print_tree_outline_format(phylo_obj):
	"""
	Prints the tree out in "outline" format (daughter clades are indented, etc.)
	"""
	
	print ""
	print "Printing out tree of", str(len(phylo_obj.leaves())), "taxa, hierarchical indented format."
	print ""
	
	node = phylo_obj
	rank = 1
	print_Node(node, rank)
	
	return



def print_Node(node, rank):
	"""
	Prints the node in question, and recursively all daughter nodes, maintaining rank as it goes.
	"""
	
	tabstr = ""
	for count in range(1,rank):
		tabstr = tabstr + "	"
	
	printstr = ''.join(["Rank #", str(rank), ", label=", str(node.label), ", brlen=", str(node.length)])
	
	printstr2 = tabstr + printstr
	
	print printstr2
	
	if node.nchildren > 0:
		rank = rank + 1
		for child in node.children:
			print_Node(child, rank)



def lagrange_disclaimer():
	"""
	Just prints lagrange citation etc. in code using lagrange libraries.
	"""
	txt = """Note: This code uses libraries from the lagrange package:
	
	http://code.google.com/p/lagrange/"
	
	Lagrange is a Python package implementing likelihood models for geographic range evolution on phylogenetic trees, with methods for inferring rates of dispersal and local extinction and ancestral ranges.
	
	This software implements methods described in Ree, R H and S A Smith. 2008. Maximum likelihood inference of geographic range evolution by dispersal, local extinction, and cladogenesis. Systematic Biology 57(1):4-14.
	
	GNU General Public License v2
	"""
	
	print txt
	return


def unescape(text):
	"""
	##
	# Removes HTML or XML character references and entities from a text string.
	#
	# @param text The HTML (or XML) source text.
	# @return The plain text, as a Unicode string, if necessary.
	# source: http://effbot.org/zone/re-sub.htm#unescape-html
	"""
	def fixup(m):
		text = m.group(0)
		if text[:2] == "&#":
			# character reference
			try:
				if text[:3] == "&#x":
					return unichr(int(text[3:-1], 16))
				else:
					return unichr(int(text[2:-1]))
			except ValueError:
				pass
		else:
			# named entity
			try:
				text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
			except KeyError:
				pass
		return text # leave as is
	return re.sub("&#?\w+;", fixup, text)
	