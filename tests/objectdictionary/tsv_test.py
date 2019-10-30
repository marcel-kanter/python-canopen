import unittest
import os
import tempfile
import canopen.objectdictionary.tsv


class TSVTest(unittest.TestCase):
	def test_dump(self):
		dictionary = canopen.ObjectDictionary()
		
		file = tempfile.TemporaryFile("w+", newline = "")
		canopen.objectdictionary.tsv.dump(dictionary, file)
		
		file.seek(0)
				
		file.close()
	
	def test_load(self):
		file = open(os.path.join(os.path.dirname(__file__), "data", "empty.tsv"))
		dictionary = canopen.objectdictionary.tsv.load(file)
		
		self.assertEqual(len(dictionary), 0)


if __name__ == "__main__":
	unittest.main()
