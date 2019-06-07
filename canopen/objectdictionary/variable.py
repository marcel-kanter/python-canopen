import struct
from .datatypes import *


class Variable(object):
	def __init__(self, name, index, subindex, data_type, access_type = "rw"):
		allowed_types = [BOOLEAN, INTEGER8, INTEGER16, INTEGER32, UNSIGNED8, UNSIGNED16, UNSIGNED32, REAL32, VISIBLE_STRING, OCTET_STRING, UNICODE_STRING, TIME_OF_DAY, TIME_DIFFERENCE, DOMAIN, INTEGER24, REAL64, INTEGER40, INTEGER48, INTEGER56, INTEGER64, UNSIGNED24, UNSIGNED40, UNSIGNED48, UNSIGNED56, UNSIGNED64]
		
		if index < 0 or index > 65535:
			raise ValueError()
		if subindex < 0 or subindex > 255:
			raise ValueError()
		if data_type not in allowed_types:
			raise ValueError()
		if access_type not in ["r", "w", "rw"]:
			raise ValueError()
		
		self._name = str(name)
		self._index = index
		self._subindex = subindex
		self._data_type = data_type
		self._access_type = access_type
	
	def decode(self, data):
		""" Returns the value for the given byte-like CANopen representation, depending on the type of the CANopen variable. """
		value = None
		
		try:
			if self._data_type == BOOLEAN:
				value, = struct.unpack_from("<?", data)
			
			if self._data_type == INTEGER8:
				value, = struct.unpack_from("<b", data)
			
			if self._data_type == INTEGER16:
				value, = struct.unpack_from("<h", data)
			
			if self._data_type == INTEGER32:
				value, = struct.unpack_from("<l", data)
			
			if self._data_type == UNSIGNED8:
				value, = struct.unpack_from("<B", data)
			
			if self._data_type == UNSIGNED16:
				value, = struct.unpack_from("<H", data)
			
			if self._data_type == UNSIGNED32:
				value, = struct.unpack_from("<L", data)
			
			if self._data_type == REAL32:
				value, = struct.unpack_from("<f", data)
			
			if self._data_type == VISIBLE_STRING:
				value = bytes.decode(data, "ascii", errors = "replace")
			
			if self._data_type == OCTET_STRING:
				value = bytes.decode(data, "utf-8", errors = "replace")
			
			if self._data_type == UNICODE_STRING:
				value = bytes.decode(data, "utf-16-le", errors = "replace")
			
			if self._data_type == DOMAIN:
				value = data
			
			if self._data_type == INTEGER24:
				if len(data) < 3:
					raise ValueError()
				value = int.from_bytes(data[0:3], "little", signed = True)
			
			if self._data_type == REAL64:
				value, = struct.unpack_from("<q", data)
			
			if self._data_type == INTEGER40:
				if len(data) < 5:
					raise ValueError()
				value = int.from_bytes(data[0:5], "little", signed = True)
			
			if self._data_type == INTEGER48:
				if len(data) < 6:
					raise ValueError()
				value = int.from_bytes(data[0:6], "little", signed = True)
			
			if self._data_type == INTEGER56:
				if len(data) < 7:
					raise ValueError()
				value = int.from_bytes(data[0:7], "little", signed = True)
			
			if self._data_type == INTEGER64:
				value, = struct.unpack_from("<q", data)
			
			if self._data_type == UNSIGNED24:
				if len(data) < 3:
					raise ValueError()
				value = int.from_bytes(data[0:3], "little", signed = False)
			
			if self._data_type == UNSIGNED40:
				if len(data) < 5:
					raise ValueError()
				value = int.from_bytes(data[0:5], "little", signed = False)
			
			if self._data_type == UNSIGNED48:
				if len(data) < 6:
					raise ValueError()
				value = int.from_bytes(data[0:6], "little", signed = False)
			
			if self._data_type == UNSIGNED56:
				if len(data) < 7:
					raise ValueError()
				value = int.from_bytes(data[0:7], "little", signed = False)
			
			if self._data_type == UNSIGNED64:
				value, = struct.unpack_from("<Q", data)
		except:
			raise ValueError()
		
		if self._data_type == TIME_OF_DAY:
			raise NotImplementedError()
		
		if self._data_type == TIME_DIFFERENCE:
			raise NotImplementedError()
		
		return value
	
	def encode(self, value):
		""" Returns the byte-like CANopen representation of the given value, depending on the type of the CANopen variable. """
		data = None
		
		try:
			if self._data_type == BOOLEAN:
				data = struct.pack("?", value)
			
			if self._data_type == INTEGER8:
				data = struct.pack("<b", value)
			
			if self._data_type == INTEGER16:
				data = struct.pack("<h", value)
			
			if self._data_type == INTEGER32:
				data = struct.pack("<l", value)
			
			if self._data_type == UNSIGNED8:
				data = struct.pack("<B", value)
			
			if self._data_type == UNSIGNED16:
				data = struct.pack("<H", value)
			
			if self._data_type == UNSIGNED32:
				data = struct.pack("<L", value)
			
			if self._data_type == REAL32:
				data = struct.pack("<f", value)
			
			if self._data_type == VISIBLE_STRING:
				data = str.encode(value, "ascii")
			
			if self._data_type == OCTET_STRING:
				data = str.encode(value, "utf-8")
			
			if self._data_type == UNICODE_STRING:
				data = str.encode(value, "utf-16-le")
			
			if self._data_type == DOMAIN:
				data = bytes(value)
			
			if self._data_type == INTEGER24:
				data = int.to_bytes(value, 3, "little", signed = True)
			
			if self._data_type == REAL64:
				data = struct.pack("<d", value)
			
			if self._data_type == INTEGER40:
				data = int.to_bytes(value, 5, "little", signed = True)
			
			if self._data_type == INTEGER48:
				data = int.to_bytes(value, 6, "little", signed = True)
			
			if self._data_type == INTEGER56:
				data = int.to_bytes(value, 7, "little", signed = True)
			
			if self._data_type == INTEGER64:
				data = struct.pack("<q", value)
			
			if self._data_type == UNSIGNED24:
				data = int.to_bytes(value, 3, "little", signed = False)
			
			if self._data_type == UNSIGNED40:
				data = int.to_bytes(value, 5, "little", signed = False)
			
			if self._data_type == UNSIGNED48:
				data = int.to_bytes(value, 6, "little", signed = False)
			
			if self._data_type == UNSIGNED56:
				data = int.to_bytes(value, 7, "little", signed = False)
			
			if self._data_type == UNSIGNED64:
				data = struct.pack("<Q", value)
		except:
			raise ValueError()
		
		if self._data_type == TIME_OF_DAY:
			raise NotImplementedError()
		
		if self._data_type == TIME_DIFFERENCE:
			raise NotImplementedError()
		
		return data
	
	@property
	def index(self):
		return self._index
	
	@property
	def name(self):
		return self._name
	
	@property
	def subindex(self):
		return self._subindex
	
	@property
	def data_type(self):
		return self._data_type
	
	@property
	def access_type(self):
		return self._access_type
