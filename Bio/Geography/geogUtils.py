import shpUtils
import dbfUtils
from Bio import Entrez as Entrez
from xml.etree import ElementTree as ET
import unicodedata
from AsciiDammit import asciiDammit
import re, htmlentitydefs


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
# Code from here:
# http://www.ariel.com.au/a/python-point-int-poly.html
#
# NOTE: does not presently deal with the case of polygons that
# cross the international dateline!
#
# determine if a point is inside a given polygon or not
# Polygon is a list of (x,y) pairs.

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
	Get the number of hits that will be returned by a given search
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
	# 
	# Search-replace to fix annoying 
	# non-ASCII characters in search results
	# 
	# inspiration:
	# http://www.amk.ca/python/howto/unicode
	# http://www.peterbe.com/plog/unicode-to-ascii
	#
	fn_fixed = fn_unfixed.replace('unfixed', 'fixed')
	fh = open(fn_unfixed, 'r')
	fh_fixed = open(fn_fixed, 'w')
	for line in fh:
		
		# library from here: http://effbot.org/zone/re-sub.htm#unescape-html
		ascii_content2 = unescape(line)
		
		# inspiration: http://www.amk.ca/python/howto/unicode
		ascii_content = unicodedata.normalize('NFKD', unicode(ascii_content2)).encode('ascii','ignore')
		
		ascii_content = fix_ampersand(ascii_content)
		
		print ascii_content		
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
	Take the text string returned by GBIF and parse to an XML tree using ElementTree.  Requires the intermediate step of saving to a temporary file (required to make ElementTree.parse work, apparently)
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

	

def print_xmltree(xmltree):
	
	for element in xmltree.getroot():
		print element
		print_subelements(element)




def unescape(text):
##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.
# source: http://effbot.org/zone/re-sub.htm#unescape-html
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
	