import unittest
import os
import tempfile
import canopen.objectdictionary.tsv


class TSVTest(unittest.TestCase):
	def setUp(self):
		"""
		Generate a default dictionary with all types of objects and use it as base for the test.
		"""
		
		dictionary = canopen.ObjectDictionary()
		
		dictionary.add(canopen.objectdictionary.DefStruct("Identity", 0x23))
		dictionary["Identity"].description = "Data structure definition for Identity object."
		dictionary["Identity"].add(canopen.objectdictionary.Variable("Highest sub-index supported", 0x23, 0x00, canopen.objectdictionary.UNSIGNED8, "ro")) 
		dictionary["Identity"].add(canopen.objectdictionary.Variable("Vendor-ID", 0x23, 0x01, canopen.objectdictionary.UNSIGNED16, "ro"))
		dictionary["Identity"].add(canopen.objectdictionary.Variable("Product code", 0x23, 0x02, canopen.objectdictionary.UNSIGNED16, "ro"))
		dictionary["Identity"].add(canopen.objectdictionary.Variable("Revision number", 0x23, 0x03, canopen.objectdictionary.UNSIGNED16, "ro"))
		dictionary["Identity"].add(canopen.objectdictionary.Variable("Serial number", 0x23, 0x04, canopen.objectdictionary.UNSIGNED16, "ro"))
		
		dictionary.add(canopen.objectdictionary.DefType("deftype", 0x60))
		dictionary["deftype"].description = "A data type definition."
		
		dictionary.add(canopen.objectdictionary.Variable("Device type", 0x1000, 0x00, canopen.objectdictionary.UNSIGNED32, "ro"))
		dictionary["Device type"].description = "The type of the CANopen device."
		
		dictionary.add(canopen.objectdictionary.Variable("Error register", 0x1001, 0x00, canopen.objectdictionary.UNSIGNED8, "ro"))
		
		dictionary.add(canopen.objectdictionary.Variable("Manufacturer status register", 0x1002, 0x00, canopen.objectdictionary.UNSIGNED32, "ro"))
		
		dictionary.add(canopen.objectdictionary.Variable("COB-ID SYNC", 0x1005, 0x00, canopen.objectdictionary.UNSIGNED32, "rw"))
		
		dictionary.add(canopen.objectdictionary.Variable("Communication cycle period", 0x1006, 0x00, canopen.objectdictionary.UNSIGNED32, "rw"))
		
		dictionary.add(canopen.objectdictionary.Variable("Synchronous window length", 0x1007, 0x00, canopen.objectdictionary.UNSIGNED32, "rw"))
		
		dictionary.add(canopen.objectdictionary.Variable("Manufacturer device name", 0x1008, 0x00, canopen.objectdictionary.VISIBLE_STRING, "ro"))
		
		dictionary.add(canopen.objectdictionary.Variable("Manufacturer hardware version", 0x1009, 0x00, canopen.objectdictionary.VISIBLE_STRING, "ro"))
		
		dictionary.add(canopen.objectdictionary.Variable("Manufacturer software version", 0x100A, 0x00, canopen.objectdictionary.VISIBLE_STRING, "ro"))
		
		dictionary.add(canopen.objectdictionary.Variable("Guard time", 0x100C, 0x00, canopen.objectdictionary.UNSIGNED16, "rw"))
		
		dictionary.add(canopen.objectdictionary.Variable("Life time factor", 0x100D, 0x00, canopen.objectdictionary.UNSIGNED16, "rw"))
		
		dictionary.add(canopen.objectdictionary.Array("Store parameters", 0x1010, canopen.objectdictionary.UNSIGNED32))
		dictionary[0x1010].add(canopen.objectdictionary.Variable("Highest sub-index supported", 0x1010, 0x00, canopen.objectdictionary.UNSIGNED8, "ro"))
		dictionary[0x1010].add(canopen.objectdictionary.Variable("Save all parameters", 0x1010, 0x01, canopen.objectdictionary.UNSIGNED32, "rw"))
		dictionary[0x1010].add(canopen.objectdictionary.Variable("Save communication parameters", 0x1010, 0x02, canopen.objectdictionary.UNSIGNED32, "rw"))
		dictionary[0x1010].add(canopen.objectdictionary.Variable("Save application parameters", 0x1010, 0x03, canopen.objectdictionary.UNSIGNED32, "rw"))
		
		dictionary.add(canopen.objectdictionary.Array("Restore default parameters", 0x1011, canopen.objectdictionary.UNSIGNED32))
		dictionary[0x1011].add(canopen.objectdictionary.Variable("Highest sub-index supported", 0x1011, 0x00, canopen.objectdictionary.UNSIGNED8, "ro"))
		dictionary[0x1011].add(canopen.objectdictionary.Variable("Restore all default parameters", 0x1011, 0x01, canopen.objectdictionary.UNSIGNED32, "rw"))
		dictionary[0x1011].add(canopen.objectdictionary.Variable("Restore communication default parameters", 0x1011, 0x02, canopen.objectdictionary.UNSIGNED32, "rw"))
		dictionary[0x1011].add(canopen.objectdictionary.Variable("Restore application default parameters", 0x1011, 0x03, canopen.objectdictionary.UNSIGNED32, "rw"))
		
		dictionary.add(canopen.objectdictionary.Variable("COB-ID TIME", 0x1012, 0x00, canopen.objectdictionary.UNSIGNED32, "rw"))
		
		dictionary.add(canopen.objectdictionary.Variable("High resolution time stamp", 0x1013, 0x00, canopen.objectdictionary.UNSIGNED32, "rw"))
		
		dictionary.add(canopen.objectdictionary.Variable("COB-ID EMCY", 0x1014, 0x00, canopen.objectdictionary.UNSIGNED32, "rw"))
		
		dictionary.add(canopen.objectdictionary.Variable("Inhibit time EMCY", 0x1015, 0x00, canopen.objectdictionary.UNSIGNED16, "rw"))
		
		dictionary.add(canopen.objectdictionary.Variable("Producer heartbeat time", 0x1017, 0x00, canopen.objectdictionary.UNSIGNED16, "rw"))
		
		dictionary.add(canopen.objectdictionary.Record("Identity object", 0x1018, 0x23))
		dictionary["Identity object"].add(canopen.objectdictionary.Variable("Highest sub-index supported", 0x1018, 0x00, canopen.objectdictionary.UNSIGNED8, "ro"))
		dictionary["Identity object"].add(canopen.objectdictionary.Variable("Vendor-ID", 0x1018, 0x01, canopen.objectdictionary.UNSIGNED16, "ro"))
		dictionary["Identity object"].add(canopen.objectdictionary.Variable("Product code", 0x1018, 0x02, canopen.objectdictionary.UNSIGNED16, "ro"))
		dictionary["Identity object"].add(canopen.objectdictionary.Variable("Revision number", 0x1018, 0x03, canopen.objectdictionary.UNSIGNED16, "ro"))
		dictionary["Identity object"].add(canopen.objectdictionary.Variable("Serial number", 0x1018, 0x04, canopen.objectdictionary.UNSIGNED16, "ro"))
		
		dictionary.add(canopen.objectdictionary.Domain("Domain", 0x2000, "rw"))
		
		self.dictionary = dictionary
		
	def test_dump(self):
		file_1 = tempfile.TemporaryFile("w+", newline = "")
		file_2 = open(os.path.join(os.path.dirname(__file__), "data", "all.tsv"), mode = "r", newline = "")
		
		canopen.objectdictionary.tsv.dump(self.dictionary, file_1)
		
		file_1.seek(0)
		
		self.assertEqual(set(file_1), set(file_2))
		
		file_1.close()
		file_2.close()
	
	def test_load(self):
		file = open(os.path.join(os.path.dirname(__file__), "data", "empty.tsv"))
		dictionary = canopen.objectdictionary.tsv.load(file)
		
		self.assertEqual(len(dictionary), 0)
		file.close()
		
		file = open(os.path.join(os.path.dirname(__file__), "data", "all.tsv"))
		dictionary = canopen.objectdictionary.tsv.load(file)
		
		self.assertEqual(dictionary, self.dictionary)
		
		file.close()


if __name__ == "__main__":
	unittest.main()
