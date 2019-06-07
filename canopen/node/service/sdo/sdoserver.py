import struct
import can
from canopen.node.service import Service
import canopen.objectdictionary


class SDOServer(Service):
	""" SDOServer server
	
	This class is an implementation of a SDO server. It handles requests for expedited and segmented uploads and downloads.
	Block upload and download is not implemented.
	Network indication is not implemented.
	"""
	def __init__(self):
		Service.__init__(self)
		
		self._state = 0x80
		self._toggle_bit = 0x00
		self._data_size = 0
		self._buffer = b""
		self._index = 0
		self._subindex = 0
	
	def attach(self, node):
		""" Attaches the service to a node. It does NOT append or assign this service to the node. """
		Service.attach(self, node)
		
		self._state = 0x80
		
		self._node.network.subscribe(self.on_request, 0x600 + self._node.id)
	
	def detach(self):
		""" Detaches the service from the node. It does NOT remove or delete the service from the node. """
		if self._node == None:
			raise RuntimeError()
		
		self._node.network.unsubscribe(self.on_request, 0x600 + self._node.id)
		Service.detach(self)
	
	def on_request(self, message):
		""" Handler for upload and download requests to the SDO server. """
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
		
		message = can.Message(arbitration_id = 0x580 + self._node.id, is_extended_id = False, data = struct.pack("<BHBL", 0x80, index, subindex, code))
		self._node.network.send(message)
	
	def _on_download_segment(self, message):
		request_command, request_data = struct.unpack_from("<B7s", message.data)
		
		if self._state != 0x20:
			# 0x05040001 Client/server command specifier not valid or unknown.
			self._abort(self._index, self._subindex, 0x05040001)
			return
	
		if self._toggle_bit != (request_command & (1 << 4)):
			# 0x05030000 Toggle bit not alternated.
			self._abort(self._index, self._subindex, 0x05030000)
			return
		
		size = 7 - ((request_command & 0x0E) >> 1)
		self._buffer = self._buffer + request_data[:size]
		
		if request_command & (1 << 0):
			# Check the size from initiate with size of buffer - maybe two segments got lost
			if self._data_size != len(self._buffer):
				# 0x06070010 Data type does not match; length of service parameter does not match.
				self._abort(self._index, self._subindex, 0x06070010)
				return
			
			# Try to get object dictionary item - the dictionary may have changed since initiate
			try:
				item = self._node.dictionary[self._index]
			except:
				# 0x06020000 Object does not exist in the object dictionary.
				self._abort(self._index, self._subindex, 0x06020000)
				return
			
			if not isinstance(item, canopen.objectdictionary.Variable):
				try:
					item = item[self._subindex]
				except:
					# 0x06090011 Sub-index does not exist.
					self._abort(self._index, self._subindex, 0x06090011)
					return
			
			try:
				data = item.decode(self._buffer)
				# TODO: Write data to node
				# self._node.set_data(self._index, self._subindex, data)
			except:
				# 0x06070010 Data type does not match; length of service parameter does not match.
				self._abort(self._index, self._subindex, 0x06070010)
				return
				
			self._state = 0x80
		
		response_command = 0x20 | self._toggle_bit
		response_data = b"\x00\x00\x00\x00\x00\x00\x00"
		d = struct.pack("<B7s", response_command, response_data)
		response = can.Message(arbitration_id = 0x580 + self._node.id, is_extended_id = False, data = d)
		self._node.network.send(response)
		
		self._toggle_bit ^= (1 << 4)
	
	def _on_initiate_download(self, message):
		request_command, index, subindex, request_data = struct.unpack("<BHB4s", message.data)
		
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
		
		if request_command & (1 << 1): # Expedited transfer
			self._state = 0x80
			
			if request_command & (1 << 0): # Size indicated
				size = 4 - ((request_command >> 2) & 0x03)
			else:
				size = 4
			
			try:
				data = item.decode(request_data[:size])
				# TODO: Write data to node
				# self._node.set_data(self._index, self._subindex, data
			except:
				# 0x06070010 Data type does not match; length of service parameter does not match.
				self._abort(index, subindex, 0x06070010)
				return
		else: # Segmented transfer
			if request_command & (1 << 0): # Size indicated
				self._state = 0x20
				self._toggle_bit = 0x00
				self._data_size = struct.unpack("<L", request_data)[0]
				self._buffer = b""
				self._index = index
				self._subindex = subindex
			else:
				# 0x05040001 Client/server command specifier not valid or unknown.
				self._abort(index, subindex, 0x05040001)
				return
		
		response_command = 0x60
		response_data = b"\x00\x00\x00\x00"
		d = struct.pack("<BHB4s", response_command, index, subindex, response_data)
		response = can.Message(arbitration_id = 0x580 + self._node.id, is_extended_id = False, data = d)
		self._node.network.send(response)
	
	def _on_initiate_upload(self, message):
		request_command, index, subindex, request_data = struct.unpack("<BHB4s", message.data)
		
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
		
		# TODO: Read data from node
		data = item.encode(0)
		
		size = len(data)
		
		if size > 0 and size <= 4: # Expedited transfer
			response_command = 0x40 | ((4 - size) << 2) | (1 << 1) | (1 << 0)
			response_data = data
			self._state = 0x80
		else: # Segmented transfer
			response_command = 0x40 | (1 << 0)
			response_data = struct.pack("<L", size)
			self._state = 0x40
			self._toggle_bit = 0x00
			self._data_size = size
			self._buffer = data
			self._index = index
			self._subindex = subindex
		
		d = struct.pack("<BHB4s", response_command, index, subindex, response_data)
		response = can.Message(arbitration_id = 0x580 + self._node.id, is_extended_id = False, data = d)
		self._node.network.send(response)
	
	def _on_upload_segment(self, message):
		request_command, request_data = struct.unpack_from("<B7s", message.data)
		
		if self._state != 0x40:
			# 0x05040001 Client/server command specifier not valid or unknown.
			self._abort(self._index, self._subindex, 0x05040001)
			return
	
		if self._toggle_bit != (request_command & (1 << 4)):
			# 0x05030000 Toggle bit not alternated.
			self._abort(self._index, self._subindex, 0x05030000)
			return
		
		size = len(self._buffer)
		
		if size > 7:
			response_command = 0x00 | self._toggle_bit
		else:
			response_command = 0x00 | self._toggle_bit | ((7 - size) << 1) | (1 << 0)
			self._state = 0x80

		response_data = self._buffer[:7]
		
		d = struct.pack("<B7s", response_command, response_data)
		response = can.Message(arbitration_id = 0x580 + self._node.id, is_extended_id = False, data = d)
		self._node.network.send(response)
		
		self._buffer = self._buffer[7:]
		
		self._toggle_bit ^= (1 << 4)
	
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
