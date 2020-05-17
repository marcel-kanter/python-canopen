from canopen.exception import CANopenError


class SDOAbortError(CANopenError):
	def __init__(self, code):
		"""
		:param code: An integer. The abort code of this exception.
		"""
		CANopenError.__init__(self)
		self.code = code
