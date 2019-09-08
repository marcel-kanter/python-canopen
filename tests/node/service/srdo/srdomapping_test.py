import unittest
from canopen.node.service.srdo.srdomapping import SRDOMapping


class SRDOMappingTest(unittest.TestCase):
	def test_init(self):
		examinee = SRDOMapping()
