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


class GbifXmlError(Exception): pass


class GbifXml():
	"""gbifxml is a class for holding and processing xmltrees of GBIF records."""
	
	# Info prints out the informative description of this class, if a user wants to see it.
	info = "Information about this class: gbifxml is a class for holding and processing xmltrees of GBIF records."
	
	
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
	
	def element_items_to_dictionary(self, element_items):
		"""
		If the XML tree element has items encoded in the tag, e.g. key/value or
		whatever, this function puts them in a python dictionary and returns 
		them.
		"""
		
		if len(element_items) < 2:
			print "element_items_to_dictionary error: < 2 items in element"
			return None
		else:
			temp_dict = {}
			for item in element_items:
				temp_dict[item[0][1]] = item[1][1]
			return temp_dict

		"""
		temp_dict = element_items_to_dictionary(element.keys())
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
		self.extract_latlong_datum(element, file_str)
		return file_str.getvalue()



	def extract_latlong_datum(self, element, file_str):
		"""
		Searches an element in an XML tree for lat/long information, and the 
		complete name. Searches recursively, if there are subelements.
		"""
		if element.__len__() == 0:
			return (element.tag, element.text)
		elif element.__len__() > 0:
			#print element.tag, element.text, "#subelements =", element.__len__()
			for subelement in element.getchildren():
				temptuple = self.extract_latlong_datum(subelement, file_str)
				if temptuple[0].endswith('decimalLatitude'):
					file_str.write(temptuple[1] + '\t')
				elif temptuple[0].endswith('decimalLongitude'):
					file_str.write(temptuple[1] + '\t')
				elif temptuple[0].endswith('nameComplete'):
					#if temptuple[1] != '':
					file_str.write(temptuple[1] + '\n')
			return ('tag: parent subelement', 'text: multiple subelements')
			

	
	
	def extract_taxonconceptkeys_tofile(self, element, outfh):
		"""
		Searches an element in an XML tree for TaxonOccurrence gbifKeys, and the complete sname. Searches recursively, if there are subelements.  Returns file at outfh.
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
					returned_item = self.extract_taxonconceptkeys_tofile(subelement, outfh)
			
			return ('Error: no TaxonOccurrence gbifKey found')
	
	
	def extract_taxonconceptkeys_tolist(self, element, output_list):
		"""
		Searches an element in an XML tree for TaxonOccurrence gbifKeys, and the complete name. Searches recursively, if there are subelements.  Returns list.
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
					templist = self.extract_taxonconceptkeys_tolist(subelement, output_list)
					
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
	
	
	
	def extract_occurrence_elements(self, element, output_list):
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
					output_list = self.extract_occurrence_elements(subelement, output_list)
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
	
	
	
	def create_sub_xmltree(self, element):
		"""
		Create a subset xmltree (to avoid going back to irrelevant parents)
		"""
		
		xmltree = ET.ElementTree(element)
		
		return xmltree
	
	
	
	
	def xml_recursive_search_w_anc(self, element, el_tag, anc_el_tag, match_el_list):
		"""
		Recursively burrows down to find whatever elements with el_tag exist inside a parent_el_tag.
		"""
		xmltree = self.xmltree
		
		# If the element matches the tag you are looking for...
		if element.tag == el_tag:
	
			# Then check if the ancestor matches
			found_anc = None
			ancestor = self.xml_burrow_up(element, anc_el_tag, found_anc)
			
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
			
			
	
	def xml_burrow_up(self, element, anc_el_tag, found_anc):
		"""
		Burrow up xml to find anc_el_tag
		"""
		xmltree = self.xmltree
		
		if found_anc == None:
			# Just get the direct parent of child_to_search_for
			child_to_search_for = element
			parent_element = self.return_parent_in_xmltree(child_to_search_for)
			
			if parent_element == None:
				return found_anc
			
			# Does the parent match the searched-for ancestor?		
			if parent_element.tag == anc_el_tag:
				found_anc = parent_element
			else:
				# Move a level up and search again, return if found
	
				found_anc = self.xml_burrow_up(parent_element, anc_el_tag, found_anc)
	
			return found_anc
			
		else:
			return found_anc
			
		
	
	def xml_burrow_up_cousin(element, cousin_el_tag, found_cousin):
		"""
		Burrow up from element of interest, until a cousin is found with cousin_el_tag
		"""
		xmltree = self.xmltree
		
		if found_cousin == None:
			# Just get the direct parent of child_to_search_for
			child_to_search_for = element
			parent_element = self.return_parent_in_xmltree(xmltree, child_to_search_for)
			
			if parent_element == None:
				return found_cousin
			
			grandparent_element = self.return_parent_in_xmltree(parent_element)
			if grandparent_element == None:
				return found_cousin
			
			# Does the parent or any cousins match the searched-for ancestor?		
			for aunt in grandparent_element.getchildren():
				if aunt.tag == cousin_el_tag:
					found_cousin = aunt
					return found_cousin
			
			if found_cousin == None:
				# Move a level up and search again, return if found
				found_cousin = self.xml_burrow_up_cousin(parent_element, cousin_el_tag, found_cousin)
	
			return found_cousin
			
		else:
			return found_cousin
		
	
	
	def return_parent_in_xmltree(self, child_to_search_for):
		"""
		Search through an xmltree to get the parent of child_to_search_for
		"""
		xmltree = self.xmltree
		
		returned_parent = None
		for element in xmltree.getroot():
			
			potential_parent = element
			
			returned_parent = self.return_parent_in_element(potential_parent, child_to_search_for, returned_parent)
			
			return returned_parent
			
					
		
	def return_parent_in_element(self, potential_parent, child_to_search_for, returned_parent):
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
						returned_parent = self.return_parent_in_element(child, child_to_search_for, returned_parent)
							
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
		
	


	
	



# Functions devoted to accessing/downloading GBIF records




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


