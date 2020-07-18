from socket import socket, AF_PACKET, SOCK_RAW
from load_images import openFileAsByteArray


class Packet:
    def __init__(self):
        self.src = ''
        self.dst = ''
        self.eth_type = ''
        self.payload = ''


def sendeth(src, dst, eth_type, payload, interface="eth0"):
    """Send raw Ethernet packet on interface."""

    assert(len(src) == len(dst) == 6)  # 48-bit ethernet addresses
    assert(len(eth_type) == 2)  # 16-bit ethernet type
    frame = []
    frame.extend(dst)
    frame.extend(src)
    frame.extend(eth_type)
    frame.extend(payload)

    s = socket(AF_PACKET, SOCK_RAW)

    #print([int.from_bytes(x, 'big') for x in frame][:30])

    # From the docs: "For raw packet
    # sockets the address is a tuple (ifname, proto [,pkttype [,hatype]])"
    s.bind((interface, 0))
    return s.send(b''.join(frame))


if __name__ == "__main__":
    src = [b'\x22', b'\x22', b'\x33', b'\x44', b'\x55', b'\x66']
    dst = [b'\x11', b'\x22', b'\x33', b'\x44', b'\x55', b'\x66']
    rows = openFileAsByteArray()

    while(True):
        print('.', end='', flush=True)
        '''
        First packet
        *   	- Data Length:     98
        *   	- Ether Type:      0x0101 (have also seen 0x0100, 0x0104, 0x0107.
        *   	- Data[0-end]:     0x00
        '''
        eth_type = [b'\x01', b'\x01']
        payload = [b.to_bytes(1, 'big') for b in bytes(98)]

        sendeth(src, dst, eth_type, payload)

        '''
        Second packet
        *   	- Ether Type:      0x0AFF 
        *   	- Data[0]:         0xFF
        *   	- Data[1]:         0xFF
        *   	- Data[2]:         0xFF
        *   	- Data[3-end]:     0x00
        '''
        eth_type = [b'\x0A', b'\xFF']
        payload = [b'\xFF', b'\xFF', b'\xFF']
        payload.extend([b.to_bytes(1, 'big') for b in bytes(60)])
        sendeth(src, dst, eth_type, payload)

        '''
        Data packets
        *   	- Ether Type:      0x5500 + MSB of Row Number
        *   	                     0x5500 for rows 0-255
        *   	                     0x5501 for rows 256-511
        *   	- Data[0]:         Row Number LSB
        *   	- Data[1]:         MSB of pixel offset for this packet
        *   	- Data[2]:         LSB of pixel offset for this packet
        *   	- Data[3]:         MSB of pixel count in packet
        *   	- Data[4]:         LSB of pixel count in packet
        *   	- Data[5]:         0x08 - ?? unsure what this is
        *   	- Data[6]:         0x80 - ?? unsure what this is
        *   	- Data[7-end]:     RGB order pixel data
        '''
        eth_type = [b'\x55', b'\x00']
        for i in range(256):
            payload = [bytes([255]), b'\x00', b'\x00', b'\x00',
                       bytes([128]), b'\x08', b'\x80']
            if i < len(rows):
                for j in range(0, 128, 3):
                    if False and j < len(rows[i]):
                        payload.extend(
                            [rows[i][j], rows[i][j+1], rows[i][j+2]])
                    else:
                        payload.extend([b'\xFF', b'\x00', b'\x00'])
            else:
                for j in range(0, 128, 3):
                    payload.extend([b'\x00', b'\x00', b'\xFF'])
                #print([rows[i][j], rows[i][j+1], rows[i][j+2]])
                # else:
                #payload.extend([b'\xFF', b'\x00', b'\x00'])
                # B G R
            sendeth(src, dst, eth_type, payload)

        #print(len(rows), len(rows[0]))
        # for i, row in enumerate(rows):
        #    eth_type = [b'\x55', b'\x00']
        #    payload = [bytes([i]), b'\x00', b'\x00', b'\x00',
        #               bytes([len(row)]), b'\x08', b'\x80']
        #    payload.extend([row])
        #    sendeth(src, dst, eth_type, payload)

        # for i in range(64):
        #    eth_type = [b'\x55', b'\x00']
        #    payload = [bytes([i]), b'\x00', b'\x00', b'\x00',
        #               b'\x80', b'\x08', b'\x80']
        #    for j in range(int(64 / 4)):
        #        payload.extend([b'\xFF', b'\x00', b'\x00'])
        #        payload.extend([b'\x00', b'\xFF', b'\x00'])
        #        payload.extend([b'\x00', b'\x00', b'\xFF'])
        #        payload.extend([b'\xFF', b'\xFF', b'\xFF'])
        #    sendeth(src, dst, eth_type, payload)
