"""
The FS9721 module provides a public interface to utilities used for parsing
and interpreting messages from an FS9721-based device, as well as for tasks
such as logging those messages and connecting to a device via Bluetooth (BLE).
"""
from .reading import Reading, InvalidPacketError, Flag, Unit
