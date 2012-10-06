import re

# Load definition of fields in the format required by the observing scripts
fields_list = open('fields.txt', 'r').readlines()
fields_dict = dict(zip([m.split(' ')[0] for m in fields_list], fields_list))


files = {}
for ra in [0,1,2,3,4,5,6,7,8,18,19,20,21,22,23]:
	files[str(ra)] = open('todo/fields.%sh.todo' % ra, 'w')

def write(info):
	ra = re.split("\W+", info)[1]
	files[ra].write(info)

def addfile(filename):
	f = open(filename, 'r')
	for line in f.readlines():
		myfield = line.split("\t")[0]
		write(fields_dict[myfield])

addfile('priority-1.txt')
addfile('priority-2.txt')
addfile('priority-3.txt')

for ra in files.keys():
	files[ra].close()