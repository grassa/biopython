"""
Generic functions for simple operations.
"""
# Used by unescape
import unicodedata
import re, htmlentitydefs
from numpy import array, reshape, NaN
# Public domain module to convert diverse characters to ASCII (dammit!)
# http://newsbruiser.tigris.org/source/browse/~checkout~/newsbruiser/nb/lib/AsciiDammit.py
from AsciiDammit import asciiDammit


def make_NaN_array(xdim, ydim):
	"""
	Make an empty floating-point array with the specified dimensions
	"""
	temparray = array( [NaN] * (xdim * ydim), dtype=float)
	temparray = reshape(temparray, (xdim, ydim))
	return temparray
	
	
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

def set_diags_to_none(list_array):
	"""
	Given a square list of lists (rows), set the diagonal to None.
	"""
	ydim = len(list_array)
	xdim = len(list_array[0])
	
	if xdim != ydim:
		print ''
		print 'ERROR: This list_array is not a square!'
	
	for index1 in range(0, ydim-1):
		for index2 in range(0, xdim-1):
			list_array[index1, index2] = None
	
	return list_array


def list1_items_in_list2(list1, list2):
	"""
	Returns the list of list1 items which are found in list2
	http://vermeulen.ca/python-techniques.html
	"""
	intersection = filter(lambda x:x in list1, list2)
	return intersection

def list1_items_not_in_list2(list1, list2):
	"""
	Returns the list of list1 items which are NOT found in list2
	http://vermeulen.ca/python-techniques.html
	"""
	difference=filter(lambda x:x not in list2,list1)
	return difference



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
	

def fix_ampersand(line):
	"""
	Replaces "&" with "&amp;" in a string; this is otherwise 
	not caught by the unescape and unicodedata.normalize functions.
	"""
	return line.replace('&', '&amp;')



def fix_ASCII_file(fn_unfixed):
	"""
	# Search-replace to fix annoying 
	# non-ASCII characters in search results
	# 
	# inspiration:
	# http://www.amk.ca/python/howto/unicode
	# http://www.peterbe.com/plog/unicode-to-ascii
	"""
	if fn_unfixed.count('.') < 1:
		return None
	
	# Make a new filename, insert '_fixed' before the rightmost period
	fn_fixed_tuple = fn_unfixed.rpartition('.')
	fn_fixed = ''.join( [fn_fixed_tuple[0], '_fixed.', fn_fixed_tuple[2]] )

	# Open unfixed file and fix all non-ASCII characters
	fh = open(fn_unfixed, 'r')
	fh_fixed = open(fn_fixed, 'w')
	for line in fh:
		#print line
		
		# library from here: http://effbot.org/zone/re-sub.htm#unescape-html
		ascii_content1 = unescape(line)
		
		# Public domain module to convert diverse characters to ASCII
		# http://newsbruiser.tigris.org/source/browse/~checkout~/newsbruiser/nb/lib/AsciiDammit.py
		ascii_content2 = asciiDammit(ascii_content1)
		
		# inspiration: http://www.amk.ca/python/howto/unicode
		ascii_content3 = unicodedata.normalize('NFKC', unicode(ascii_content2)).encode('ascii','ignore')
		
		# Fix the ampersand
		ascii_content = fix_ampersand(ascii_content3)
		
		#print ascii_content		
		fh_fixed.write(ascii_content)

	fh_fixed.close()
	fh.close()
	return fn_fixed




def fix_ASCII(lines):
	"""
	Convert each line in an input string into pure ASCII
	(This avoids crashes when printing to screen, etc.)
	"""
	
	newstr_list = []
	for line in lines:
		
		# library from here: http://effbot.org/zone/re-sub.htm#unescape-html
		ascii_content1 = unescape(line)
		
		# Public domain module to convert diverse characters to ASCII
		# http://newsbruiser.tigris.org/source/browse/~checkout~/newsbruiser/nb/lib/AsciiDammit.py
		ascii_content2 = asciiDammit(ascii_content1)
		
		# inspiration: http://www.amk.ca/python/howto/unicode
		ascii_content3 = unicodedata.normalize('NFKC', unicode(ascii_content2)).encode('ascii','ignore')
		
		# Fix the ampersand
		ascii_content = fix_ampersand(ascii_content3)
		newstr_list.append(ascii_content + '\n')

	return ''.join(newstr_list)



def element_text_to_string(txt):
	if txt == None:
		txt = ""
	return str(txt).strip()


def element_items_to_string(items):
	"""
	Input a list of items, get string back
	"""
	s = ""
	for item in items:
		s = s + " " + str(item)
		s = s.strip()
	
	return s




def get_str_subset(start, end, seq):
	
	index1 = start-1
	index2 = end
	
	newstring = str()
	
	for i in range(index1, index2):
		newstring = newstring + seq[i]
	
	#print 'len(newstring)=', str(len(newstring))
	#print 'start - stop', str(end - start + 1) 
	
	return newstring



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


	
def print_obj(obj):
	"""
	print/run all the methods in an object
	"""
	
	methods = dir(obj)
	
	for method in methods:
		print method
		"""
		tempstr = "obj" + "." + str(method)
		print ''
		print tempstr
		
		# Return object type
		cmd1 = 'type(' + tempstr + ')'
		print cmd1
		eval(cmd1)
		"""
		
		
	