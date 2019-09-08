import unittest
from canopen.node.service.pdo.pdomapping import PDOMapping


class PDOMappingTest(unittest.TestCase):
	def test_init(self):
		examinee = PDOMapping()
