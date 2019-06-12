import struct
import can
from canopen.node.service import Service
import canopen.objectdictionary


class SDOClient(Service):
	""" SDOClient
	
	This class is an implementation of a SDO client. It handles requests for expedited and segmented uploads and downloads.
	Block upload and download is not implemented.
	Network indication is not implemented.
	"""
	def __init__(self):
		Service.__init__(self)
		self._state = 0x80
	
	def attach(self, node):
		""" Attaches the service to a node. It does NOT append or assign this service to the node. """
		Service.attach(self, node)
		self._state = 0x80
		self._node.network.subscribe(self.on_response, 0x580 + self._node.id)
	
	def detach(self):
		""" Detaches the service from the node. It does NOT remove or delete the service from the node. """
		if self._node == None:
			raise RuntimeError()
		
		self._node.network.unsubscribe(self.on_response, 0x580 + self._node.id)
		Service.detach(self)

	def on_response(self, message):
		""" Handler for upload and download responses from the SDO server. """
		if message.dlc != 8:
			return
		
		command = message.data[0] & 0xE0
		if command == 0x00: # Upload segment
			self._on_upload_segment(message)
		if command == 0x20: # Download segment
			self._on_download_segment(message)
		if command == 0x40: # Initiate upload
			self._on_initiate_upload(message)
		if command == 0x60: # Initiate download
			self._on_initiate_download(message)
		if command == 0x80: # Abort transfer
			self._on_abort(message)
		if command == 0xA0: # Block download
			self._on_block_download(message)
		if command == 0xC0: # Block upload
			self._on_block_upload(message)
		if command == 0xE0: # Network indication
			self._on_network_indication(message)
	
	def _abort(self, index, subindex, code):
		self._state = 0x80
		
		message = can.Message(arbitration_id = 0x600 + self._node.id, is_extended_id = False, data = struct.pack("<BHBL", 0x80, index, subindex, code))
		self._node.network.send(message)

	def _on_upload_segment(self, message):
		response_command, response_data = struct.unpack_from("<B7s", message.data)
		
		# TODO: Implement
		# 0x05040001 Client/server command specifier not valid or unknown.
		self._abort(0, 0, 0x05040001)
	
	def _on_download_segment(self, message):
		response_command, response_data = struct.unpack_from("<B7s", message.data)

		# TODO: Implement		
		# 0x05040001 Client/server command specifier not valid or unknown.
		self._abort(0, 0, 0x05040001)
	
	def _on_initiate_upload(self, message):
		response_command, index, subindex, response_data = struct.unpack("<BHB4s", message.data)
		
		# TODO: Implement
		# 0x05040001 Client/server command specifier not valid or unknown.
		self._abort(0, 0, 0x05040001)
		
	def _on_initiate_download(self, message):
		response_command, index, subindex, response_data = struct.unpack("<BHB4s", message.data)
		
		# TODO: Implement
		# 0x05040001 Client/server command specifier not valid or unknown.
		self._abort(0, 0, 0x05040001)
	
	def _on_abort(self, message):
		self._state = 0x80
	
	def _on_block_upload(self, message):
		# 0x05040001 Client/server command specifier not valid or unknown.
		self._abort(0, 0, 0x05040001)
	
	def _on_block_download(self, message):
		# 0x05040001 Client/server command specifier not valid or unknown.
		self._abort(0, 0, 0x05040001)
	
	def _on_network_indication(self, message):
		# 0x05040001 Client/server command specifier not valid or unknown.
		self._abort(0, 0, 0x05040001)
