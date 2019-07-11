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
		self._identifier_rx = 0x580 + self._node.id
		self._identifier_tx = 0x600 + self._node.id
		self._node.network.subscribe(self.on_response, self._identifier_rx)
	
	def detach(self):
		""" Detaches the service from the node. It does NOT remove or delete the service from the node. """
		if self._node == None:
			raise RuntimeError()
		self._node.network.unsubscribe(self.on_response, self._identifier_rx)
		Service.detach(self)

	def upload(self, index, subindex):
		item = self._node.dictionary[index]
		
		if not isinstance(item, canopen.objectdictionary.Variable):
			item = item[subindex]
		
		self._index = index
		self._subindex = subindex
		self._buffer = b""
		self._data_size = 0
		self._state = 0x40
		self._toggle_bit = 0x00
		
		request_command = 0x40
		request_data = b"\x00\x00\x00\x00"
		
		d = struct.pack("<BHB4s", request_command, index, subindex, request_data)
		request = can.Message(arbitration_id = self._identifier_tx, is_extended_id = False, data = d)
		self._node.network.send(request)
		
		# TODO: wait for response
	
	def download(self, index, subindex, value):
		item = self._node.dictionary[index]
		
		if not isinstance(item, canopen.objectdictionary.Variable):
			item = item[subindex]
		
		self._index = index
		self._subindex = subindex
		self._buffer = item.encode(value)
		self._data_size = len(self._buffer)
		
		if self._data_size > 0 and self._data_size <= 4: # Expedited transfer
			request_command = 0x20 | ((4 - self._data_size) << 2) | (1 << 1) | (1 << 0)
			request_data = self._buffer
		else: # Segmented transfer
			request_command = 0x20 | (1 << 0)
			request_data = struct.pack("<L", self._data_size)
			self._state = 0x20
			self._toggle_bit = 0x00
		
		d = struct.pack("<BHB4s", request_command, index, subindex, request_data)
		request = can.Message(arbitration_id = self._identifier_tx, is_extended_id = False, data = d)
		self._node.network.send(request)
		
		# TODO: wait for response
	
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
		
		message = can.Message(arbitration_id = self._identifier_tx, is_extended_id = False, data = struct.pack("<BHBL", 0x80, index, subindex, code))
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
		
	def _on_initiate_download(self, message):
		response_command, index, subindex, response_data = struct.unpack("<BHB4s", message.data)
		
		# TODO: Implement
	
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
