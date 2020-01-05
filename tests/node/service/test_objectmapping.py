import unittest
from canopen.node.service.objectmapping import ObjectMapping


class ObjectMappingTest(unittest.TestCase):
	def test_init(self):
		examinee = ObjectMapping()
		self.assertEqual(len(examinee), 0)


if __name__ == "__main__":
	unittest.main()
