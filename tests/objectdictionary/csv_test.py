import unittest
import os
import tempfile
import canopen
import canopen.objectdictionary.csv


class CSVTest(unittest.TestCase):
	def test_dump(self):
		dictionary = canopen.ObjectDictionary()
		file = tempfile.TemporaryFile()
		canopen.objectdictionary.csv.dump(dictionary, file)
		file.close()
	
	def test_load(self):
		file = open(os.path.join(os.path.dirname(__file__), 'data', 'empty.csv'))
		dictionary = canopen.objectdictionary.csv.load(file)
		
		self.assertEqual(len(dictionary), 0)


if __name__ == "__main__":
	unittest.main()
