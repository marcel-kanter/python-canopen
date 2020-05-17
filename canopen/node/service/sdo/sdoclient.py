import struct
import can
import threading

from canopen.node.service import Service
from canopen.sdo.abortcodes import TOGGLE_BIT_NOT_ALTERNATED, SDO_PROTOCOL_TIMED_OUT, COMMAND_SPECIFIER_NOT_VALID, GENERAL_ERROR, LENGTH_DOES_NOT_MATCH
from canopen.sdo.exception import SDOAbortError
from canopen.objectdictionary import Variable


class SDOClient(Service):
	""" SDOClient
	
	This class is an implementation of a SDO client. It handles requests for expedited and segmented uploads and downloads.
	Block upload and download is not implemented.
	Network indication is not implemented.
	"""
	def __init__(self, node, timeout = 1):
		""" Initializes the service
		
		:param node: The node, to which this service belongs to.
			Must be of type canopen.node.Node
		
		:raises: TypeError
		"""
		Service.__init__(self, node)
		self._cob_id_rx = None
		self._cob_id_tx = None
		
		self._state = 0x80
		self._toggle_bit = 0x00
		self._data_size = 0
		self._buffer = b""
		self._index = 0
		self._subindex = 0
		self._condition = threading.Condition()
		self._timeout = float(timeout)
	
	def attach(self, cob_id_rx = None, cob_id_tx = None):
		""" Attach handler. Must be called when the node gets attached to the network.
		
		:param cob_id_rx: The COB ID for the SDO service, used for the CAN ID of the SDO messages to be received.
			Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			If it is omitted or None is passed, the value defaults to 0x580 + node.id .

		:param cob_id_tx: The COB ID for the SDO service, used for the CAN ID of the SDO messages to be sent.
			Bit 29 selects whether an extended frame is used. The CAN ID is masked out of the lowest 11 or 29 bits.
			If it is omitted or None is passed, the value defaults to 0x600 + node.id .

		:raises: ValueError
		"""
		if cob_id_rx == None:
			cob_id_rx = 0x580 + self._node.id
		if cob_id_rx < 0 or cob_id_rx > 0xFFFFFFFF:
			raise ValueError()
		if cob_id_tx == None:
			cob_id_tx = 0x600 + self._node.id
		if cob_id_tx < 0 or cob_id_tx > 0xFFFFFFFF:
			raise ValueError()
		if self.is_attached():
			self.detach()
		
		self._state = 0x80
		
		if cob_id_rx & (1 << 29):
			self._node.network.subscribe(self.on_response, cob_id_rx & 0x1FFFFFFF)
		else:
			self._node.network.subscribe(self.on_response, cob_id_rx & 0x7FF)
		
		self._cob_id_rx = int(cob_id_rx)
		self._cob_id_tx = int(cob_id_tx)
	
	def detach(self):
		""" Detach handler. Must be called when the node gets detached from the network.
		Raises RuntimeError if not attached.
		
		:raises: RuntimeError
		"""
		if not self.is_attached():
			raise RuntimeError()
		
		if self._cob_id_rx & (1 << 29):
			self._node.network.unsubscribe(self.on_response, self._cob_id_rx & 0x1FFFFFFF)
		else:
			self._node.network.unsubscribe(self.on_response, self._cob_id_rx & 0x7FF)
		
		self._cob_id_rx = None
		self._cob_id_tx = None
		
	def is_attached(self):
		""" Returns True if the service is attached.
		"""
		return self._cob_id_rx != None
	
	def upload(self, index, subindex):
		"""
		:param index: An integer. Range 0x0000 ... 0xFFFF. The object index
		
		:param subindex: An integer. Range 0x00 ... 0xFF. The object subindex.
		
		:raises: TimeoutError, SDOAbortError
		"""
		item = self._node.dictionary[index]
		
		if not isinstance(item, Variable):
			item = item[subindex]
		
		with self._condition:
			self._index = index
			self._subindex = subindex
			self._toggle_bit = 0x00
			self._buffer = b""
			
			request_command = 0x40
			request_data = b"\x00\x00\x00\x00"
			
			self._state = request_command
			
			d = struct.pack("<BHB4s", request_command, index, subindex, request_data)
			if self._cob_id_tx & (1 << 29):
				request = can.Message(arbitration_id = self._cob_id_tx & 0x1FFFFFFF, is_extended_id = True, data = d)
			else:
				request = can.Message(arbitration_id = self._cob_id_tx & 0x7FF, is_extended_id = False, data = d)
			self._node.network.send(request)
			
			if not self._condition.wait(self._timeout):
				self._abort(index, subindex, SDO_PROTOCOL_TIMED_OUT)
				raise TimeoutError()
			
			if self._state == 0x40:
				try:
					value = item.decode(self._buffer)
				except:
					self._abort(self._index, self._subindex, LENGTH_DOES_NOT_MATCH)
					raise SDOAbortError(LENGTH_DOES_NOT_MATCH)
				
				self._state = 0x80
				return value
			else:
				self._state = 0x80
				#TODO: Get specific exception from lower half.
				raise SDOAbortError(GENERAL_ERROR)
	
	def download(self, index, subindex, value):
		"""
		:param index: An integer. Range 0x0000 ... 0xFFFF. The object index
		
		:param subindex: An integer. Range 0x00 ... 0xFF. The object subindex.
		
		:param value: An object. The data to write
		
		:raises: TimeoutError, SDOAbortError
		"""
		item = self._node.dictionary[index]
		
		if not isinstance(item, Variable):
			item = item[subindex]
		
		with self._condition:
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
			if self._cob_id_tx & (1 << 29):
				request = can.Message(arbitration_id = self._cob_id_tx & 0x1FFFFFFF, is_extended_id = True, data = d)
			else:
				request = can.Message(arbitration_id = self._cob_id_tx & 0x7FF, is_extended_id = False, data = d)
			self._node.network.send(request)
			
			if not self._condition.wait(self._timeout):
				self._abort(index, subindex, SDO_PROTOCOL_TIMED_OUT)
				raise TimeoutError()
			
			if self._state & 0xE0 != 0x20:
				self._state = 0x80
				#TODO: Get specific exception from lower half.
				raise SDOAbortError(GENERAL_ERROR)
			self._state = 0x80
	
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
		d = struct.pack("<BHBL", 0x80, index, subindex, code)
		if self._cob_id_tx & (1 << 29):
			message = can.Message(arbitration_id = self._cob_id_tx & 0x1FFFFFFF, is_extended_id = True, data = d)
		else:
			message = can.Message(arbitration_id = self._cob_id_tx & 0x7FF, is_extended_id = False, data = d)
		self._node.network.send(message)
		
		self._state = 0x80
		with self._condition:
			self._condition.notify_all()
	
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
			
			with self._condition:
				self._condition.notify_all()
		else:
			self._toggle_bit ^= (1 << 4)
			
			request_command = 0x60 | self._toggle_bit
			request_data = b"\x00\x00\x00\x00\x00\x00\x00"
			d = struct.pack("<B7s", request_command, request_data)
			if self._cob_id_tx & (1 << 29):
				request = can.Message(arbitration_id = self._cob_id_tx & 0x1FFFFFFF, is_extended_id = True, data = d)
			else:
				request = can.Message(arbitration_id = self._cob_id_tx & 0x7FF, is_extended_id = False, data = d)
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
			with self._condition:
				self._condition.notify_all()
		else:
			self._toggle_bit ^= (1 << 4)
			if size > 7:
				request_command = 0x00 | self._toggle_bit
			else:
				request_command = 0x00 | self._toggle_bit | ((7 - size) << 1) | (1 << 0)
			
			request_data = self._buffer[:7]
			
			d = struct.pack("<B7s", request_command, request_data)
			if self._cob_id_tx & (1 << 29):
				request = can.Message(arbitration_id = self._cob_id_tx & 0x1FFFFFFF, is_extended_id = True, data = d)
			else:
				request = can.Message(arbitration_id = self._cob_id_tx & 0x7FF, is_extended_id = False, data = d)
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
			
			with self._condition:
				self._condition.notify_all()
		else:
			if response_command & (1 << 0): # size indicated
				self._buffer = b""
				self._data_size, = struct.unpack("<L", response_data)
				
				request_command = 0x60 | self._toggle_bit
				request_data = b"\x00\x00\x00\x00\x00\x00\x00"
				d = struct.pack("<B7s", request_command, request_data)
				if self._cob_id_tx & (1 << 29):
					request = can.Message(arbitration_id = self._cob_id_tx & 0x1FFFFFFF, is_extended_id = True, data = d)
				else:
					request = can.Message(arbitration_id = self._cob_id_tx & 0x7FF, is_extended_id = False, data = d)
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
			with self._condition:
				self._condition.notify_all()
		else: # Segmented transfer
			size = len(self._buffer)
		
			if size > 7:
				request_command = 0x00 | self._toggle_bit
			else:
				request_command = 0x00 | self._toggle_bit | ((7 - size) << 1) | (1 << 0)
				
			request_data = self._buffer[:7]
			
			d = struct.pack("<B7s", request_command, request_data)
			if self._cob_id_tx & (1 << 29):
				request = can.Message(arbitration_id = self._cob_id_tx & 0x1FFFFFFF, is_extended_id = True, data = d)
			else:
				request = can.Message(arbitration_id = self._cob_id_tx & 0x7FF, is_extended_id = False, data = d)
			self._node.network.send(request)
		
			self._buffer = self._buffer[7:]
	
	def _on_abort(self, message):
		self._state = 0x80
		
		with self._condition:
			self._condition.notify_all()
	
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
