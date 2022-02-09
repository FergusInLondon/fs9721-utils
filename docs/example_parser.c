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

char lookup_digit(uint8_t segments) {
    switch segments {
        case 0x7D: return "0";
        case 0x05: return "1";
        case 0x5B: return "2";
        case 0x1F: return "3";
        case 0x27: return "4";
        case 0x3E: return "5";
        case 0x7E: return "6";
        case 0x15: return "7";
        case 0x7F: return "8";
        case 0x3F: return "9";
        case 0x68: return "L";
        default:
            return "";
    }
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
