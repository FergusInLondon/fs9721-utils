# The FS9721 Protocol

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

```c
/*
 * parse_packet accepts raw byte values taken from the inbound packet
 * and (a) checks the sequencing of the bytes to ensure the packet is
 * correctly forms, and then (b) creates a continuous 7 byte buffer
 * containing the data from the packet.
 */
uint8_t* parse_packet(uint8_t *data) {
    uint8_t *packet = (uint8_t *)calloc(7, sizeof(uint8_t));

    for (int i=0; i < PACKET_LENGTH; i++) {
        if ((i+1) != (data[i] >> 4)) {
            return NULL;
        }

        uint8_t mask = data[i] & 0x0F;
        if ((i%2) == 0) {
            mask = mask << 4;
        }

        packet[i/2] |= mask;
    }

    return packet;
}
```

    0x1D 0x2E 0x3A 0x4D 0x5B 0x6E 0x7E
    0x8F 0x91 0xA2 0xB3 0xC3 0xD4 0xE5

    0xDE 0xAD 0xBE 0xEF 0x12 0x34 0x50 # Note final 4 bits not required; could be reduced to 6 bytes

### Data Format

The remaining 56 bits of the packet can be treated as a bitfield, where each individual bit represents a Boolean signifying whether a given segment of the LCD is currently enabled.

```c
typedef union {
    uint8_t data[DATA_LENGTH];
    struct {
        uint8_t ac : 1;
        uint8_t dc : 1;
        uint8_t autorange : 1;
        uint8_t connected : 1;
        uint8_t negative : 1;
        uint8_t first_digit : 7;
        uint8_t first_dp : 1;
        uint8_t second_digit : 7;
        uint8_t second_dp : 1;
        uint8_t third_digit : 7;
        uint8_t third_dp : 1;
        uint8_t fourth_digit : 7;
        uint8_t micro : 1;
        uint8_t nano : 1;
        uint8_t kilo : 1;
        uint8_t diode : 1;
        uint8_t milli : 1;
        uint8_t percent : 1;
        uint8_t mega : 1;
        uint8_t continuity : 1;
        uint8_t capacitance : 1;
        uint8_t ohm : 1;
        uint8_t relative : 1;
        uint8_t hold : 1;
        uint8_t amp : 1;
        uint8_t volts : 1;
        uint8_t hertz : 1;
        uint8_t low_battery : 1;
        uint8_t minimum : 1;
        uint8_t celsius : 1;
        uint8_t fahrenheight : 1;
        uint8_t maximum : 1;
    };
} multimeter_reading;
```

Note that the segments of the LCD used for digits are contained within continuous 7-bit regions of this structure, and follow a standard way of representing seven segment displays. This allows them to be mapped with ease:

    Map

## Example Parser

```c
/**
 * @file example_parser.c
 * @author your name (you@domain.com)
 * @brief 
 * @version 0.1
 * @date 2022-02-03
 * 
 * @copyright Copyright (c) 2022
 * 
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

#define REVERSE_DATA
#define PACKET_LENGTH 14
#define DATA_LENGTH 7


/**
 * 
 * 
 */
typedef union {
    uint8_t data[DATA_LENGTH];
    struct {
        unsigned int ac : 1;
        unsigned int dc : 1;
        unsigned int autorange : 1;
        unsigned int connected : 1;
        unsigned int negative : 1;
        unsigned int first_digit : 7;
        unsigned int first_dp : 1;
        unsigned int second_digit : 7;
        unsigned int second_dp : 1;
        unsigned int third_digit : 7;
        unsigned int third_dp : 1;
        unsigned int fourth_digit : 7;
        unsigned int micro : 1;
        unsigned int nano : 1;
        unsigned int kilo : 1;
        unsigned int diode : 1;
        unsigned int milli : 1;
        unsigned int percent : 1;
        unsigned int mega : 1;
        unsigned int continuity : 1;
        unsigned int capacitance : 1;
        unsigned int ohm : 1;
        unsigned int relative : 1;
        unsigned int hold : 1;
        unsigned int amp : 1;
        unsigned int volts : 1;
        unsigned int hertz : 1;
        unsigned int low_battery : 1;
        unsigned int minimum : 1;
        unsigned int celsius : 1;
        unsigned int fahrenheight : 1;
        unsigned int maximum : 1;
    };
} multimeter_reading;


/**
 * Used for when bit order (i.e. LSB vs MSB first) on the system does
 * not match the format from the device. Real solution: don't use a bitfield.
 * 
 * @see https://graphics.stanford.edu/~seander/bithacks.html#BitReverseObvious
 */
uint8_t reverse(uint8_t in) {
    uint8_t r = in; 

    int cnt = 7;
    for (in >>= 1; in; in >>= 1) {   
        r <<= 1;
        r |= in & 1;
        cnt--;
    }

    r <<= cnt;
    return r;
}


/* 
 * parse_packet accepts raw byte values taken from the inbound packet
 * and (a) checks the sequencing of the bytes to ensure the packet is
 * correctly forms, and then (b) creates a continuous 7 byte buffer
 * containing the data from the packet.
 */
multimeter_reading* parse_packet(uint8_t *data) {
    multimeter_reading *packet = (multimeter_reading *)calloc(1, sizeof(uint8_t));

    for (int i=0; i < PACKET_LENGTH; i++) {
        if ((i+1) != (data[i] >> 4)) {
            return NULL;
        }

        uint8_t mask = data[i] & 0x0F;
        if ((i%2) == 0) {
            mask = mask << 4;
        }

        packet->data[i/2] |= mask;
    }

    // Bit field was chosen for simplicity so as to demonstrate the
    // structure of the data; but in reality this isn't ideal, as there's
    // no gaurantee over the order of bits - it's implementation specific.
    #ifdef REVERSE_DATA
    for (int i=0; i < PACKET_LENGTH; i++) {
        packet->data[i] = reverse(packet->data[i]);
    }
    #endif

    return packet;
}


void print_bytes(uint8_t *bytes, int len) {
    for (int i = 0; i < len; i++) {
        printf("%02X ", bytes[i]);
    }
    printf("\n");
}


void print_meter(multimeter_reading *dmm) {
    printf(
        "Multimeter Reading:\n\t Mode AC: %i\n\t Mode DC: %i\n\t Autorange: %i\n\t Connected: %i\n",
        dmm->ac, dmm->dc, dmm->autorange, dmm->connected
    );
}


int main(int argc, char *argv[]) {
    uint8_t packet[] = {
        0x17, 0x27, 0x3D, 0x47, 0x5D, 0x65, 0x7B,
        0x89, 0x97, 0xA0, 0xB8, 0xC0, 0xD4, 0xE1
    };

    multimeter_reading *parsed = parse_packet(packet);
    if (parsed == NULL) {
        printf("failed to decode packet: invalid length?");
        return -1;
    }

    printf("Inbound Packet:\t");
    print_bytes(packet, 14);

    printf("Parsed Data:\t");
    print_bytes(parsed->data, 7);

    print_meter(parsed);
    return 0;
}
```

## Resources

    The author of that handy blog post and the github account/repo of the python example.

[^1]: **Over-simplification alert:** the last four bits of the message are not actually associated with segments on the LCD, and seem to be implementation specific for given manufacturers. They are not required to take readings from the device though.

