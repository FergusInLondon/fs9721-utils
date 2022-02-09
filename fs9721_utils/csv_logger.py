"""
This module is responsible for writing data from the multimeter to a CSV file,
it's a very simplistic wrapper around the `csv.writer` object - and performs
some basic transformation logic.
"""
import logging

from collections import namedtuple
from csv import writer
from datetime import datetime
from typing import Optional, Union

from fs9721_utils.reading import NonNumericReadingError, Reading, readable_unit


_LOGGER = logging.getLogger("fs9721")

_CSV_COLUMNS = ["time", "value", "unit"]

CSVRow = namedtuple("CSVRow", _CSV_COLUMNS)

Loggable = Union[CSVRow, Reading]

def _parse_reading(reading: Reading) -> CSVRow:
    read_at = datetime.now()

    try:
        value = reading.value()
    except NonNumericReadingError:
        value = "L"

    return CSVRow(
        time=read_at, value=value,
        unit=readable_unit(reading.units())
    )


class CSVWriterNotReadyError(Exception):
    """
    CSVWriterNotReady is thrown when there's an attempt to write a row to the
    CSV file but the CSV file has already been closed. CSVWriter will not
    reopen the file by default.
    """


class CSVWriter:
    """
    Logger provides a simple wrapper for logging values to a CSV file; handling
    the transformation of values and the management of underlying files.

    When `filename` is specified it sets the name of the destination CSV file.
    When `auto_reopen` is specified then the CSV file will automatically be opened
    in the event that there's an attempted write and the file has been closed.
    """
    def __init__(self, filename: Optional[str] = None, auto_reopen: bool = False):
        self.auto_reopen = auto_reopen
        self.csv = None
        self.writing = False

        self.filename = filename if filename else f"{datetime.now().isoformat()}-dmm-log.csv"
        self._open()

    def _open(self):
        _LOGGER.info("opening CSV file for writing",extra={"filename": self.filename})
        self.output = open(self.filename, "a") # pylint: disable=consider-using-with,unspecified-encoding
        self.csv = writer(self.output)
        self.csv.writerow(_CSV_COLUMNS)
        self.writing = True

    def log_value(self, value, unit):
        """logs out a key/value pairing of value and unit."""
        self.log(CSVRow(time=datetime.now(), value=value, unit=unit))

    def log(self, entry: Loggable):
        """logs out a `Loggable` type - either a `CSVRow` or a `Reading`."""
        if not self.writing:
            _LOGGER.warning("attempt to write CSV data when file is unavailable")
            if self.auto_reopen:
                self._open()
            else:
                raise CSVWriterNotReadyError

        if isinstance(entry, Reading):
            entry = _parse_reading(entry)

        row = [entry.time.isoformat(), entry.value, entry.unit]
        _LOGGER.debug("writing row to CSV file", extra={"row": row})
        self.csv.writerow(row)

    def stop(self):
        """closes the file for writing and marks itself as finished."""
        _LOGGER.debug("csv logging stopping: closing file")
        if self.writing:
            self.output.close()
            self.writing = False

    @property
    def is_logging(self) -> bool:
        """returns whether or not the CSV logger has the file ready for writing"""
        return self.writing
