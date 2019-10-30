import csv
import canopen


def dump(obj, file):
	field_names = ["name", "index", "sub-index"]
	writer = csv.DictWriter(file, field_names, delimiter = "\t")
	
	writer.writeheader()
	
	del writer

def load(file):
	dictionary = canopen.ObjectDictionary()
	reader = csv.DictReader(file, delimiter = "\t")
	
	del reader
	return dictionary
