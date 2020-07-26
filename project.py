
# define CL5A75_BUFFER_SIZE               1536
# define CL5A75_HEADER_LEN                7
# define CL5A75_MAX_PIXELS_PER_PACKET     497
# define CL5A75_MAX_CHANNELS_PER_PACKET   (CL5A75_MAX_PIXELS_PER_PACKET * 3)
# define CL5A75_0101_PACKET_DATA_LEN      98
# define CL5A75_0AFF_PACKET_DATA_LEN      63

from socket import socket, AF_PACKET, SOCK_RAW
from load_images import openFileAsByteArray
import time

time_between_frames = 0.2

# Set up static variables
src = b'\x22\x22\x33\x44\x55\x66'
dst = b'\x11\x22\x33\x44\x55\x66'
'''
    First packet
    *   	- Data Length:     98
    *   	- Ether Type:      0x0101 (have also seen 0x0100, 0x0104, 0x0107.
    *   	- Data[0-end]:     0x00
'''
first_frame = dst + src + b'\x01\x01'
first_frame += b''.join([b.to_bytes(1, 'big') for b in bytes(98)])
'''
    Second packet
    *   	- Ether Type:      0x0AFF
    *   	- Data[0]:         0xFF
    *   	- Data[1]:         0xFF
    *   	- Data[2]:         0xFF
    *   	- Data[3-end]:     0x00
'''
second_frame = dst + src + b'\x0A\xFF\xFF\xFF\xFF'
second_frame += b''.join([b.to_bytes(1, 'big') for b in bytes(60)])

data_prefix = dst + src + b'\x55'

s = socket(AF_PACKET, SOCK_RAW)
s.bind(('eth0', 0))


class Packet:
    def __init__(self, panelWidth: int, panelHeight: int):
        self.frames = []
        self.panelWidth = panelWidth
        self.panelHeight = panelHeight

    def addRow(self, row_num: int, offset: int, pixel_data: list):
        '''
        Data packets
        *   	- Ether Type:      0x5500 + MSB of Row Number
        *   	                     0x5500 for rows 0-255
        *   	                     0x5501 for rows 256-511
        *   	- Data[0]:         Row Number LSB
        *   	- Data[1]:         MSB of pixel offset for this packet
        *   	- Data[2]:         LSB of pixel offset for this packet
        *   	- Data[3]:         MSB of pixel count in packet   (int(len(pixel_data) / 3)).to_bytes(2, 'big')
        *   	- Data[4]:         LSB of pixel count in packet
        *   	- Data[5]:         0x08 - ?? unsure what this is
        *   	- Data[6]:         0x80 - ?? unsure what this is
        *   	- Data[7-end]:     RGB order pixel data
        '''
        frame = data_prefix + row_num.to_bytes(2, 'big') + offset.to_bytes(
            2, 'big') + (int(self.panelWidth / 3)).to_bytes(2, 'big') + b'\x08\x80'
        if len(pixel_data) / 3 < self.panelWidth:
            padding = b''.join([b.to_bytes(2, 'big')
                                for b in bytes(self.panelWidth - len(pixel_data))])
            frame += padding
        frame += b''.join([b for b in pixel_data])
        print(frame[:20])
        self.frames.append(frame)

    def send(self):
        i = 0
        s.send(first_frame)
        s.send(second_frame)
        for i, frame in enumerate(self.frames):
            s.send(frame)

        # while i < self.panelHeight:
        #     i += 1
        #     frame = data_prefix + i.to_bytes(2, 'big') + b'\x00\x00' + (int(self.panelWidth / 3)).to_bytes(
        #         2, 'big') + b'\x08\x80' + b''.join([b.to_bytes(2, 'big') for b in bytes(self.panelWidth)])
        #     s.send(frame)
        #     time.sleep(0.001)


if __name__ == "__main__":
    rows = openFileAsByteArray()
    print(rows)
    img = Packet(256, 32)
    for i, row in enumerate(rows):
        img.addRow(i, 0, row)

    print("Sending packets...", flush=True)
    while(True):
        print('.', end='', flush=True)
        img.send()
        time.sleep(time_between_frames)
