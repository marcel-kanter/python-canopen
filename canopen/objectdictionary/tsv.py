import csv
import canopen.objectdictionary


def _dump_obj(obj, writer):
	r = {"index": hex(obj.index), "name": obj.name, "object type": hex(obj.object_type), "description": obj.description}
	
	if isinstance(obj, (canopen.objectdictionary.Variable, canopen.objectdictionary.Array, canopen.objectdictionary.Record)) and not isinstance(obj, (canopen.objectdictionary.DefStruct, canopen.objectdictionary.Domain)):
		r["data type"] = hex(obj.data_type)
	
	if isinstance(obj, canopen.objectdictionary.Variable):
		r["access type"] = obj.access_type
	
	if isinstance(obj, canopen.objectdictionary.Variable) and not isinstance(obj, canopen.objectdictionary.Domain):
		r["sub-index"] = hex(obj.subindex)
	
	writer.writerow(r)
	
	if isinstance(obj, (canopen.objectdictionary.Array, canopen.objectdictionary.Record)):
		for o in obj:
			_dump_obj(o, writer)


def dump(obj, file):
	field_names = ["index", "name", "object type", "sub-index", "data type", "access type", "description"]
	writer = csv.DictWriter(file, field_names, delimiter = "\t")
	
	writer.writeheader()
	
	for o in obj:
		_dump_obj(o, writer)
	
	del writer


def load(file):
	dictionary = canopen.ObjectDictionary()
	reader = csv.DictReader(file, delimiter = "\t")
	
	for row in reader:
		object_type = int(row["object type"], 16)
		name = row["name"]
		index = int(row["index"], 16)
		
		if object_type == 6:
			o = canopen.objectdictionary.DefStruct(name, index)
			dictionary.add(o)
		if object_type == 8:
			data_type = int(row["data type"], 16)
			o = canopen.objectdictionary.Array(name, index, data_type)
			dictionary.add(o)
		if object_type == 9:
			data_type = int(row["data type"], 16)
			o = canopen.objectdictionary.Record(name, index, data_type)
			dictionary.add(o)
		if object_type == 2:
			access_type = row["access type"]
			o = canopen.objectdictionary.Domain(name, index, access_type)
			dictionary.add(o)
		if object_type == 5:
			o = canopen.objectdictionary.DefType(name, index)
			dictionary.add(o)
		if object_type == 7:
			subindex = int(row["sub-index"], 16)
			data_type = int(row["data type"], 16)
			access_type = row["access type"]
			o = canopen.objectdictionary.Variable(name, index, subindex, data_type, access_type)
			# If there is already an object in the dictionary asume it is an Array of Record
			if index in dictionary:
				dictionary[index].add(o)
			else:
				dictionary.add(o)
	
	del reader
	return dictionary
