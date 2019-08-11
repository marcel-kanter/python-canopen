import struct
import can
import threading
from canopen.sdo.abortcodes import *
from canopen.node.service import Service
import canopen.objectdictionary


class SDOClient(Service):
	""" SDOClient
	
	This class is an implementation of a SDO client. It handles requests for expedited and segmented uploads and downloads.
	Block upload and download is not implemented.
	Network indication is not implemented.
	"""
	def __init__(self, timeout = 1):
		Service.__init__(self)
		self._state = 0x80
		self._toggle_bit = 0x00
		self._data_size = 0
		self._buffer = b""
		self._index = 0
		self._subindex = 0
		self._condition = threading.Condition()
		self._timeout = timeout
	
	def attach(self, node):
		""" Attaches the ``SDOClient`` to a ``Node``. It does NOT append or assign this ``SDOClient`` to the ``Node``. """
		Service.attach(self, node)
		self._state = 0x80
		self._identifier_rx = 0x580 + self._node.id
		self._identifier_tx = 0x600 + self._node.id
		self._node.network.subscribe(self.on_response, self._identifier_rx)
	
	def detach(self):
		""" Detaches the ``SDOClient`` from the ``Node``. It does NOT remove or delete the ``SDOClient`` from the ``Node``. """
		if self._node == None:
			raise RuntimeError()
		self._node.network.unsubscribe(self.on_response, self._identifier_rx)
		Service.detach(self)

	def upload(self, index, subindex):
		item = self._node.dictionary[index]
		
		if not isinstance(item, canopen.objectdictionary.Variable):
			item = item[subindex]
		
		self._condition.acquire()
		
		self._index = index
		self._subindex = subindex
		self._toggle_bit = 0x00
		self._buffer = b""
		
		request_command = 0x40
		request_data = b"\x00\x00\x00\x00"
		
		self._state = request_command
		
		d = struct.pack("<BHB4s", request_command, index, subindex, request_data)
		request = can.Message(arbitration_id = self._identifier_tx, is_extended_id = False, data = d)
		self._node.network.send(request)
		
		if not self._condition.wait(self._timeout):
			self._abort(index, subindex, SDO_PROTOCOL_TIMED_OUT)
			self._condition.release()
			raise TimeoutError()
		
		if self._state == 0x40:
			try:
				value = item.decode(self._buffer)
			except:
				# 0x06070010 Data type does not match; length of service parameter does not match.
				self._abort(self._index, self._subindex, 0x06070010)
				self._condition.release()
				raise Exception()
			
			self._state = 0x80
			self._condition.release()
			return value
		else:
			self._state = 0x80
			self._condition.release()
			raise Exception()
	
	def download(self, index, subindex, value):
		item = self._node.dictionary[index]
		
		if not isinstance(item, canopen.objectdictionary.Variable):
			item = item[subindex]
		
		self._condition.acquire()
		
		self._index = index
		self._subindex = subindex
		self._buffer = item.encode(value)
		self._data_size = len(self._buffer)
		self._toggle_bit = 0x00
		
		if self._data_size > 0 and self._data_size <= 4: # Expedited transfer
			request_command = 0x20 | ((4 - self._data_size) << 2) | (1 << 1) | (1 << 0)
			request_data = self._buffer
		else: # Segmented transfer
			request_command = 0x20 | (1 << 0)
			request_data = struct.pack("<L", self._data_size)
		
		self._state = request_command
		
		d = struct.pack("<BHB4s", request_command, index, subindex, request_data)
		request = can.Message(arbitration_id = self._identifier_tx, is_extended_id = False, data = d)
		self._node.network.send(request)
		
		if not self._condition.wait(self._timeout):
			self._abort(index, subindex, SDO_PROTOCOL_TIMED_OUT)
			self._condition.release()
			raise TimeoutError()
		
		if self._state & 0xE0 == 0x20:
			self._state = 0x80
			self._condition.release()
		else:
			self._state = 0x80
			self._condition.release()
			raise Exception()
	
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
		message = can.Message(arbitration_id = self._identifier_tx, is_extended_id = False, data = struct.pack("<BHBL", 0x80, index, subindex, code))
		self._node.network.send(message)
		
		self._state = 0x80
		self._condition.acquire()
		self._condition.notify(1)
		self._condition.release()

	def _on_upload_segment(self, message):
		response_command, response_data = struct.unpack_from("<B7s", message.data)
		
		if self._state != 0x40:
			self._abort(0, 0, COMMAND_SPECIFIER_NOT_VALID)
			return
		
		if self._toggle_bit != (response_command & (1 << 4)):
			self._abort(self._index, self._subindex, TOGGLE_BIT_NOT_ALTERNATED)
			return
		
		size = 7 - ((response_command & 0x0E) >> 1)
		self._buffer = self._buffer + response_data[:size]
		
		if response_command & (1 << 0): # Last segment
			# Check the size from initiate with size of buffer - maybe two segments got lost (which is not detectable with toggle bit alternation)
			if self._data_size != len(self._buffer):
				# 0x06070010 Data type does not match; length of service parameter does not match.
				self._abort(self._index, self._subindex, 0x06070010)
				return
			
			self._condition.acquire()
			self._condition.notify(1)
			self._condition.release()
		else:
			self._toggle_bit ^= (1 << 4)
			
			request_command = 0x60 | self._toggle_bit
			request_data = b"\x00\x00\x00\x00\x00\x00\x00"
			d = struct.pack("<B7s", request_command, request_data)
			request = can.Message(arbitration_id = self._identifier_tx, is_extended_id = False, data = d)
			self._node.network.send(request)
	
	def _on_download_segment(self, message):
		response_command, response_data = struct.unpack_from("<B7s", message.data)
		
		if self._state & 0xE0 != 0x20:
			self._abort(0, 0, COMMAND_SPECIFIER_NOT_VALID)
			return
		
		if self._toggle_bit != (response_command & (1 << 4)):
			self._abort(self._index, self._subindex, TOGGLE_BIT_NOT_ALTERNATED)
			return
		
		size = len(self._buffer)
		
		if size == 0:
			self._condition.acquire()
			self._condition.notify(1)
			self._condition.release()
		else:
			self._toggle_bit ^= (1 << 4)
			if size > 7:
				request_command = 0x00 | self._toggle_bit
			else:
				request_command = 0x00 | self._toggle_bit | ((7 - size) << 1) | (1 << 0)
				
			request_data = self._buffer[:7]
			
			d = struct.pack("<B7s", request_command, request_data)
			request = can.Message(arbitration_id = self._identifier_tx, is_extended_id = False, data = d)
			self._node.network.send(request)
		
			self._buffer = self._buffer[7:]
	
	def _on_initiate_upload(self, message):
		response_command, index, subindex, response_data = struct.unpack("<BHB4s", message.data)
		
		if self._state != 0x40:
			self._abort(index, subindex, COMMAND_SPECIFIER_NOT_VALID)
			return
		
		# The server responds with differend index or subindex
		if self._index != index or self._subindex != subindex:
			self._abort(index, subindex, GENERAL_ERROR)
			return
		
		if response_command & (1 << 1): # expedited transfer
			if response_command & (1 << 0): # Size indicated
				size = 4 - ((response_command >> 2) & 0x03)
			else:
				size = 4
			
			self._buffer = response_data[:size]
			self._data_size = size
			
			self._condition.acquire()
			self._condition.notify(1)
			self._condition.release()
		else:
			if response_command & (1 << 0): # size indicated
				self._buffer = b""
				self._data_size, = struct.unpack("<L", response_data)
				
				request_command = 0x60 | self._toggle_bit
				request_data = b"\x00\x00\x00\x00\x00\x00\x00"
				d = struct.pack("<B7s", request_command, request_data)
				request = can.Message(arbitration_id = self._identifier_tx, is_extended_id = False, data = d)
				self._node.network.send(request)
			else:
				self._abort(index, subindex, COMMAND_SPECIFIER_NOT_VALID)
				return
		
	def _on_initiate_download(self, message):
		response_command, index, subindex, response_data = struct.unpack("<BHB4s", message.data)
		
		if self._state & 0xE0 != 0x20:
			self._abort(index, subindex, COMMAND_SPECIFIER_NOT_VALID)
			return
		
		# The server responds with differend index or subindex
		if self._index != index or self._subindex != subindex:
			self._abort(index, subindex, GENERAL_ERROR)
			return
		
		if self._state & (1 << 1): # Expedited transfer
			self._condition.acquire()
			self._condition.notify(1)
			self._condition.release()
		else: # Segmented transfer
			size = len(self._buffer)
		
			if size > 7:
				request_command = 0x00 | self._toggle_bit
			else:
				request_command = 0x00 | self._toggle_bit | ((7 - size) << 1) | (1 << 0)
				
			request_data = self._buffer[:7]
			
			d = struct.pack("<B7s", request_command, request_data)
			request = can.Message(arbitration_id = self._identifier_tx, is_extended_id = False, data = d)
			self._node.network.send(request)
		
			self._buffer = self._buffer[7:]
	
	def _on_abort(self, message):
		self._state = 0x80
		
		self._condition.acquire()
		self._condition.notify(1)
		self._condition.release()
	
	def _on_block_upload(self, message):
		self._abort(0, 0, COMMAND_SPECIFIER_NOT_VALID)
	
	def _on_block_download(self, message):
		self._abort(0, 0, COMMAND_SPECIFIER_NOT_VALID)
	
	def _on_network_indication(self, message):
		self._abort(0, 0, COMMAND_SPECIFIER_NOT_VALID)
	
	@property
	def timeout(self):
		return self._timeout
	
	@timeout.setter
	def timeout(self, x):
		if x != None and x <= 0:
			raise ValueError()
		self._timeout = x
