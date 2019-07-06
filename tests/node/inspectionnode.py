from unittest.mock import Mock
import canopen.node


class InspectionNode(canopen.Node):
	def __init__(self, name, node_id, dictionary):
		canopen.Node.__init__(self, name, node_id, dictionary)
		self.raise_exception = False
		self.data = {}
		self.get_data = Mock(side_effect = self._sideeffect_get_data)
		self.set_data = Mock(side_effect = self._sideeffect_set_data)
	
	def _sideeffect_get_data(self, index, subindex):
		if self.raise_exception:
			raise Exception()
		else:
			return self.data[(index, subindex)]
	
	def _sideeffect_set_data(self, index, subindex, data):
		if self.raise_exception:
			raise Exception()
		else:
			self.data[(index, subindex)] = data
