"""CANopen stuff"""

from enum import IntEnum, unique


@unique
class EmcyCode(IntEnum):
    """EMCY error codes from CiA 301."""

    ERROR_RESET = 0x0000
    """Error reset or no error."""
    GENERIC = 0x1000
    """Generic error."""
    CURRENT_GENERIC = 0x2000
    """Current - generic error."""
    CURRENT_DEVICE_INPUT = 0x2100
    """Current, CANopen device input side - generic."""
    CURRENT_DEVICE_INSIDE = 0x2200
    """Current, inside the CANopen device - generic."""
    CURRENT_DEVICE_OUTPUT = 0x2300
    """Current, CANopen device output side - generic."""
    VOLTAGE_GENERIC = 0x3000
    """Voltage - generic error."""
    VOLTAGE_MAINS = 0x3100
    """Mains voltage - generic."""
    VOLTAGE_DEVICE_INSIDE = 0x3200
    """Voltage inside the CANopen deivce - generic."""
    VOLTAGE_DEVICE_OUTPUT = 0x3300
    """Output voltage - generic."""
    TEMERATURE_GENERIC = 0x4000
    """Temperature - generic error."""
    TEMERATURE_AMBIENT = 0x4100
    """Ambient temperature - generic."""
    TEMERATURE_DEVICE = 0x4200
    """Device temperature - generic."""
    HARDWARE_GENERIC = 0x5000
    """CANopen device hardware - generic error."""
    SOFTWARE_GENERIC = 0x6000
    """CANopen device software - generic error."""
    SOFTWARE_INTERNAL = 0x6100
    """Internal software - generic."""
    SOFTWARE_USER = 0x6200
    """User software - generic."""
    SOFTWARE_DATA_SET = 0x6300
    """Data set - generic."""
    ADDITIONAL_MODULES_GENERIC = 0x7000
    """Additional moules - generic error."""
    MONITORING_GENERIC = 0x8000
    """Monitoring - generic error."""
    COMM_GENERIC = 0x8100
    """Communication - generic."""
    COMM_CAN_OVERRUN = 0x8110
    """CAN overrun (objects lost)."""
    COMM_CAN_PASSIVE_MODE = 0x8120
    """CAN in error passive mode."""
    COMM_HB_ERROR = 0x8130
    """Life guard or heartbeat error."""
    COMM_RECOVERED_BUS = 0x8140
    """recover from bus off."""
    COMM_CAN_ID_COLLISION = 0x8150
    """CAN-ID collision."""
    PROTOCOL_GENERIC = 0x8200
    """Protocol error - generic."""
    PROTOCOL_PDO_NOT_PROCESSED = 0x8210
    """PDO not process due to length error."""
    PROTOCOL_PDO_LEN_EXCEEDED = 0x8220
    """PDO length exceeded."""
    PROTOCOL_DAM_MPDO_NOT_PROCESSED = 0x8230
    """DAM MPDO not processed, destination object not available."""
    PROTOCOL_SYNC_LEN = 0x8240
    """Unexpected SYNC data length."""
    PROTOCOL_RPDO_TIMEOUT = 0x8250
    """RPDO timeout."""
    EXTERNAL_GENERIC = 0x9000
    """Extern error - generic error."""
    ADDITIONAL_FUNCS_GENERIC = 0xF0000
    """"Additional functions - generic error."""
    DEVICE_SPECIFIC_GENERIC = 0xFF00
    """Device specific - generic error."""


class OdDataType(IntEnum):
    """Object dictionary data types defined by CiA 301."""

    BOOLEAN = 0x0001
    INTEGER8 = 0x0002
    INTEGER16 = 0x0003
    INTEGER32 = 0x0004
    UNSIGNED8 = 0x0005
    UNSIGNED16 = 0x0006
    UNSIGNED32 = 0x0007
    REAL32 = 0x0008
    VISIBLE_STRING = 0x0009
    OCTET_STRING = 0x000A
    DOMAIN = 0x000F
    REAL64 = 0x0011
    INTEGER64 = 0x0015
    UNSIGNED64 = 0x001B

    @property
    def is_int(self) -> bool:
        """bool: Check if type is a integer type."""
        return self.value in [
            self.INTEGER8,
            self.INTEGER16,
            self.INTEGER32,
            self.INTEGER64,
            self.UNSIGNED8,
            self.UNSIGNED16,
            self.UNSIGNED32,
            self.UNSIGNED64,
        ]

    def is_float(self) -> bool:
        """bool: Check if type is a float type."""
        return self.value in [self.REAL32, self.REAL64]

    def is_str(self) -> bool:
        """bool: Check if type is a str type."""
        return self.value in [self.VISIBLE_STRING, self.OCTET_STRING]
