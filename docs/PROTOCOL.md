# FS9721-LP3 Protocol

Originally intended to interface with PCs via RS232, the FS9721-LP3 controller is now incredibly common in a variety of inexpensive BLE enabled multimeters sold under various brand names and with different companion smartphone apps.

## Transport (Bluetooth Low Energy)

The FS9721-LP3 controller was intended to communicate unidirectionally with a PC by dispatching 14 byte messages over RS232 (as `8n1` - i.e. 8 bits per byte, with one stop bit). Most of the inexpensive BLE multimeters that employ this chip continue to use this format, with the sole difference that they chunk the packet in to two separate messages: an initial one containing 8 bytes of data, and a subsequent one with the remaining 6 bytes.

These messages tend to be communicated with the host by way of Bluetooth notifications, as opposed to polling. As a result, a client needs only to connect to the device, subscribe for notifications, and store incoming messages in a 16 byte buffer. When this buffer is full the data can then be parsed.

    bleak example

## Packet Structure

### Integrity and Byte Indexing

Half of the packet is used for sequencing, with the higher 4 bits of each byte containing the index of associated with that byte - starting with 0x01. This allows the ability to rebuild the packet when the two seperate chunks may have arrived out of order.

For example, given a packet that had no data - and simply contained zero values - then the byte values would be:

    0x10 0x20 0x30 0x40 0x50 0x60 0x70
    0x80 0x90 0xA0 0xB0 0xC0 0xD0 0xE0

Verifying the order of bytes and then removing the indexing can be done via some simple bit wise operations:

     Psuedocode

    0x1D 0x2E 0x3A 0x4D 0x5B 0x6E 0x7E
    0x8F 0x91 0xA2 0xB3 0xC3 0xD4 0xE5

    0xDE 0xAD 0xBE 0xEF 0x12 0x34 0x50 # Note final 4 bits not required; could be reduced to 6 bytes

### Data Format

The remaining 56 bits of the packet can be treated as a bitfield, where each individual bit represents a Boolean signifying whether a given segment of the LCD is currently enabled.

    C Struct and Enum

Note that the segments of the LCD used for digits are contained within continuous 7-bit regions of this structure, and follow a standard way of representing seven segment displays. This allows them to be mapped with ease:

    Map

## Example Parser

    In C.

## Resources

    The author of that handy blog post and the github account/repo of the python example.

[^1]: **Over-simplification alert:** the last four bits of the message are not actually associated with segments on the LCD, and seem to be implementation specific for given manufacturers. They are not required to take readings from the device though.

