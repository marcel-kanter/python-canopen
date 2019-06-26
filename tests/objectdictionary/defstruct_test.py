import unittest
import canopen.objectdictionary


class DefStructTestCase(unittest.TestCase):
	def test_init(self):
		with self.assertRaises(ValueError):
			canopen.objectdictionary.DefStruct("defstruct", -1)
		with self.assertRaises(ValueError):
			canopen.objectdictionary.DefStruct("defstruct", 65536)
		
		name = "defstruct"
		index = 0x40
		ds = canopen.objectdictionary.DefStruct(name, index)
		
		self.assertEqual(ds.name, name)
		self.assertEqual(ds.index, index)
		
		with self.assertRaises(AttributeError):
			ds.name = name
		with self.assertRaises(AttributeError):
			ds.index = index
	
	def test_collection(self):
		ds = canopen.objectdictionary.DefStruct("defstruct", 0x40)
		
		#### Test step: Append wrong type
		x = canopen.objectdictionary.Array("arr", 0x40)
		with self.assertRaises(TypeError):
			ds.append(x)
		
		x = canopen.objectdictionary.Record("rec", 0x40)
		with self.assertRaises(TypeError):
			ds.append(x)
		
		x = canopen.objectdictionary.DefType("deftype", 0x40)
		with self.assertRaises(TypeError):
			ds.append(x)
		
		#### Test step: Append wrong index
		x = canopen.objectdictionary.Variable("var", 200, 0, canopen.objectdictionary.UNSIGNED8, "ro")
		with self.assertRaises(ValueError):
			ds.append(x)
		
		### Test step: Append Variable with UNSIGNED16 to subindex 0
		x = canopen.objectdictionary.Variable("var1", 0x40, 0, canopen.objectdictionary.UNSIGNED16, "ro")
		with self.assertRaises(ValueError):
			ds.append(x)
		
		#### Test step: Append correct Variable
		v1 = canopen.objectdictionary.Variable("var1", 0x40, 0, canopen.objectdictionary.UNSIGNED8, "ro")
		ds.append(v1)
		self.assertEqual(len(ds), 1)
		
		### Test step: Append Variable twice, same subindex, differend name
		x = canopen.objectdictionary.Variable("var2", 0x40, 0, canopen.objectdictionary.UNSIGNED8, "ro")
		with self.assertRaises(ValueError):
			ds.append(x)
		
		### Test step: Append Variable with UNSIGNED32 to subindex 1
		x = canopen.objectdictionary.Variable("var2", 0x40, 1, canopen.objectdictionary.UNSIGNED32, "ro")
		with self.assertRaises(ValueError):
			ds.append(x)
		
		### Test step: Append Variable with UNSIGNED32 to subindex 1
		x = canopen.objectdictionary.Variable("var2", 0x40, 1, canopen.objectdictionary.UNSIGNED16, "rw")
		with self.assertRaises(ValueError):
			ds.append(x)
		
		#### Test step: Append correct Variable
		v2 = canopen.objectdictionary.Variable("var2", 0x40, 1, canopen.objectdictionary.UNSIGNED16, "ro")
		ds.append(v2)
		self.assertEqual(len(ds), 2)
		
		#### Test step: contains
		self.assertFalse("xxx" in ds)
		self.assertFalse(99 in ds)
		self.assertTrue(v1.name in ds)
		self.assertTrue(v1.subindex in ds)
		self.assertTrue(v2.name in ds)
		self.assertTrue(v2.subindex in ds)
		
		#### Test step: iter, getitem
		items = []
		for k in ds:
			items.append(ds[k])
		
		#### Test step: delitem
		for x in items:
			del ds[x.name]
		
		self.assertEqual(len(ds), 0)


if __name__ == "__main__":
	unittest.main()
