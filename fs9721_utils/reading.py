"""
The reading module contains all the logic required to parse and understand a
reading that has been received by a FS9721-based device.
"""
from __future__ import annotations
from collections import namedtuple
from enum import Enum, auto
from math import floor
from typing import List, OrderedDict

from bitstruct import unpack


_PacketParameter = namedtuple("_PacketParameter", [
    "width", "type", "value"
])


class _PacketParameterType(Enum):
    UNIT = auto()
    FLAG = auto()
    VALUE = auto()


class Flag(Enum):
    """A Flag describes the state of the device; such as mode or battery level."""
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


class Unit(Enum):
    """A unit provides context as to how a value should be interpreted."""
    NANO = auto()
    MICRO = auto()
    MILLI = auto()
    KILO = auto()
    MEGA = auto()
    VOLT = auto()
    AMP = auto()
    OHM = auto()
    PERCENT = auto()
    FAHRENHEIGHT = auto()
    CELSIUS = auto()
    HERTZ = auto()


def readable_unit(units: List[Unit], with_prefixes=True) -> str:
    """returns a string representation of the reading's units - i.e. 'mV'."""
    parts = [None, None]

    unit_prefixes = {
        Unit.NANO: 'n', Unit.MICRO: 'u', Unit.MILLI: 'm',
        Unit.KILO: 'k', Unit.MEGA: 'm'
    }

    unit_symbols = {
        Unit.VOLT: 'V', Unit.AMP: 'A', Unit.OHM: 'Ohm', Unit.PERCENT: '%',
        Unit.FAHRENHEIGHT: 'F', Unit.CELSIUS: 'C', Unit.HERTZ: 'Hz'
    }

    for val in units:
        prefix = unit_prefixes.get(val)
        if with_prefixes and prefix:
            parts[0] = prefix
            continue

        symbol = unit_symbols.get(val)
        if symbol:
            parts[1] = symbol
            continue

    return ''.join([p for p in parts if p])


def readable_raw_value(units: List[Unit], val: float) -> float:
    """returns the raw value - i.e. a float in the _base_ unit. (i.e. V vs mV)"""
    unit_multiplier = {
        Unit.NANO: 0.1000000, Unit.MICRO: 0.100000, Unit.MILLI: 0.001,
        Unit.KILO: 1000, Unit.MEGA: 1000000
    }

    for unit in units:
        multiplier = unit_multiplier.get(unit)
        if multiplier:
            return val * multiplier

    return val


_PACKET_SPEC = OrderedDict()
_PACKET_SPEC["ac"] = _PacketParameter(
    type=_PacketParameterType.FLAG, value=Flag.AC, width=1
)
_PACKET_SPEC["dc"] = _PacketParameter(
    type=_PacketParameterType.FLAG, value=Flag.DC, width=1
)
_PACKET_SPEC["auto"] = _PacketParameter(
    type=_PacketParameterType.FLAG, value=Flag.AUTO, width=1
)
_PACKET_SPEC["connected"] = _PacketParameter(
    type=_PacketParameterType.FLAG, value=Flag.CONNECTED, width=1
)
_PACKET_SPEC["negative"] = _PacketParameter(
    type=_PacketParameterType.VALUE, value=None, width=1
)
_PACKET_SPEC["digit1"] = _PacketParameter(
    type=_PacketParameterType.VALUE, value=None, width=7
)
_PACKET_SPEC["dp1"] = _PacketParameter(
    type=_PacketParameterType.VALUE, value=None, width=1
)
_PACKET_SPEC["digit2"] = _PacketParameter(
    type=_PacketParameterType.VALUE, value=None, width=7
)
_PACKET_SPEC["dp2"] = _PacketParameter(
    type=_PacketParameterType.VALUE, value=None, width=1
)
_PACKET_SPEC["digit3"] = _PacketParameter(
    type=_PacketParameterType.VALUE, value=None, width=7
)
_PACKET_SPEC["dp3"] = _PacketParameter(
    type=_PacketParameterType.VALUE, value=None, width=1
)
_PACKET_SPEC["digit4"] = _PacketParameter(
    type=_PacketParameterType.VALUE, value=None, width=7
)
_PACKET_SPEC["micro"] = _PacketParameter(
    type=_PacketParameterType.UNIT, value=Unit.MICRO, width=1
)
_PACKET_SPEC["nano"] = _PacketParameter(
    type=_PacketParameterType.UNIT, value=Unit.NANO, width=1
)
_PACKET_SPEC["kilo"] = _PacketParameter(
    type=_PacketParameterType.UNIT, value=Unit.KILO, width=1
)
_PACKET_SPEC["diode"] = _PacketParameter(
    type=_PacketParameterType.FLAG, value=Flag.DIODE, width=1
)
_PACKET_SPEC["milli"] = _PacketParameter(
    type=_PacketParameterType.UNIT, value=Unit.MILLI, width=1
)
_PACKET_SPEC["percent"] = _PacketParameter(
    type=_PacketParameterType.UNIT, value=Unit.PERCENT, width=1
)
_PACKET_SPEC["mega"] = _PacketParameter(
    type=_PacketParameterType.UNIT, value=Unit.MEGA, width=1
)
_PACKET_SPEC["continuity"] = _PacketParameter(
    type=_PacketParameterType.FLAG, value=Flag.CONTINUITY, width=1
)
_PACKET_SPEC["capacitance"] = _PacketParameter(
    type=_PacketParameterType.FLAG, value=Flag.CAPACITANCE, width=1
)
_PACKET_SPEC["ohm"] = _PacketParameter(
    type=_PacketParameterType.UNIT, value=Unit.OHM, width=1
)
_PACKET_SPEC["relative"] = _PacketParameter(
    type=_PacketParameterType.FLAG, value=Flag.RELATIVE, width=1
)
_PACKET_SPEC["hold"] = _PacketParameter(
    type=_PacketParameterType.VALUE, value=Flag.HOLD, width=1
)
_PACKET_SPEC["amp"] = _PacketParameter(
    type=_PacketParameterType.UNIT, value=Unit.AMP, width=1
)
_PACKET_SPEC["volts"] = _PacketParameter(
    type=_PacketParameterType.UNIT, value=Unit.VOLT, width=1
)
_PACKET_SPEC["hertz"] = _PacketParameter(
    type=_PacketParameterType.UNIT, value=Unit.HERTZ, width=1
)
_PACKET_SPEC["low_battery"] = _PacketParameter(
    type=_PacketParameterType.VALUE, value=Flag.LOW_BATTERY, width=1
)
_PACKET_SPEC["minimum"] = _PacketParameter(
    type=_PacketParameterType.VALUE, value=Flag.MINIMUM, width=1
)
_PACKET_SPEC["celsius"] = _PacketParameter(
    type=_PacketParameterType.UNIT, value=Unit.CELSIUS, width=1
)
_PACKET_SPEC["fahrenheight"] = _PacketParameter(
    type=_PacketParameterType.UNIT, value=Unit.FAHRENHEIGHT, width=1
)
_PACKET_SPEC["maximum"] = _PacketParameter(
    type=_PacketParameterType.VALUE, value=Flag.MAXIMUM, width=1
)


_PACKET_PARSE_STR = ''.join([f"u{p.width}" for p in _PACKET_SPEC.values()])


_PacketParams = namedtuple("_PacketParams", _PACKET_SPEC.keys())


class InvalidPacketError(Exception):
    """
    InvalidPacketError indicates that the packet read from the device is of
    the wrong length or invalid counter bits.
    """

class NonNumericReadingError(Exception):
    """
    NonNumericReadingError occurs when an attempt to read the current value
    as a float is made, but the reading isn't valid - i.e. in the case of "L".
    """

class Reading:
    """
    A Reading is the representation of the state of the device at a given time.
    It accepts a raw packet that has been recieved from the device, performs basic
    validation, parses the packet, and provides an interface for accessing the
    values contained in it.

    Packets that arrive with their bytes in an incorrect order can still be parsed
    by the Reading, as long as the indexing bits (i.e. higher 4 bits of each byte)
    are intact and valid.
    """
    def __init__(self, packet: bytearray):
        if len(packet) != 14:
            raise InvalidPacketError(f"invalid payload: incorrect length ({len(packet)} bytes)")

        seen = [False for _ in range(0, 14)]

        packet_data = bytearray(7)
        for byte in packet:
            # MSB 4 bits are used to index the byte; with a value between 0x01 and 0x014
            byte_idx = (byte >> 4)
            if (not 14 >= byte_idx >= 1) or seen[(byte_idx-1)]:
                raise InvalidPacketError(f"invalid or duplicate byte index recieved: {byte_idx}")

            # Revert to "normal" 0-based indexing now the byte index has been
            # validated
            idx = (byte_idx - 1)
            seen[idx] = True

            # Zero out the four higher bits that contained the index (i.e. 0b0000xxxx)
            byte &= 0x0F

            # Two packet bytes make-up one data byte when indexing is removed,
            # so every second iteration sets the MSB. (i.e. 0bxxxx0000)
            if (idx % 2) == 0:
                byte <<= 4

            packet_data[floor(idx/2)] |= byte

        if not all(seen):
            raise InvalidPacketError("duplicate bytes present in the packet")

        self.state = _PacketParams(
            *(unpack(_PACKET_PARSE_STR, packet_data))
        )

    def display(self) -> str:
        """Returns a string representation of the reading from the devices LCD."""
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
        """
        Returns a numerical representation of the devices read value.
        BEWARE: an exception may be raised (`ValueError`) when that value contains 'L'!
        """
        try:
            return float(self.display())
        except ValueError as value_err:
            msg = f"{self.display()} is not a numeric reading - no suitable value"
            raise NonNumericReadingError(msg) from value_err

    def units(self) -> List[Unit]:
        """Returns a List of `Unit` items associated with the payloads value."""
        def has_unit(ident: str, param: _PacketParameter):
            is_unit = (param.type == _PacketParameterType.UNIT)
            return is_unit and (getattr(self.state, ident))

        return [p.value for i, p in _PACKET_SPEC.items() if has_unit(i, p)]

    def flags(self) -> List[Flag]:
        """Returns a List of `Flag` items for each flag detected in the payload."""
        def has_flag(ident: str, param: _PacketParameter):
            is_flag = (param.type == _PacketParameterType.FLAG)
            return is_flag and (getattr(self.state, ident))

        return [p.value for i, p in _PACKET_SPEC.items() if has_flag(i, p)]
