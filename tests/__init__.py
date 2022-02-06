from contextlib import contextmanager
from unittest import main
from sys import exit, stdout

from coverage import Coverage

from .parser_test import TestPacketParsing

@contextmanager
def coverage():
    c = Coverage()
    c.start()

    yield

    c.stop()
    c.report(file=stdout)

def run():
    with coverage():
        t = main(module="tests", exit=False)

    exit(0 if t.result.wasSuccessful() else -1)
