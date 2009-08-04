"""
Functions for accessing GBIF, downloading records, processing them into a class, and extracting information from the xmltree in that class.
"""

# Attempting a class
#
# Import using:
# import gbif_xml
# g = gbif_xml.GbifXml(xmltree)
# g.print_xmltree()

# Based on here:
# http://docs.python.org/tutorial/classes.html



from xml.etree import ElementTree as ET

# Used generally
import handyfunctions

# Used by classification utility
import shpUtils
import dbfUtils


# Used by fix_ASCII
# Used by unescape
import unicodedata
import re, htmlentitydefs
# Public domain module to convert diverse characters to ASCII (dammit!)
# http://newsbruiser.tigris.org/source/browse/~checkout~/newsbruiser/nb/lib/AsciiDammit.py
from AsciiDammit import asciiDammit



# Used by self._open
import urllib, time, warnings
import os.path
from Bio import File



class ObsRec(Exception): pass

class ObsRec():
	"""ObsRec is a class for holding an individual observation at an individual lat/long point."""
	
	# Info prints out the informative description of this class, if a user wants to see it.
	#info = "Information about this class: ObsRec is a class for holding an individual observation at an individual lat/long point."
	
	
	def __init__(self):
		"""
		This is an instantiation class for setting up new objects of this class.
		"""
		
		self.lat = None
		self.long = None
		self.taxon = None
		self.genus = None
		self.species = None
		
		self.key = None
		self.date = None
		
	
	def latlong_to_obj(self, line):
		"""
		Read in a string, read species/lat/long to ObsRec object
		# This can be slow, e.g. 10 seconds for even just ~1000 records.
		"""
		print line
		words = line.split("\t")
		numwords = len(words)
		self.key = int(words[0])
		self.lat = float(words[1])
		self.long = float(words[2])
		self.taxon = str(words[3])
		self.date = str(words[4])
		
		temptaxon_words = self.taxon.split()
		if len(temptaxon_words) == 2:
			self.genus = str(temptaxon_words[0])
			self.species = str(temptaxon_words[1])
		if len(temptaxon_words) == 1:
			self.genus = self.taxon

		
		return







class XmlString(Exception): pass

class XmlString(str):
	"""XmlString is a class for holding the xmlstring returned by a GBIF search, & processing it to plain text, then an xmltree (an ElementTree).
	
	XmlString inherits string methods from str (class String).
	"""
	
	# Info prints out the informative description of this class, if a user wants to see it.
	info = "Information about this class: XmlString is a class for holding the xmlstring returned by a GBIF search, & processing it to plain text, then an xmltree (an ElementTree)."
	

	def __init__(self, rawstring=None):
		"""
		This is an instantiation class for setting up new objects of this class.
		"""
		
		if rawstring:
			self.plainstring = rawstring
		else:
			self.plainstring = None
		


	def fix_ASCII_lines(self, endline=''):
		"""
		Convert each line in an input string into pure ASCII
		(This avoids crashes when printing to screen, etc.)
		"""
		# Split the plain string into a list of lines
		lines = self.splitlines()
		
		newstr_list = []
		for line in lines:
			ascii_content = self._fix_ASCII_line(line)
			newstr_list.append(ascii_content + endline)
	
		# Returns a plain string (with linebreaks specified by endline)
		return ''.join(newstr_list)

	
	def _fix_ASCII_line(self, line):
		"""
		Convert a single string line into pure ASCII
		(This avoids crashes when printing to screen, etc.)
		"""
		# library from here: http://effbot.org/zone/re-sub.htm#unescape-html
		ascii_content1 = self._unescape(line)
		
		# Public domain module to convert diverse characters to ASCII
		# http://newsbruiser.tigris.org/source/browse/~checkout~/newsbruiser/nb/lib/AsciiDammit.py
		ascii_content2 = asciiDammit(ascii_content1)
		
		# inspiration: http://www.amk.ca/python/howto/unicode
		ascii_content3 = unicodedata.normalize('NFKC', unicode(ascii_content2)).encode('ascii','ignore')
		
		# Fix the ampersand
		ascii_content = self._fix_ampersand(ascii_content3)
		return ascii_content
		

	def _unescape(self, text):
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
		
	
	def _fix_ampersand(self, line):
		"""
		Replaces "&" with "&amp;" in a string; this is otherwise 
		not caught by the unescape and unicodedata.normalize functions.
		"""
		return line.replace('&', '&amp;')
	
	
	

class GbifXmlError(Exception): pass

class GbifXml():
	"""gbifxml is a class for holding and processing xmltrees of GBIF records."""
	
	# Info prints out the informative description of this class, if a user wants to see it.
	info = "Information about this class: gbifxml is a class for holding and processing xmltrees of GBIF records."

	# Used in _open function to determine 3 second waiting time for server access
	

	def __init__(self, xmltree=None):
		"""
		This is an instantiation class for setting up new objects of this class.
		"""
		
		self.data = []
		
		if xmltree:
			self.xmltree = xmltree
			self.root = xmltree.getroot()
		else:
			print "GbifXml.__init__(): No xmltree, so creating empty object."
			self.xmltree = None
			self.root = None
	
		
	def hello(self):
		return 'hello world'
	
	
	
	def print_xmltree(self):
		"""
		Prints all the elements & subelements of the xmltree to screen (may require 
		fix_ASCII to input file to succeed)
		"""
		xmltree = self.xmltree
		
		for element in xmltree.getroot():
			print element
			self.print_subelements(element)
			
	def print_subelements(self, element):
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
				self.print_subelements(subelement)
			return
	
	def _element_items_to_dictionary(self, element_items):
		"""
		If the XML tree element has items encoded in the tag, e.g. key/value or
		whatever, this function puts them in a python dictionary and returns 
		them.
		"""
		
		if len(element_items) < 2:
			print "_element_items_to_dictionary error: < 2 items in element"
			return None
		else:
			temp_dict = {}
			for item in element_items:
				temp_dict[item[0][1]] = item[1][1]
			return temp_dict

		"""
		temp_dict = _element_items_to_dictionary(element.keys())
		for key in temp_dict.keys():
			print key, ": ", temp_dict[key]
			# Check if there is more than a key/value pair
			if len(element.keys()) > 2:
				print "There is more than a key/value pair encoded in this element"
				print element.items()
		"""
	
	
	def extract_latlongs(self, element):
		"""
		Create a temporary pseudofile, extract lat longs to it, 
		return results as string.
		
		Inspired by: http://www.skymind.com/~ocrow/python_string/
		(Method 5: Write to a pseudo file)
		"""
		from cStringIO import StringIO
		file_str = StringIO()
		self._extract_latlong_datum(element, file_str)
		return file_str.getvalue()



	def _extract_latlong_datum(self, element, file_str):
		"""
		Searches an element in an XML tree for lat/long information, and the 
		complete name. Searches recursively, if there are subelements.
		
		file_str is a string created by StringIO in extract_latlongs() (i.e., a temp filestr)
		"""
		if element.__len__() == 0:
			return (element.tag, element.text)
		elif element.__len__() > 0:
			#print element.tag, element.text, "#subelements =", element.__len__()
			for subelement in element.getchildren():
				# Get the TaxonOccurrence
				if subelement.tag.endswith('TaxonOccurrence'):
					for item in subelement.items():
						if item[0] == 'gbifKey':
							#print item[0], item[1]
							file_str.write(item[1] + '\t')
				
				# Get the lat/long/name
				temptuple = self._extract_latlong_datum(subelement, file_str)
				if temptuple[0].endswith('decimalLatitude'):
					file_str.write(temptuple[1] + '\t')
				elif temptuple[0].endswith('decimalLongitude'):
					file_str.write(temptuple[1] + '\t')
				elif temptuple[0].endswith('taxonName'):
					#if temptuple[1] != '':
					file_str.write(temptuple[1] + '\t')
				elif temptuple[0].endswith('latestDateCollected'):
					#if temptuple[1] != '':
					file_str.write(str(temptuple[1]) + '\n')
			return ('tag: parent subelement', 'text: multiple subelements')
			

	
	
	def _extract_occurrence_elements(self, element, output_list):
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
					output_list = self._extract_occurrence_elements(subelement, output_list)
					return output_list
			
			return ('Error: no output_list of XML elements returned')
	


	
	
	
	def find_to_elements_w_ancs(self, el_tag, anc_el_tag):
		"""
		Burrow into XML to get an element with tag el_tag, return only those el_tags underneath a particular parent element parent_el_tag
		"""
		xmltree = self.xmltree
		
		match_el_list = []
	
		for element in xmltree.getroot():
			
			match_el_list = self.xml_recursive_search_w_anc(element, el_tag, anc_el_tag, match_el_list)
		
		
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
	
	
	
	
	def xml_recursive_search_w_anc(self, element, el_tag, anc_el_tag, match_el_list):
		"""
		Recursively burrows down to find whatever elements with el_tag exist inside a parent_el_tag.
		"""
		xmltree = self.xmltree
		
		# If the element matches the tag you are looking for...
		if element.tag == el_tag:
	
			# Then check if the ancestor matches
			found_anc = None
			ancestor = self._xml_burrow_up(element, anc_el_tag, found_anc)
			
			if ancestor == None:
				pass
			else:
				if ancestor.tag == anc_el_tag:
					match_el = element
					match_el_list.append((ancestor, match_el))
	
		else:
			for child in element.getchildren():
				match_el_list = self.xml_recursive_search_w_anc(child, el_tag, anc_el_tag, match_el_list)
				
		return match_el_list
			

	def create_sub_xmltree(self, element):
		"""
		Create a subset xmltree (to avoid going back to irrelevant parents)
		"""
		
		xmltree = ET.ElementTree(element)
		
		return xmltree
	
	
			
	
	def _xml_burrow_up(self, element, anc_el_tag, found_anc):
		"""
		Burrow up xml to find anc_el_tag
		"""
		xmltree = self.xmltree
		
		if found_anc == None:
			# Just get the direct parent of child_to_search_for
			child_to_search_for = element
			parent_element = self._return_parent_in_xmltree(child_to_search_for)
			
			if parent_element == None:
				return found_anc
			
			# Does the parent match the searched-for ancestor?		
			if parent_element.tag == anc_el_tag:
				found_anc = parent_element
			else:
				# Move a level up and search again, return if found
	
				found_anc = self._xml_burrow_up(parent_element, anc_el_tag, found_anc)
	
			return found_anc
			
		else:
			return found_anc
			
		
	
	def _xml_burrow_up_cousin(element, cousin_el_tag, found_cousin):
		"""
		Burrow up from element of interest, until a cousin is found with cousin_el_tag
		"""
		xmltree = self.xmltree
		
		if found_cousin == None:
			# Just get the direct parent of child_to_search_for
			child_to_search_for = element
			parent_element = self._return_parent_in_xmltree(xmltree, child_to_search_for)
			
			if parent_element == None:
				return found_cousin
			
			grandparent_element = self._return_parent_in_xmltree(parent_element)
			if grandparent_element == None:
				return found_cousin
			
			# Does the parent or any cousins match the searched-for ancestor?		
			for aunt in grandparent_element.getchildren():
				if aunt.tag == cousin_el_tag:
					found_cousin = aunt
					return found_cousin
			
			if found_cousin == None:
				# Move a level up and search again, return if found
				found_cousin = self._xml_burrow_up_cousin(parent_element, cousin_el_tag, found_cousin)
	
			return found_cousin
			
		else:
			return found_cousin
		
	
	
	def _return_parent_in_xmltree(self, child_to_search_for):
		"""
		Search through an xmltree to get the parent of child_to_search_for
		"""
		xmltree = self.xmltree
		
		returned_parent = None
		for element in xmltree.getroot():
			
			potential_parent = element
			
			returned_parent = self._return_parent_in_element(potential_parent, child_to_search_for, returned_parent)
			
			return returned_parent
			
					
		
	def _return_parent_in_element(self, potential_parent, child_to_search_for, returned_parent):
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
						returned_parent = self._return_parent_in_element(child, child_to_search_for, returned_parent)
							
			return returned_parent
		else:
			return returned_parent
			
	
	def find_1st_matching_element(self, element, el_tag, return_element):
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
						return_element = self.find_1st_matching_element(child, el_tag, return_element)
			return return_element	
		else:
			return return_element
		
	

	
	def extract_numhits(self, element):
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
				temp_return_item = self.extract_numhits(subelement)
			if temp_return_item != None:
				return_item = temp_return_item
				return return_item
			else:
				return return_item
				
	

	
		
	
	
	












	
class ObsRecs(Exception): pass

class ObsRecs():	
	"""
	ObsRecs is a class for holding a series of ObsRec records, and processing them
	e.g. into classified areas.
	"""
	
	# Info prints out the informative description of this class, if a user wants to see it.
	info = "ObsRecs is a class for holding a series of ObsRec records, and processing them	e.g. into classified areas."
	
	
	def __init__(self, gbif_recs_xmltree=None):
		"""
		This is an instantiation class for setting up new objects of this class.
		"""

		# These are used by the _open function, e.g. to set wait times for 
		# accessing GBIF
		self.time_last_gbif_access = 0
		self.email = None

		# xmltree of GBIF records (GbifXml class)	
		if gbif_recs_xmltree:
			self.gbif_recs_xmltree = gbif_recs_xmltree
		else:
			self.gbif_recs_xmltree = GbifXml()
		
		
		# xmltree of GBIF count query
		self.gbif_count_xmltree = None
		
		# String (tempfile-ish) list of records
		# An XmlString object, with methods for cleaning the string
		self.obs_recs_xmlstring = None
		self.count_recs_xmlstring = None
		
		# Summary statistics for search
		self.gbif_hits_count = None
		self.gbif_count_params = None
		self.count_params_str = None
		
		# List of ObsRec objects
		self.obs_recs_list = []


	def latlongs_to_obj(self):
		"""
		Takes the string from extract_latlongs, puts each line into a
		ObsRec object.
		
		Return a list of the objects
		"""
		
		if self.obs_recs_xmlstring == None:
			# If there is no string of records yet, extract the string,
			# using the gbif_recs_xmltree root (getroot from xmltree) as the input
			# element
			print "Filling in self.obs_recs_xmlstring"
			self.obs_recs_xmlstring = self.gbif_recs_xmltree.extract_latlongs(self.gbif_recs_xmltree.root)
			#print type(self.obs_recs_xmlstring)
			# Print the header
			for index, line in enumerate(self.obs_recs_xmlstring.splitlines()):
				print "Line" + str(index) + ": " + line
				if index > 4:
					print '...'
					break
		
		for line in self.obs_recs_xmlstring.splitlines():
			temprec = ObsRec()
			temprec.latlong_to_obj(line)
			self.obs_recs_list.append(temprec)
			#del temprec
		
		return
	

	# Functions devoted to accessing/downloading GBIF records
		
	def access_gbif(self, url, params):
		"""
		# Helper function to access various GBIF services
		# 
		# choose the URL ("url") from here:
		# http://data.gbif.org/ws/rest/occurrence
		#
		# params are a dictionary of key/value pairs
		#
		# "self._open" is from Bio.Entrez.self._open, online here: 
		# http://www.biopython.org/DIST/docs/api/Bio.Entrez-pysrc.html#self._open
		#
		# Get the handle of results
		# (looks like e.g.: <addinfourl at 75575128 whose fp = <socket._fileobject object at 0x48117f0>> )
		
		# (open with results_handle.read() )
		"""
		print 'Accessing GBIF with access_gbif...'
		
	
		results_handle = self._open(url, params)
		return results_handle
	
	
	def _get_hits(self, params):
		"""
		Get the actual hits that are be returned by a given search
		(this allows parsing & gradual downloading of searches larger 
		than e.g. 1000 records)
	
		It will return the LAST non-none instance (in a standard search result there
		should be only one, anyway).
		"""
		print '  Running _get_hits(params)...'
	
		# instructions: http://data.gbif.org/ws/rest/occurrence
		url = 'http://data.gbif.org/ws/rest/occurrence/list'
	
		cmd = url + self._paramsdict_to_string(params)
		results_handle = self.access_gbif(url, params)
		
		self.obs_recs_xmlstring = XmlString(results_handle.read())
				
		print 'XML search results stored via: "self.obs_recs_xmlstring = XmlString(results_handle.read())"'
		
		return self.obs_recs_xmlstring

	
	def get_xml_hits(self, params):
		"""
		Returns hits like _get_hits, but returns a parsed XML tree.
		"""
		
		print ''
		print 'Running get_xml_hits(params)...'
	
		# Returns XmlString object
		# (stored in self.obs_recs_xmlstring)
		self._get_hits(params)
		
		# Fix the xmlstring:
		# returns a plain string
		plain_xmlstring_fixed = self.obs_recs_xmlstring.fix_ASCII_lines('\n')
		#temp_xmlstring.splitlines() works because XmlString inherits from string class
		
		# Store the plain string in an XmlString object, store as method of
		# GbifXml object
		self.obs_recs_xmlstring = XmlString(plain_xmlstring_fixed)
				
		# make sure the self.obs_recs_xmlstring (an XmlString object) parses into an ElementTree
		try:
			self.xmltree = ET.ElementTree(ET.fromstring(self.obs_recs_xmlstring))
			print_it = 0
			if print_it == 1:
				print ''
				print "Printing xmlstring_fixed..."
				print self.obs_recs_xmlstring
				print ''
		except Exception, inst:
			print "Unexpected error opening %s: %s" % ('"self.obs_recs_xmlstring = XmlString(plain_xmlstring_fixed)"', inst)
		
		#self.print_xmltree
		
		return self.xmltree



	def get_record(self, key):
		"""
		Given the key, get a single record, return xmltree for it.
		"""
		
		print ''
		print 'Running get_record(params)...'
	
		# URL for the record utility
		# instructions: http://data.gbif.org/ws/rest/occurrence
		url = 'http://data.gbif.org/ws/rest/occurrence/get'
	
		params = {'format': 'darwin', 'key' : key}
	
		cmd = url + self._paramsdict_to_string(params)
		results_handle = self.access_gbif(url, params)
		
		#print results_handle.read()
		xmlstring = XmlString(results_handle.read())
		
		# Save to a tempfile
		"""
		fn_unfixed ='tempxml_unfixed2.xml'
		fh = open(fn_unfixed, 'w')
		fh.write(xmlstring)
		fh.close()
		"""
		
		# returns plain string, with linebreaks for parsing with ET.fromstring
		xmlstring2 = xmlstring.fix_ASCII_lines('\n')
		
		"""
		fh = open(fn, 'r')
		xmlstring2 = fh.read()
		fh.close()
		"""
		
		print ''
		print 'xmlstring2'
		print xmlstring2
		
		xmltree = ET.ElementTree(ET.fromstring(xmlstring2))
		temp = GbifXml(xmltree)
		temp.print_xmltree()
		
		return xmltree


	
	
	def get_numhits(self, params):
		"""
		Get the number of hits that will be returned by a given search
		(this allows parsing & gradual downloading of searches larger 
		than e.g. 1000 records)
	
		It will return the LAST non-none instance (in a standard search result there
		should be only one, anyway).
		"""
		self.gbif_count_params = params

		print ''
		print 'Running get_numhits(params)...'
	
		# URL for the count utility
		# instructions: http://data.gbif.org/ws/rest/occurrence
		url = 'http://data.gbif.org/ws/rest/occurrence/count'
		
		self.count_params_str = self._paramsdict_to_string(params)
		cmd = url + self.count_params_str
		results_handle = self.access_gbif(url, params)
		
		self.count_recs_xmlstring = XmlString(results_handle.read())
		
		
		
		# Fix xmlstring
		plain_xmlstring_fixed = self.count_recs_xmlstring.fix_ASCII_lines('\n')
		#temp_xmlstring.splitlines() works because XmlString inherits from string class
		
		# Store the plain string in an XmlString object, store as method of
		# GbifXml object
		self.count_recs_xmlstring = XmlString(plain_xmlstring_fixed)
				
		# make sure the self.obs_recs_xmlstring (an XmlString object) parses into an ElementTree
		try:
			self.gbif_count_xmltree = GbifXml(ET.ElementTree(ET.fromstring(self.count_recs_xmlstring)))
		except Exception, inst:
			print "Unexpected error opening %s: %s" % ('"self.count_recs_xmlstring = XmlString(plain_xmlstring_fixed)"', inst)

		
		#print_xmltree(xmltree)

		# Get the element from the xmltree attribute of the GbifXml object stored in self
		for element in self.gbif_count_xmltree.xmltree.getroot():
			temp_numhits = self.gbif_count_xmltree.extract_numhits(element)
			if temp_numhits != None:
				self.gbif_hits_count = int(temp_numhits)
		
		
		print '# hits on "' + self.count_params_str + '" = ' + str(self.gbif_hits_count)
		
		return self.gbif_hits_count
	
	

	
	def xmlstring_to_xmltree(self, xmlstring):
		"""
		Take the text string returned by GBIF and parse to an XML tree using ElementTree.  
		Requires the intermediate step of saving to a temporary file (required to make
		ElementTree.parse work, apparently)
		"""
		
		"""
		tempfn = 'tempxml.xml'
		fh = open(tempfn, 'w')
		fh.write(xmlstring)
		fh.close()
		"""
		
		# instructions for ElementTree:
		# http://docs.python.org/library/xml.etree.elementtree.html
	
		# make sure the file is findable
		try:
			xmltree = ET.fromstring(xmlstring)
		except Exception, inst:
			print "Unexpected error opening %s: %s" % ('file_str', inst)
	
		# make sure the file is parsable
		try:
			xmltree.getroot()
		except Exception, inst:
			print "Unexpected error running getroot() on text in file %s: %s" % (tempfn, inst)
	
		return xmltree
	
	




	
	def get_all_records_by_increment(self, params, inc):
		"""
		Download all of the records in stages, store in list of elements.
		Increments of e.g. 100 to not overload server
		"""

		print ''
		print "Running get_all_records_by_increment(params, inc)"

		# Set up the list of chunks to get
		numhits = self.get_numhits(params)
		print "#hits = ", numhits
		list_of_chunks = range(0, numhits-1, inc)

		# Set up tempfile
		from cStringIO import StringIO
		file_str = StringIO()

		# Set up url to parse
		# instructions: http://data.gbif.org/ws/rest/occurrence
		url = 'http://data.gbif.org/ws/rest/occurrence/list'

		# download them by increment	
		for index, startindex in enumerate(list_of_chunks):
		
			if startindex + inc - 1 > numhits:
				print "Downloading records# ", startindex, numhits-1
				params['startindex'] = str(startindex)
				params['maxresults'] = str(numhits - startindex)
			else:
				print "Downloading records# ", startindex, startindex+inc-1
				params['startindex'] = str(startindex)
				params['maxresults'] = str(inc)
	
			results_handle = self.access_gbif(url, params)
		
			xmlstring = XmlString(results_handle.read())
			xmlstring2 = xmlstring.fix_ASCII_lines('\n')
			results_handle.close()
			
			# Add these latlongs to filestr
			try:
				gbifxml = GbifXml(ET.ElementTree(ET.fromstring(xmlstring2)))
			except:
				print ''
				print '...printing xmlstring2...'
				print xmlstring2
			gbifxml._extract_latlong_datum(gbifxml.xmltree.getroot(), file_str)

						
		return file_str.getvalue()
	


	def _paramsdict_to_string(self, params):
		"""
		# Converts the python dictionary of search parameters into a text 
		# string for submission to GBIF
		"""
		temp_outstring_list = []
		for key in params.keys():
			temp_outstring_list.append(str(key) + '=' + str(params[key]))
		outstring = '&'.join(temp_outstring_list)
		return outstring

	

	
	def _open(self, cgi, params={}):
		"""
		Function for accessing online databases.
		
		Modified from: 
		http://www.biopython.org/DIST/docs/api/Bio.Entrez-module.html

		Helper function to build the URL and open a handle to it (PRIVATE).
	
		Open a handle to Entrez.  cgi is the URL for the cgi script to access.
		params is a dictionary with the options to pass to it.  Does some
		simple error checking, and will raise an IOError if it encounters one.
	
		This function also enforces the "three second rule" to avoid abusing
		the NCBI servers.
		"""
		# NCBI requirement: At least three seconds between queries
		delay = 3.0
		current = time.time()

		wait = self.time_last_gbif_access + delay - current
		if wait > 0:
			time.sleep(wait)
			self.time_last_gbif_access = current + wait
		else:
			self.time_last_gbif_access = current
		# Remove None values from the parameters
		for key, value in params.items():
			if value is None:
				del params[key]
		
		# Eliminating this bit; irrelevant in GBIF
		# Tell Entrez that we are using Biopython
		"""
		if not "tool" in params:
			params["tool"] = "biopython"
		"""
		# Tell Entrez who we are
		if not "email" in params:
			if self.email != None:
				params["email"] = email
		# Open a handle to Entrez.
		options = urllib.urlencode(params, doseq=True)
		cgi += "?" + options
		handle = urllib.urlopen(cgi)
	
		# Wrap the handle inside an UndoHandle.
		uhandle = File.UndoHandle(handle)
	
		# Check for errors in the first 5 lines.
		# This is kind of ugly.
		lines = []
		for i in range(5):
			lines.append(uhandle.readline())
		for i in range(4, -1, -1):
			uhandle.saveline(lines[i])
		data = ''.join(lines)
					   
		if "500 Proxy Error" in data:
			# Sometimes Entrez returns a Proxy Error instead of results
			raise IOError("500 Proxy Error (NCBI busy?)")
		elif "502 Proxy Error" in data:
			raise IOError("502 Proxy Error (NCBI busy?)")
		elif "WWW Error 500 Diagnostic" in data:
			raise IOError("WWW Error 500 Diagnostic (NCBI busy?)")
		elif data.startswith("Error:") :
			#e.g. 'Error: Your session has expired. Please repeat your search.\n'
			raise IOError(data.strip())
		elif data.startswith("The resource is temporarily unavailable") :
			#This can occur with an invalid query_key
			#Perhaps this should be a ValueError?
			raise IOError("The resource is temporarily unavailable")
		elif data.startswith("download dataset is empty") :
			#This can occur when omit the identifier, or the WebEnv and query_key
			#Perhaps this should be a ValueError?
			raise IOError("download dataset is empty")
		elif data[:5] == "ERROR":
			# XXX Possible bug here, because I don't know whether this really
			# occurs on the first line.  I need to check this!
			raise IOError("ERROR, possibly because id not available?")
		# Should I check for 404?  timeout?  etc?
		return uhandle
	
	




