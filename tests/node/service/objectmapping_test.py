import unittest
from canopen.node.service.objectmapping import ObjectMapping


class ObjectMappingTest(unittest.TestCase):
	def test_init(self):
		examinee = ObjectMapping()
