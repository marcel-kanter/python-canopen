import unittest
import canopen
import canopen.objectdictionary


class LocalNodeTestCase(unittest.TestCase):
	def test_init(self):
		dictionary = canopen.ObjectDictionary()
		
		with self.assertRaises(ValueError):
			canopen.LocalNode("n", 0, dictionary)
		with self.assertRaises(ValueError):
			canopen.LocalNode("n", 128, dictionary)
		with self.assertRaises(TypeError):
			canopen.LocalNode("n", 1, None)
		
		name = "n"
		node_id = 1
		node = canopen.LocalNode(name, node_id, dictionary)
		
		self.assertEqual(node.dictionary, dictionary)
		self.assertEqual(node.id, node_id)
		self.assertEqual(node.name, name)
		self.assertEqual(node.network, None)
		
		with self.assertRaises(AttributeError):
			node.dictionary = dictionary
		with self.assertRaises(AttributeError):
			node.id = node_id
		with self.assertRaises(AttributeError):
			node.name = name
		with self.assertRaises(AttributeError):
			node.network = None

	def test_attach_detach(self):
		network1 = canopen.Network()
		network2 = canopen.Network()
		dictionary = canopen.ObjectDictionary()
		node = canopen.LocalNode("n", 1, dictionary)
		
		with self.assertRaises(RuntimeError):
			node.detach()
		
		with self.assertRaises(TypeError):
			node.attach(None)
		
		node.attach(network1)
		
		self.assertEqual(node.network, network1)
		
		with self.assertRaises(ValueError):
			node.attach(network1)
		
		node.attach(network2)
		
		self.assertEqual(node.network, network2)
		
		node.detach()

	def test_data_access(self):
		dictionary = canopen.ObjectDictionary()
		dictionary.add(canopen.objectdictionary.Record("rec", 0x1234))
		dictionary["rec"].add(canopen.objectdictionary.Variable("integer32", 0x1234, 0x04, canopen.objectdictionary.INTEGER32, "rw"))
		dictionary.add(canopen.objectdictionary.Variable("var", 0x5678, 0x00, canopen.objectdictionary.UNSIGNED32, "rw"))
		examinee = canopen.LocalNode("n", 1, dictionary)
		
		# Store some data as default value
		dictionary["rec"]["integer32"].default_value = 0x55AA
		dictionary["var"].default_value = 0xCAFE
		
		#### Test step: get_data of entry that is not existent
		with self.assertRaises(KeyError):
			examinee.get_data(0x9999, 0x00)
		
		#### Test step: get_data of entry that is not existent
		with self.assertRaises(KeyError):
			examinee.get_data(0x1234, 0x99)
		
		#### Test step: get_data of entry that has no data in node -> should be the default value
		self.assertEqual(examinee.get_data(0x1234, 0x04), dictionary["rec"]["integer32"].default_value)
		
		#### Test step: Unless data is set, the default value from dictionary is returned
		# Change the default value in dictionary and the value returned by the node still is the same
		dictionary["rec"]["integer32"].default_value = 0xAA55
		self.assertEqual(examinee.get_data(0x1234, 0x04), dictionary["rec"]["integer32"].default_value)
		
		#### Test step set some data into node
		examinee.set_data(0x1234, 0x04, 0xCAFE)
		self.assertEqual(examinee.get_data(0x1234, 0x04), 0xCAFE)
		
		#### Test step: get data of a Variable (default value)
		self.assertEqual(examinee.get_data(0x5678, 0x00), dictionary["var"].default_value)
		
		#### Test step set some data into node
		examinee.set_data(0x5678, 0x00, 0xAFFE)
		self.assertEqual(examinee.get_data(0x5678, 0x00), 0xAFFE)


if __name__ == "__main__":
	unittest.main()
