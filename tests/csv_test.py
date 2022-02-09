from csv import reader
from datetime import datetime
import enum
from tempfile import TemporaryFile
from unittest.mock import patch
import unittest

from freezegun import freeze_time

from fs9721_utils import Reading
from fs9721_utils.csv_logger import CSVWriter

from .cases import valid_expectations

_frozen_time = datetime.now()
_expected_header = ["time", "value", "unit"]
_expected_timestamp = _frozen_time.isoformat()


@freeze_time(_frozen_time)
class TestCSVLogging(unittest.TestCase):
    def test_logs_with_values(self):
        expectations = [None]

        with TemporaryFile(mode='w+') as tmp:
            with patch('fs9721_utils.csv_logger.open') as mo:
                mo.return_value = tmp

                w = CSVWriter()

                for i in range(0, 10):
                    expectations.append([str(i), "V"])
                    w.log_value(value=i, unit="V")
                
                for i in range(0,45):
                    expectations.append([str(i*15), "Ohm"])
                    w.log_value(value=i*15, unit="Ohm")
            
            tmp.seek(0)
            for idx, actual in enumerate(reader(tmp)):
                if idx == 0:
                    assert actual == _expected_header
                    continue
                
                assert actual == [_expected_timestamp] + expectations[idx]


    def test_logs_from_reading(self):
        with TemporaryFile(mode='w+') as tmp:
            test_expectations = valid_expectations()

            with patch('fs9721_utils.csv_logger.open') as mo:
                mo.return_value = tmp

                w = CSVWriter()
                for case in test_expectations:
                    w.log(Reading(case["sample"]))
                
            tmp.seek(0)
            for idx, actual in enumerate(reader(tmp)):
                if idx == 0:
                    assert actual == _expected_header
                    continue
                
                assert actual == [_expected_timestamp] + test_expectations[idx-1]["as_csv"]
