import struct
import calendar
from .datatypes import *


class Variable(object):
	"""	This class is the representation of a Variable in an object dictionary.
	"""
	
	_canopen_epoch = calendar.timegm((1984, 1, 1, 0, 0, 0))
	
	def __init__(self, name, index, subindex, data_type, access_type = "rw"):
		allowed_types = [BOOLEAN, INTEGER8, INTEGER16, INTEGER32, UNSIGNED8, UNSIGNED16, UNSIGNED32, REAL32, VISIBLE_STRING, OCTET_STRING, UNICODE_STRING, TIME_OF_DAY, TIME_DIFFERENCE, DOMAIN, INTEGER24, REAL64, INTEGER40, INTEGER48, INTEGER56, INTEGER64, UNSIGNED24, UNSIGNED40, UNSIGNED48, UNSIGNED56, UNSIGNED64]
		
		if index < 0 or index > 65535:
			raise ValueError()
		if subindex < 0 or subindex > 255:
			raise ValueError()
		if data_type not in allowed_types:
			raise ValueError()
		if access_type not in ["rw", "wo", "ro"]:
			raise ValueError()
		
		self._object_type = 7
		self._name = str(name)
		self._index = index
		self._subindex = subindex
		self._data_type = data_type
		self._access_type = access_type
		
		if self._data_type == BOOLEAN:
			self._default = False
		elif self._data_type in [REAL32, REAL64]:
			self._default = 0.0	
		elif self._data_type in [VISIBLE_STRING, OCTET_STRING, UNICODE_STRING]:
			self._default = ""
		elif self._data_type == DOMAIN:
			self._default = b""
		elif self._data_type == TIME_OF_DAY:
			self._default = self._canopen_epoch
		else:
			self._default = 0
	
	def __eq__(self, other):
		""" Indicates whether some other object is "equal to" this one. """
		if self is other:
			return True
		if self.__class__ != other.__class__:
			return False
		if self._name != other._name or self._index != other.index or self._subindex != other.subindex or self._data_type != other.data_type or self._access_type != other.access_type or self._default != other.default:
			return False
		return True
	
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
			
			if self._data_type == TIME_OF_DAY:
				m, d = struct.unpack_from("<LH", data)
				m &= 0xFFFFFFF
				value = d * 24 * 60 * 60 + m / 1000 + self._canopen_epoch
			
			if self._data_type == TIME_DIFFERENCE:
				m, d = struct.unpack_from("<LH", data)
				m &= 0xFFFFFFF
				value = d * 24 * 60 * 60 + m / 1000
			
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
			
			if self._data_type == TIME_OF_DAY:
				if value < self._canopen_epoch:
					raise ValueError()
				x = divmod(value - self._canopen_epoch, 24 * 60 * 60)
				d = int(x[0])
				m = round(x[1] * 1000)
				data = struct.pack("<LH", m, d)
			
			if self._data_type == TIME_DIFFERENCE:
				if value < 0:
					raise ValueError()
				x = divmod(value, 24 * 60 * 60)
				d = int(x[0])
				m = round(x[1] * 1000)
				data = struct.pack("<LH", m, d)
			
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
		
		return data
	
	@property
	def object_type(self):
		"""
		Returns the object type as defined in DS301 v4.02 Table 42: Object code usage.
		"""
		return self._object_type
	
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
		"""
		Returns the data type as defined in DS301 v4.02 Table 44: Object dictionary data types.
		"""
		return self._data_type
	
	@property
	def access_type(self):
		"""
		Returns the access type as defined in DS301 v4.02 Table 43: Access attributes for data objects.
		"""
		return self._access_type
	
	@access_type.setter
	def access_type(self, x):
		if x not in ["rw", "wo", "ro"]:
			raise ValueError()
		self._access_type = x
	
	@property
	def default(self):
		"""
		Returns the default value for this Variable.
		"""
		return self._default
	
	@default.setter
	def default(self, x):
		self._default = x
