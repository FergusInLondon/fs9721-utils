from __future__ import annotations
from collections import namedtuple
from enum import Enum, auto
from math import floor
from typing import List

from bitstruct import unpack


PacketParameter = namedtuple("PacketParameter", [
    "identifier", "width", "type", "value"
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


_PACKET_SPEC = [
    PacketParameter(
        identifier="ac", width=1,
        type=PacketParameterType.FLAG, value=FS9721Flag.AC
    ),
    PacketParameter(
        identifier="dc", width=1,
        type=PacketParameterType.FLAG, value=FS9721Flag.DC
    ),
    PacketParameter(
        identifier="auto", width=1,
        type=PacketParameterType.FLAG, value=FS9721Flag.AUTO
    ),
    PacketParameter(
        identifier="rs232", width=1,
        type=PacketParameterType.FLAG, value=FS9721Flag.CONNECTED
    ),
    PacketParameter(
        identifier="negative", width=1,
        type=PacketParameterType.VALUE, value=None
    ),
    PacketParameter(
        identifier="digit1", width=7,
        type=PacketParameterType.VALUE, value=None
    ),
    PacketParameter(
        identifier="dp1", width=1,
        type=PacketParameterType.VALUE, value=None
    ),
    PacketParameter(
        identifier="digit2", width=7,
        type=PacketParameterType.VALUE, value=None
    ),
    PacketParameter(
        identifier="dp2", width=1,
        type=PacketParameterType.VALUE, value=None
    ),
    PacketParameter(
        identifier="digit3", width=7,
        type=PacketParameterType.VALUE, value=None
    ),
    PacketParameter(
        identifier="dp3", width=1,
        type=PacketParameterType.VALUE, value=None
    ),
    PacketParameter(
        identifier="digit4", width=7,
        type=PacketParameterType.VALUE, value=None
    ),
    PacketParameter(
        identifier="micro", width=1,
        type=PacketParameterType.UNIT, value=FS9721Flag.AC
    ),
    PacketParameter(
        identifier="nano", width=1,
        type=PacketParameterType.UNIT, value=FS9721Flag.DC
    ),
    PacketParameter(
        identifier="kilo", width=1,
        type=PacketParameterType.UNIT, value=FS9721Flag.AUTO
    ),
    PacketParameter(
        identifier="diode", width=1,
        type=PacketParameterType.FLAG, value=FS9721Flag.DIODE
    ),
    PacketParameter(
        identifier="milli", width=1,
        type=PacketParameterType.UNIT, value=FS9721Unit.MILLI
    ),
    PacketParameter(
        identifier="percent", width=1,
        type=PacketParameterType.UNIT, value=FS9721Unit.PERCENT
    ),
    PacketParameter(
        identifier="mega", width=1,
        type=PacketParameterType.UNIT, value=FS9721Unit.MEGA
    ),
    PacketParameter(
        identifier="continuity", width=1,
        type=PacketParameterType.FLAG, value=FS9721Flag.CONTINUITY
    ),
    PacketParameter(
        identifier="capacitance", width=1,
        type=PacketParameterType.FLAG, value=FS9721Flag.CAPACITANCE
    ),
    PacketParameter(
        identifier="ohm", width=1,
        type=PacketParameterType.UNIT, value=FS9721Unit.OHM
    ),
    PacketParameter(
        identifier="relative", width=1,
        type=PacketParameterType.FLAG, value=FS9721Flag.RELATIVE
    ),
    PacketParameter(
        identifier="hold", width=1,
        type=PacketParameterType.VALUE, value=FS9721Flag.HOLD
    ),
    PacketParameter(
        identifier="amp", width=1,
        type=PacketParameterType.UNIT, value=FS9721Unit.AMP
    ),
    PacketParameter(
        identifier="volts", width=1,
        type=PacketParameterType.UNIT, value=FS9721Unit.VOLT
    ),
    PacketParameter(
        identifier="hertz", width=1,
        type=PacketParameterType.UNIT, value=FS9721Unit.HERTZ
    ),
    PacketParameter(
        identifier="low_battery", width=1,
        type=PacketParameterType.VALUE, value=FS9721Flag.LOW_BATTERY
    ),
    PacketParameter(
        identifier="minimum", width=1,
        type=PacketParameterType.VALUE, value=FS9721Flag.MINIMUM
    ),
    PacketParameter(
        identifier="celsius", width=1,
        type=PacketParameterType.UNIT, value=FS9721Unit.CELSIUS
    ),
    PacketParameter(
        identifier="fahrenheight", width=1,
        type=PacketParameterType.UNIT, value=FS9721Unit.FAHRENHEIGHT
    ),
    PacketParameter(
        identifier="maximum", width=1,
        type=PacketParameterType.VALUE, value=FS9721Flag.MAXIMUM
    ),
]


_PACKET_PARSE_STR = ''.join(f"u{p.width}" for p in _PACKET_SPEC)


ParsedFlags = namedtuple("ParsedFlags", [p.identifier for p in _PACKET_SPEC])


class InvalidPacketError(Exception):
    pass


class FS9721:
    """
    FS9721 parses a control packet recieved from the FS9721-based multimeter,
    and builds an object that contains the current state of the device.
    """
    def __init__(self, packet: bytearray):
        if len(packet) != 14:
            raise InvalidPacketError("invalid payload: incorrect length")
        
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
        def has_unit(param: PacketParameter):
            is_unit = (param.type == PacketParameterType.UNIT)
            return is_unit and (getattr(self.state, param.identifier))
        
        return [u.value for u in _PACKET_SPEC if has_unit(u)]

    def flags(self) -> List[FS9721Flag]:
        def has_flag(param: PacketParameter):
            is_flag = (param.type == PacketParameterType.FLAG)
            return is_flag and (getattr(self.state, param.identifier)) 
        
        return [f.value for f in _PACKET_SPEC if has_flag(f)]
