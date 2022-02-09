# FS9721-LP3 Digital Multimeter Utilities <br/> [![Build Status](https://github.com/FergusInLondon/fs9721-utils/actions/workflows/python.yml/badge.svg))(https://github.com/FergusInLondon/fs9721-utils/actions/workflows/python.yml) [![CodeFactor](https://www.codefactor.io/repository/github/fergusinlondon/fs9721-utils/badge)](https://www.codefactor.io/repository/github/fergusinlondon/fs9721-utils) [![PyPI version](https://badge.fury.io/py/fs9721-utils.svg)](https://badge.fury.io/py/fs9721-utils)

It's just a parser, a csv logger, and some unit tests.

## Usage

```
$ python
imPython 3.9.9 (main, Nov 21 2021, 03:23:42)
[Clang 13.0.0 (clang-1300.0.29.3)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import parser
>>> meter = parser.FS9721([0x17, 0x27, 0x3D, 0x40, 0x55, 0x67, 0x7D, 0x8B, 0x9F, 0xA0, 0xB8, 0xC0, 0xD4, 0xE1])
>>> meter.flags()
[<FS9721Flag.DC: 2>, <FS9721Flag.AUTO: 3>, <FS9721Flag.CONNECTED: 4>]
>>> meter.units()
[<FS9721Unit.MILLI: 4>, <FS9721Unit.VOLT: 9>]
>>> meter.display()
'010.9'
>>> exit()
```

## Notes

**Feb 2022: v0.0.3 enables parsing of packets from the FS9721 device, and logging (to CSV) of the data contained in those packets. After Bluetooth discovery and connection management, docs, and some minor clean-up, this will be stable enough for tagging as v1.**

# License

This repository and the code contained wherein is licensed under the MIT License - see [LICENSE.md](LICENSE.md).
