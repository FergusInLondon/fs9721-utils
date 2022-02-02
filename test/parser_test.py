import unittest

from fs9721_utils.parser import FS9721, FS9721Flag, FS9721Unit


class TestPacketParsing(unittest.TestCase):

    def test_parse_flags(self):
        cases = [
            {
                "sample": [0x17, 0x27, 0x3D, 0x47, 0x5D, 0x65, 0x7B, 0x89, 0x97, 0xA0, 0xB8, 0xC0, 0xD4, 0xE1],
                "units": [FS9721Unit.MILLI, FS9721Unit.VOLT],
                "flags": [FS9721Flag.DC, FS9721Flag.AUTO, FS9721Flag.CONNECTED],
                "display": "002."
            },
            {
                "sample": [0x17, 0x27, 0x3D, 0x40, 0x55, 0x67, 0x7D, 0x8B, 0x9F, 0xA0, 0xB8, 0xC0, 0xD4, 0xE1],
                "units": [FS9721Unit.MILLI, FS9721Unit.VOLT],
                "flags": [FS9721Flag.DC, FS9721Flag.AUTO, FS9721Flag.CONNECTED],
                "display": "010.9"
            },
            {
                "sample": [0x17, 0x27, 0x3D, 0x47, 0x5D, 0x63, 0x7F, 0x8F, 0x9F, 0xA0, 0xB8, 0xC0, 0xD4, 0xE1],
                "units": [FS9721Unit.MILLI, FS9721Unit.VOLT],
                "flags": [FS9721Flag.DC, FS9721Flag.AUTO, FS9721Flag.CONNECTED],
                "display": "009.8"
            },
            {
                "sample": [0x17, 0x27, 0x3D, 0x47, 0x5D, 0x61, 0x75, 0x8F, 0x9F, 0xA0, 0xB8, 0xC0, 0xD4, 0xE1],
                "units": [FS9721Unit.MILLI, FS9721Unit.VOLT],
                "flags": [FS9721Flag.DC, FS9721Flag.AUTO, FS9721Flag.CONNECTED],
                "display": "007.8"
            },
            {
                "sample": [0x15, 0x27, 0x3D, 0x47, 0x5D, 0x67, 0x7D, 0x87, 0x9E, 0xA0, 0xB0, 0xC0, 0xD0, 0xE4],
                "units": [FS9721Unit.CELSIUS],
                "flags": [FS9721Flag.DC, FS9721Flag.CONNECTED],
                "display": "0006"
            },
        ]

        for test in cases:
            meter = FS9721(test["sample"])
            assert test["display"] == meter.display()

            units = meter.units()
            assert len(units) == len(test["units"])
            assert all([u in units for u in test["units"]])

            flags = meter.flags()
            assert len(flags) == len(test["flags"])
            assert all([f in flags for f in test["flags"]])
