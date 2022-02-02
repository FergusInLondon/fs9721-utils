# FS9721-LP3 Digital Multimedia Utilities ![Build Status](https://github.com/FergusInLondon/fs9721-utils/actions/workflows/python.yml/badge.svg)


It's just a parser and some unit tests.

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