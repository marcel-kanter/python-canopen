"""
SDO Abort Error Codes:
0x05030000 Toggle bit not alternated.
0x05040000 SDO protocol timed out.
0x05040001 Client/server command specifier not valid or unknown.
0x05040002 Invalid block size (block mode only).
0x05040003 Invalid sequence number (block mode only).
0x05040004 CRC error (block mode only).
0x05040005 Out of memory.
0x06010000 Unsupported access to an object.
0x06010001 Attempt to read a write only object.
0x06010002 Attempt to write a read only object.
0x06020000 Object does not exist in the object dictionary.
0x06040041 Object cannot be mapped to the PDO.
0x06040042 The number and length of the objects to be mapped would exceed PDO length.
0x06040043 General parameter incompatibility reason.
0x06040047 General internal incompatibility in the device.
0x06060000 Access failed due to a hardware error.
0x06070010 Data type does not match; length of service parameter does not match.
0x06070012 Data type does not match; length of service parameter too high.
0x06070013 Data type does not match; length of service parameter too low.
0x06090011 Sub-index does not exist.
0x06090030 Value range of parameter exceeded (download only).
0x06090031 Value of parameter written too high (download only).
0x06090032 Value of parameter written too low (download only).
0x06090036 Maximum value is less than minimum value.
0x060A0023 Resource not available: SDO connection
0x08000000 General error.
0x08000020 Data cannot be transferred or stored to the application.
0x08000021 Data cannot be transferred or stored to the application because of local control.
0x08000022 Data cannot be transferred or stored to the application because of the present device state.
0x08000023 Object dictionary dynamic generation fails or no object dictionary is present.
0x08000024 No data available.
"""

NO_ERROR = 0x00000000

TOGGLE_BIT_NOT_ALTERNATED = 0x05030000
SDO_PROTOCOL_TIMED_OUT = 0x05040000
COMMAND_SPECIFIER_NOT_VALID = 0x05040001
INVALID_BLOCK_SIZE = 0x05040002
INVALID_SEQUENCE_NUMBER = 0x05040003
CRC_ERROR = 0x05040004
OUT_OF_MEMORY = 0x05040005
UNSUPPORTED_ACCESS = 0x06010000

OBJECT_DOES_NOT_EXIST = 0x06020000

LENGTH_DOES_NOT_MATCH = 0x06070010
LENGTH_TOO_HIGH = 0x06070012
LENGTH_TOO_LOW = 0x06070013

SUBINDEX_DOES_NOT_EXIST = 0x06090011
VALUE_RANGE_EXCEEDED = 0x06090030
VALUE_TOO_HIGH = 0x06090031
VALUE_TOO_LOW = 0x06090032
MAXIMUM_LESS_THAN_MINIMUM = 0x06090036

GENERAL_ERROR = 0x08000000

NO_DATA_AVAILABLE = 0x08000024
