import shpUtils
import dbfUtils

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




# Code from here:
# http://www.ariel.com.au/a/python-point-int-poly.html
#
# NOTE: does not presently deal with the case of polygons that
# cross the international dateline!
#
# determine if a point is inside a given polygon or not
# Polygon is a list of (x,y) pairs.

def point_inside_polygon(x,y,poly):

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
	if element.__len__() == 0:
		print element.tag, element.text
		return
	elif element.__len__() > 0:
		print element.tag, element.text, "#subelements =", element.__len__()
		for subelement in element.getchildren():
			print_subelements(subelement)
		return

def extract_latlong(element, outfh):
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


