from collections import namedtuple
from csv import writer
from datetime import date, datetime
from typing import Optional, Union


from fs9721_utils.reading import NonNumericReadingError, Reading, Unit, readable_raw_value, readable_unit


_LOG_COLUMNS = ["time", "value", "unit"]

CSVRow = namedtuple("CSVRow", _LOG_COLUMNS)

Loggable = Union[CSVRow, Reading]

def parse_reading(reading: Reading) -> CSVRow:
    read_at = datetime.now()

    try:
        value = reading.value()
    except NonNumericReadingError:
        value = "L"

    return CSVRow(
        time=read_at, value=value,        
        unit=readable_unit(reading.units())
    )


class CSVWriterNotReady(Exception):
    pass


class CSVWriter:
    """
    Logger provides a simple wrapper for logging values to CSV 
    """
    def __init__(self, output: Optional[str] = None):
        if not output:
            output = f"{datetime.now().isoformat()}-dmm-log.csv"
        
        self.output = open(output, "w")

        self.csv = writer(self.output)
        self.csv.writerow(_LOG_COLUMNS)
        self.writing = True

    def log_value(self, value, unit):
        self.log(CSVRow(time=datetime.now(), value=value, unit=unit))

    def log(self, entry: Loggable):
        if not self.writing:
            raise CSVWriterNotReady
        
        if isinstance(entry, Reading):
            entry = parse_reading(entry)

        self.csv.writerow([entry.time.isoformat(), entry.value, entry.unit])

    def stop(self):
        if self.writing:
            self.output.close()
            self.writing = False

    @property
    def is_logging(self) -> bool:
        return self.writing


if __name__ == "__main__":
    example_payloads = [
        [0x17, 0x27, 0x3D, 0x47, 0x5D, 0x65, 0x7B, 0x89, 0x97, 0xA0, 0xB8, 0xC0, 0xD4, 0xE1],
        [0x17, 0x27, 0x3D, 0x40, 0x55, 0x67, 0x7D, 0x8B, 0x9F, 0xA0, 0xB8, 0xC0, 0xD4, 0xE1],
        [0x17, 0x27, 0x3D, 0x47, 0x5D, 0x63, 0x7F, 0x8F, 0x9F, 0xA0, 0xB8, 0xC0, 0xD4, 0xE1],
        [0x17, 0x27, 0x3D, 0x47, 0x5D, 0x61, 0x75, 0x8F, 0x9F, 0xA0, 0xB8, 0xC0, 0xD4, 0xE1],
        [0x15, 0x27, 0x3D, 0x47, 0x5D, 0x67, 0x7D, 0x87, 0x9E, 0xA0, 0xB0, 0xC0, 0xD0, 0xE4],
    ]

    logger = CSVWriter()

    for i in range(0, 10):
        logger.log(CSVRow(time=datetime.now(), value=i/10, unit="mV"))

    for i in range(0, 10):
        logger.log_value(value=i*10, unit="Ohm")
    
    for p in example_payloads:
        logger.log(Reading(p))

    print(logger.is_logging)
    logger.stop()
    print(logger.is_logging)




