import unittest

from fs9721 import Reading
from fs9721.reading import InvalidPacketError

from .cases import _MALFORMED, valid_expectations

class TestPacketParsing(unittest.TestCase):
    def test_raises_for_malformed_packet(self):
        for p in _MALFORMED:
            got_exception = False

            try:
                Reading(p)
            except InvalidPacketError:
                got_exception = True

            assert got_exception

    def test_parse_flags(self):
        for cases in [valid_expectations(), valid_expectations(random=True)]:
            for test in cases:
                meter = Reading(test["sample"])
                assert test["display"] == meter.display()

                units = meter.units()
                assert len(units) == len(test["units"])
                assert all([u in units for u in test["units"]])

                flags = meter.flags()
                assert len(flags) == len(test["flags"])
                assert all([f in flags for f in test["flags"]])
