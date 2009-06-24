#!/usr/bin/python
import os
from geogUtils import readshpfile, summarize_shapefile, point_inside_polygon, shapefile_points_in_poly

from geogUtils import access_gbif, get_numhits, get_hits, print_xmltree, get_xml_hits, extract_taxonconceptkeys_tofile, extract_taxonconceptkeys_tolist, get_record, get_all_records_by_increment


from geogUtils import lagrange_disclaimer, read_ultrametric_Newick, list_leaves, print_tree_outline_format, treelength, phylodistance, get_distance_matrix, subset_tree


lagrange_disclaimer()


print "Running _test_functions_wk4.py..."
print ""
print "Here is an example Newick file:"
print "(Bovine:0.69395,(Gibbon:0.36079,(Orang:0.33636,(Gorilla:0.17147,(Chimp:0.19268, Human:0.11927):0.08386):0.06124):0.15057):0.54939,Mouse:1.21460):0.10;"

newickstr = "(Bovine:0.69395,(Gibbon:0.36079,(Orang:0.33636,(Gorilla:0.17147,(Chimp:0.19268, Human:0.11927):0.08386):0.06124):0.15057):0.54939,Mouse:1.21460):0.10;"

phylo_obj = read_ultrametric_Newick(newickstr)

print ""
print "Printing the parsed newick tree"
print phylo_obj
print ""

numleaves = list_leaves(phylo_obj)

print_tree_outline_format(phylo_obj)


treelen = treelength(phylo_obj)
print "Total phylogenetic branch length in tree = ", treelen

x=phylo_obj
y=x.leaves()
PD = phylodistance(y[5], y[0])

print ""
print "Phylogenetic distances between two tips = ", PD


mar = get_distance_matrix(phylo_obj)

print ""
print "Getting distance matrix between all pairs of leaves"
print mar



print ""
print "Subsetting a tree"
list_to_keep = ["Human", "Chimp"]
newtree = subset_tree(phylo_obj, list_to_keep)
print "Here is the new tree:"
print_tree_outline_format(newtree)


stop
