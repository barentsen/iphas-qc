import re


fdone = open('../qcdata/scripts/gotterdammerung/fields-done-in-fall-2012.txt', 'r')
fields_done_fall2012 = [l.strip() for l in fdone.readlines()]

def is_done(field):
	if field in fields_done_fall2012:
		return True
	return False


# Load definition of fields in the format required by the observing scripts
fields_list = open('fields.txt', 'r').readlines()
fields_dict = dict(zip([m.split(' ')[0] for m in fields_list], fields_list))


files = {}
for ra in [0,1,2,3,4,5,6,7,8,18,19,20,21,22,23]:
	files[str(ra)] = open('todo/fields.%sh.todo' % ra, 'w')

def write(info):
	# Obtain Right Ascension from field descriptor
	ra = re.split("\W+", info)[1]
	files[ra].write(info)

fields_written = fields_done_fall2012

def addfile(filename):
	f = open(filename, 'r')
	for line in f.readlines():
		myfield = line.split("\t")[0].strip()
		if myfield not in fields_written:
			fields_written.append( myfield )
			write(fields_dict[myfield])

addfile('priority-1.txt')
addfile('priority-2.txt')
addfile('priority-3.txt')
addfile('extra_janet_gv_6800-1000.txt')

for ra in files.keys():
	files[ra].close()