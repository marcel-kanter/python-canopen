import csv
import canopen.objectdictionary


def _dump_obj(obj, writer):
	r = {"Index": hex(obj.index), "Name": obj.name, "ObjectType": hex(obj.object_type), "Description": obj.description}
	
	if isinstance(obj, (canopen.objectdictionary.Variable, canopen.objectdictionary.Array, canopen.objectdictionary.Record)) and not isinstance(obj, (canopen.objectdictionary.DefStruct, canopen.objectdictionary.Domain)):
		r["DataType"] = hex(obj.data_type)
	
	if isinstance(obj, canopen.objectdictionary.Variable):
		r["AccessType"] = obj.access_type
	
	if isinstance(obj, canopen.objectdictionary.Variable) and not isinstance(obj, canopen.objectdictionary.Domain):
		r["SubIndex"] = hex(obj.subindex)
	
	writer.writerow(r)
	
	if isinstance(obj, (canopen.objectdictionary.Array, canopen.objectdictionary.Record)):
		for o in obj:
			_dump_obj(o, writer)


def dump(obj, file):
	field_names = ["Index", "Name", "ObjectType", "SubIndex", "DataType", "AccessType", "Description"]
	writer = csv.DictWriter(file, field_names, delimiter = "\t")
	
	writer.writeheader()
	
	for o in obj:
		_dump_obj(o, writer)
	
	del writer


def load(file):
	dictionary = canopen.ObjectDictionary()
	reader = csv.DictReader(file, delimiter = "\t")
	
	for row in reader:
		object_type = int(row["ObjectType"], 16)
		name = row["Name"]
		index = int(row["Index"], 16)
		
		if object_type == 6:
			o = canopen.objectdictionary.DefStruct(name, index)
			o.description = row["Description"]
			dictionary.add(o)
		if object_type == 8:
			data_type = int(row["DataType"], 16)
			o = canopen.objectdictionary.Array(name, index, data_type)
			o.description = row["Description"]
			dictionary.add(o)
		if object_type == 9:
			data_type = int(row["DataType"], 16)
			o = canopen.objectdictionary.Record(name, index, data_type)
			o.description = row["Description"]
			dictionary.add(o)
		if object_type == 2:
			access_type = row["AccessType"]
			o = canopen.objectdictionary.Domain(name, index, access_type)
			o.description = row["Description"]
			dictionary.add(o)
		if object_type == 5:
			o = canopen.objectdictionary.DefType(name, index)
			o.description = row["Description"]
			dictionary.add(o)
		if object_type == 7:
			subindex = int(row["SubIndex"], 16)
			data_type = int(row["DataType"], 16)
			access_type = row["AccessType"]
			o = canopen.objectdictionary.Variable(name, index, subindex, data_type, access_type)
			o.description = row["Description"]
			# If there is already an object in the dictionary asume it is an Array of Record
			if index in dictionary:
				dictionary[index].add(o)
			else:
				dictionary.add(o)
	
	del reader
	return dictionary
