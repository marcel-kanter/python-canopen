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
		description = "abc"
		ds = canopen.objectdictionary.DefStruct(name, index, description)
		
		self.assertEqual(ds.object_type, 6)
		self.assertEqual(ds.name, name)
		self.assertEqual(ds.index, index)
		self.assertEqual(ds.description, description)
		
		with self.assertRaises(AttributeError):
			ds.name = name
		with self.assertRaises(AttributeError):
			ds.index = index
	
	def test_collection(self):
		ds = canopen.objectdictionary.DefStruct("defstruct", 0x40)
		
		#### Test step: add wrong type
		x = canopen.objectdictionary.Array("arr", 0x40, canopen.objectdictionary.UNSIGNED16)
		with self.assertRaises(TypeError):
			ds.add(x)
		
		x = canopen.objectdictionary.Record("rec", 0x40, 0x00)
		with self.assertRaises(TypeError):
			ds.add(x)
		
		x = canopen.objectdictionary.DefType("deftype", 0x40)
		with self.assertRaises(TypeError):
			ds.add(x)
		
		x = canopen.objectdictionary.Domain("domain", 0x40)
		with self.assertRaises(TypeError):
			ds.add(x)
		
		#### Test step: add wrong index
		x = canopen.objectdictionary.Variable("var", 200, 0, canopen.objectdictionary.UNSIGNED8, "ro")
		with self.assertRaises(ValueError):
			ds.add(x)
		
		### Test step: add Variable with UNSIGNED16 to subindex 0
		x = canopen.objectdictionary.Variable("var1", 0x40, 0, canopen.objectdictionary.UNSIGNED16, "ro")
		with self.assertRaises(ValueError):
			ds.add(x)
		
		#### Test step: add correct Variable
		v1 = canopen.objectdictionary.Variable("var1", 0x40, 0, canopen.objectdictionary.UNSIGNED8, "ro")
		ds.add(v1)
		self.assertEqual(len(ds), 1)
		
		### Test step: add Variable twice, same subindex, differend name
		x = canopen.objectdictionary.Variable("var2", 0x40, 0, canopen.objectdictionary.UNSIGNED8, "ro")
		with self.assertRaises(ValueError):
			ds.add(x)
		
		### Test step: add Variable with UNSIGNED32 to subindex 1
		x = canopen.objectdictionary.Variable("var2", 0x40, 1, canopen.objectdictionary.UNSIGNED32, "ro")
		with self.assertRaises(ValueError):
			ds.add(x)
		
		### Test step: add Variable with UNSIGNED16 to subindex 1, but with rw access
		x = canopen.objectdictionary.Variable("var2", 0x40, 1, canopen.objectdictionary.UNSIGNED16, "rw")
		with self.assertRaises(ValueError):
			ds.add(x)
		
		x = canopen.objectdictionary.Variable("var2", 0x40, 0xFF, canopen.objectdictionary.UNSIGNED16, "ro")
		with self.assertRaises(ValueError):
			ds.add(x)
		
		#### Test step: add correct Variable
		v2 = canopen.objectdictionary.Variable("var2", 0x40, 1, canopen.objectdictionary.UNSIGNED16, "ro")
		ds.add(v2)
		self.assertEqual(len(ds), 2)
		
		v3 = canopen.objectdictionary.Variable("var3", 0x40, 0xFF, canopen.objectdictionary.UNSIGNED32, "ro")
		ds.add(v3)
		self.assertEqual(len(ds), 3)
		
		#### Test step: contains
		self.assertFalse("xxx" in ds)
		self.assertFalse(99 in ds)
		self.assertTrue(v1.name in ds)
		self.assertTrue(v1.subindex in ds)
		self.assertTrue(v2.name in ds)
		self.assertTrue(v2.subindex in ds)
		
		# getitem
		item = ds["var1"]
		self.assertTrue(item.name in ds)
		
		#### Test step: iter
		items = []
		for k in ds:
			items.append(k)
		
		#### Test step: delitem
		for x in items:
			del ds[x.name]
		
		self.assertEqual(len(ds), 0)


if __name__ == "__main__":
	unittest.main()
