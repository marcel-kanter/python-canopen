import struct
import can
from .service import Service
import canopen.objectdictionary


class SDOServer(Service):
	def __init__(self):
		Service.__init__(self)
		
		self._state = 0x80
		self._index = 0
		self._subindex = 0
		self._buffer = b""
	
	def attach(self, node):
		Service.attach(self, node)
		
		self._state = 0x80
		self._index = 0
		self._subindex = 0
		self._buffer = b""
		
		self._node.network.subscribe(self.on_request, 0x600 + self._node.id)
	
	def detach(self):
		if self._node == None:
			raise RuntimeError()
		
		self._node.network.unsubscribe(self.on_request, 0x600 + self._node.id)
		Service.detach(self)
	
	def on_request(self, message):
		if message.dlc != 8:
			return
		
		command = message.data[0] & 0xE0
		if command == 0x00: # Download segment
			self._on_download_segment(message)
		if command == 0x20: # Initiate download
			self._on_initiate_download(message)
		if command == 0x40: # Initiate upload
			self._on_initiate_upload(message)
		if command == 0x60: # Upload segment
			self._on_upload_segment(message)
		if command == 0x80: # Abort transfer
			self._on_abort(message)
		if command == 0xA0: # Block upload
			self._on_block_upload(message)
		if command == 0xC0: # Block download
			self._on_block_download(message)
		if command == 0xE0: # Network indication
			self._on_network_indication(message)
	
	def _abort(self, index, subindex, code):
		self._state = 0x80
		self._index = 0
		self._subindex = 0
		self._buffer = b""
		
		message = can.Message(arbitration_id = 0x580 + self._node.id, is_extended_id = False, data = struct.pack("<BHBL", 0x80, index, subindex, code))
		self._node.network.send(message)
	
	def _on_download_segment(self, message):
		command, request_data = struct.unpack_from("<B7s", message.data)
		
		if self._state != 0x20:
			# 0x05040001 Client/server command specifier not valid or unknown.
			self._abort(self._index, self._subindex, 0x05040001)
	
	def _on_initiate_download(self, message):
		command, index, subindex, request_data = struct.unpack("<BHB4s", message.data)
		
		try:
			item = self._node.dictionary[index]
		except:
			# 0x06020000 Object does not exist in the object dictionary.
			self._abort(index, subindex, 0x06020000)
			return
		
		if not isinstance(item, canopen.objectdictionary.Variable):
			try:
				item = item[subindex]
			except:
				# 0x06090011 Sub-index does not exist.
				self._abort(index, subindex, 0x06090011)
				return
		
		if "w" not in item.access_type:
			# 0x06010002 Attempt to write a read only object.
			self._abort(index, subindex, 0x06010002)
			return
		
		if command & (1 << 1): # Expedited transfer
			self._state = 0x80
		else: # Segmented transfer
			self._state = 0x20
			self._index = index
			self._subindex = subindex
			self._buffer = b""
	
	def _on_initiate_upload(self, message):
		command, index, subindex, request_data = struct.unpack("<BHB4s", message.data)
		
		try:
			item = self._node.dictionary[index]
		except:
			# 0x06020000 Object does not exist in the object dictionary.
			self._abort(index, subindex, 0x06020000)
			return
		
		if not isinstance(item, canopen.objectdictionary.Variable):
			try:
				item = item[subindex]
			except:
				# 0x06090011 Sub-index does not exist.
				self._abort(index, subindex, 0x06090011)
				return
		
		if "r" not in item.access_type:
			# 0x06010001 Attempt to read a write only object.
			self._abort(index, subindex, 0x06010001)
			return
		
		if command & (1 << 1): # Expedited transfer
			self._state = 0x80
		else: # Segmented transfer
			self._state = 0x40
			self._index = index
			self._subindex = subindex
			self._buffer = b""
	
	def _on_upload_segment(self, message):
		command, request_data = struct.unpack_from("<B7s", message.data)
		
		if self._state != 0x40:
			# 0x05040001 Client/server command specifier not valid or unknown.
			self._abort(self._index, self._subindex, 0x05040001)
	
	def _on_abort(self, message):
		command, index, subindex, code = struct.unpack("<BHBL", message.data)
		
		self._state = 0x80
		self._index = 0
		self._subindex = 0
		self._buffer = b""
	
	def _on_block_upload(self, message):
		# 0x05040001 Client/server command specifier not valid or unknown.
		self._abort(0, 0, 0x05040001)
	
	def _on_block_download(self, message):
		# 0x05040001 Client/server command specifier not valid or unknown.
		self._abort(0, 0, 0x05040001)
	
	def _on_network_indication(self, message):
		# 0x05040001 Client/server command specifier not valid or unknown.
		self._abort(0, 0, 0x05040001)
