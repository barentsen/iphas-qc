"""
Read the priority-*.txt files and generate corresponding field lists
which are understood by the IPHAS observing scripts.

Todo lists are organized by R.A. hour "output-todo/fields.**h.todo"
to make it easier to observe them at the right time.
"""
import re
import matplotlib.pyplot as plt
import numpy as np

# Load fields observed successfully recently
fdone = open('../data/gotterdammerung/fields-done-in-fall-2012.txt', 'r')
fields_done = [l.strip() for l in fdone.readlines()]

# Load definition of fields in the format required by the observing scripts
fields_list = open('fields.txt', 'r').readlines()
fields_dict = dict(zip([m.split(' ')[0] for m in fields_list], fields_list))

# Global variable to hold output files
files = {}
rahist = {}

def output_open():
	"""Initiate the output files"""
	for ra in [0,1,2,3,4,5,6,7,8,18,19,20,21,22,23]:
		files[str(ra)] = open('output-todo/fields.%sh.todo' % ra, 'w')

def output_close():
	# Close the output files
	for ra in files.keys():
		files[ra].close()

def add_field(filename, info):
	"""Write a field descriptor to the appropriate todo file"""
	# Obtain Right Ascension from field descriptor
	ra = re.split("\W+", info)[1]
	files[ra].write(info)
	rahist[filename].append( int(ra) )

def process_file(filename):
	"""Add all fields listed in 'filename' to the todo files"""
	rahist[filename] = []
	f = open(filename, 'r')
	for line in f.readlines():
		# Assume the field identifier "nnnn(o)" is the first row
		myfield = line.split("\t")[0].strip()
		if myfield not in fields_done:
			add_field(filename, fields_dict[myfield])
			fields_done.append( myfield )

def plot_histogram():
	"""Histogram showing fields remaining per R.A. bin"""
	f = plt.figure()
	ax = f.add_subplot(111)
	ax.set_title('IPHAS fields left to do', fontsize=26)
	ax.set_xlabel('R.A.')
	ax.set_xticks( tuple( np.arange(0,24) ) )
	# Actual histogram plotting:
	data = (rahist['priority-1.txt'], rahist['priority-2.txt'], rahist['priority-3.txt'], rahist['priority-4.txt'], rahist['priority-5.txt'])
	mylabels = ('Priority 1', 'Priority 2', 'Priority 3', 'Priority 4', 'Priority 5')
	mycolors = ('red', 'blue', 'gray', 'gray', 'darkgray')
	ax.hist(data, histtype='barstacked', label=mylabels, color=mycolors, bins=24, range=(0,24))
	ax.legend()
	f.savefig('output-todo/iphas-todo-histogram.png')
	plt.close(f)


""" MAIN EXECUTION """
output_open()
process_file('priority-1.txt')
process_file('priority-2.txt')
process_file('priority-3.txt')
process_file('priority-4.txt')
process_file('priority-5.txt')
#process_file('extra_janet_gv_6800-1000.txt')
plot_histogram()
output_close()
