from __future__ import annotations
from collections import namedtuple
from enum import Enum, auto
from math import floor
from typing import List, OrderedDict

from bitstruct import unpack


PacketParameter = namedtuple("PacketParameter", [
    "width", "type", "value"
])


PacketSpecification = List[PacketParameter]


class PacketParameterType(Enum):
    UNIT = auto()
    FLAG = auto()
    VALUE = auto()


class FS9721Flag(Enum):
    AC = auto()
    DC = auto()
    AUTO = auto()
    CONNECTED = auto()
    DIODE = auto()
    CONTINUITY = auto()
    CAPACITANCE = auto()
    RELATIVE = auto()
    HOLD = auto()
    MINIMUM = auto()
    MAXIMUM = auto()
    LOW_BATTERY = auto()


class FS9721Unit(Enum):
    NANO = auto()
    MICRO = auto()
    KILO = auto()
    MILLI = auto()
    MEGA = auto()
    PERCENT = auto()
    OHM = auto()
    AMP = auto()
    VOLT = auto()
    FAHRENHEIGHT = auto()
    HERTZ = auto()
    CELSIUS = auto()


_PACKET_SPEC = OrderedDict()
_PACKET_SPEC["ac"] = PacketParameter(
    type=PacketParameterType.FLAG, value=FS9721Flag.AC, width=1
)
_PACKET_SPEC["dc"] = PacketParameter(
    type=PacketParameterType.FLAG, value=FS9721Flag.DC, width=1
)
_PACKET_SPEC["auto"] = PacketParameter(
    type=PacketParameterType.FLAG, value=FS9721Flag.AUTO, width=1
)
_PACKET_SPEC["connected"] = PacketParameter(
    type=PacketParameterType.FLAG, value=FS9721Flag.CONNECTED, width=1
)
_PACKET_SPEC["negative"] = PacketParameter(
    type=PacketParameterType.VALUE, value=None, width=1
)
_PACKET_SPEC["digit1"] = PacketParameter(
    type=PacketParameterType.VALUE, value=None, width=7
)
_PACKET_SPEC["dp1"] = PacketParameter(
    type=PacketParameterType.VALUE, value=None, width=1
)
_PACKET_SPEC["digit2"] = PacketParameter(
    type=PacketParameterType.VALUE, value=None, width=7
)
_PACKET_SPEC["dp2"] = PacketParameter(
    type=PacketParameterType.VALUE, value=None, width=1
)
_PACKET_SPEC["digit3"] = PacketParameter(
    type=PacketParameterType.VALUE, value=None, width=7
)
_PACKET_SPEC["dp3"] = PacketParameter(
    type=PacketParameterType.VALUE, value=None, width=1
)
_PACKET_SPEC["digit4"] = PacketParameter(
    type=PacketParameterType.VALUE, value=None, width=7
)
_PACKET_SPEC["micro"] = PacketParameter(
    type=PacketParameterType.UNIT, value=FS9721Unit.MICRO, width=1
)
_PACKET_SPEC["nano"] = PacketParameter(
    type=PacketParameterType.UNIT, value=FS9721Unit.NANO, width=1
)
_PACKET_SPEC["kilo"] = PacketParameter(
    type=PacketParameterType.UNIT, value=FS9721Unit.KILO, width=1
)
_PACKET_SPEC["diode"] = PacketParameter(
    type=PacketParameterType.FLAG, value=FS9721Flag.DIODE, width=1
)
_PACKET_SPEC["milli"] = PacketParameter(
    type=PacketParameterType.UNIT, value=FS9721Unit.MILLI, width=1
)
_PACKET_SPEC["percent"] = PacketParameter(
    type=PacketParameterType.UNIT, value=FS9721Unit.PERCENT, width=1
)
_PACKET_SPEC["mega"] = PacketParameter(
    type=PacketParameterType.UNIT, value=FS9721Unit.MEGA, width=1
)
_PACKET_SPEC["continuity"] = PacketParameter(
    type=PacketParameterType.FLAG, value=FS9721Flag.CONTINUITY, width=1
)
_PACKET_SPEC["capacitance"] = PacketParameter(
    type=PacketParameterType.FLAG, value=FS9721Flag.CAPACITANCE, width=1
)
_PACKET_SPEC["ohm"] = PacketParameter(
    type=PacketParameterType.UNIT, value=FS9721Unit.OHM, width=1
)
_PACKET_SPEC["relative"] = PacketParameter(
    type=PacketParameterType.FLAG, value=FS9721Flag.RELATIVE, width=1
)
_PACKET_SPEC["hold"] = PacketParameter(
    type=PacketParameterType.VALUE, value=FS9721Flag.HOLD, width=1
)
_PACKET_SPEC["amp"] = PacketParameter(
    type=PacketParameterType.UNIT, value=FS9721Unit.AMP, width=1
)
_PACKET_SPEC["volts"] = PacketParameter(
    type=PacketParameterType.UNIT, value=FS9721Unit.VOLT, width=1
)
_PACKET_SPEC["hertz"] = PacketParameter(
    type=PacketParameterType.UNIT, value=FS9721Unit.HERTZ, width=1
)
_PACKET_SPEC["low_battery"] = PacketParameter(
    type=PacketParameterType.VALUE, value=FS9721Flag.LOW_BATTERY, width=1
)
_PACKET_SPEC["minimum"] = PacketParameter(
    type=PacketParameterType.VALUE, value=FS9721Flag.MINIMUM, width=1
)
_PACKET_SPEC["celsius"] = PacketParameter(
    type=PacketParameterType.UNIT, value=FS9721Unit.CELSIUS, width=1
)
_PACKET_SPEC["fahrenheight"] = PacketParameter(
    type=PacketParameterType.UNIT, value=FS9721Unit.FAHRENHEIGHT, width=1
)
_PACKET_SPEC["maximum"] = PacketParameter(
    type=PacketParameterType.VALUE, value=FS9721Flag.MAXIMUM, width=1
)


_PACKET_PARSE_STR = ''.join([f"u{p.width}" for p in _PACKET_SPEC.values()])


ParsedFlags = namedtuple("ParsedFlags", _PACKET_SPEC.keys())


class InvalidPacketError(Exception):
    pass


class FS9721:
    """
    FS9721 parses a control packet recieved from the FS9721-based multimeter,
    and builds an object that contains the current state of the device.
    """
    def __init__(self, packet: bytearray):
        if len(packet) != 14:
            raise InvalidPacketError(f"invalid payload: incorrect length ({len(packet)} bytes)")
        
        packet_data = bytearray(7)
        for idx, byte in enumerate(packet):
            # MSB 4 bits are a counter
            if (idx+1) != (byte >> 4):
                raise InvalidPacketError("packet out of sequence")

            mask = (byte & 0x0F) # 0b0000XXXX

            # set higher bytes on every other iteration;
            # i.e. 0b0000XXXX -> 0bXXXX0000
            if (idx % 2) == 0:
                mask = mask << 4

            packet_data[floor(idx/2)] |= mask
        
        self.state = ParsedFlags(
            *(unpack(_PACKET_PARSE_STR, packet_data))
        )
    
    def display(self) -> str:
        char_map = {
            0x7D: "0", 0x05: "1", 0x5B: "2", 0x1F: "3", 0x27: "4", 0x3E: "5",
            0x7E: "6", 0x15: "7", 0x7F: "8", 0x3F: "9", 0x0: "", 0x68: "L"
        }

        def parse_digit(val):
            return char_map.get(val, "")
        
        def parse_dp(val):
            return "." if val else ""
        
        return ''.join([
            "-" if self.state.negative else "", parse_digit(self.state.digit1), 
            parse_dp(self.state.dp1), parse_digit(self.state.digit2),
            parse_dp(self.state.dp2), parse_digit(self.state.digit3),
            parse_dp(self.state.dp3), parse_digit(self.state.digit4)
        ])

    def value(self) -> float:
        return float(self.display())
    
    def units(self) -> List[str]:
        def has_unit(ident: str, param: PacketParameter):
            is_unit = (param.type == PacketParameterType.UNIT)
            return is_unit and (getattr(self.state, ident))
        
        return [p.value for i, p in _PACKET_SPEC.items() if has_unit(i, p)]

    def flags(self) -> List[FS9721Flag]:
        def has_flag(ident: str, param: PacketParameter):
            is_flag = (param.type == PacketParameterType.FLAG)
            return is_flag and (getattr(self.state, ident)) 
        
        return [p.value for i, p in _PACKET_SPEC.items() if has_flag(i, p)]
