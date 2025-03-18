import socket
import struct
import textwrap

TAB_1 = '\t - '
TAB_2 = '\t\t - '
TAB_3 = '\t\t\t - '
TAB_4 = '\t\t\t\t - '

DATA_TAB_1 = '\t '
DATA_TAB_2 = '\t\t '
DATA_TAB_3 = '\t\t\t '
DATA_TAB_4 = '\t\t\t\t '

def main():
    conn = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
    
    while True:
        raw_data, addr = conn.recvfrom(65536)
        dest_mac, src_mac, eth_proto, data = ethernet_frame(raw_data)
        printst('\nEthernet Frame:')
        printst(TAB_1 + 'Destination: {}, Source: {}, Protocol: {}'.format(dest_mac,src_mac,eth_proto))
        
        # 8 for IPv4
        if eth_proto == 8:
            (version, header_length, ttl, proto, src, target, data) = ipv4_packet(data)
            printst(TAB_1 + 'IPV4 Packet:')
            printst(TAB_2 + 'Version: {}, Header Length: {}, TTL: {}'.format(version, header_length, ttl))
            printst(TAB_2 + 'Protocol: {}, Source: {}, Target: {}'.format(proto, src, target))
            
            # ICMP
            if proto == 1:
                icmp_type, code, checksum, data = icmp_packet(data)
                printst(TAB_1 + 'ICMP Packet:')
                printst(TAB_2 + 'Type: {}, Code: {}, Checksum: {}'.format(icmp_type, code, checksum))
                printst(TAB_2 + 'Data:')
                printst(format_mult_line(DATA_TAB_3, data))
                
            # TCP
            elif proto == 6:
                src_port, dest_port, sequence, ack, flag_urg, flag_ack, flag_psh, flag_rst, flag_syn, flag_fin, data = tcp_segment(data)
                printst(TAB_1 + 'TCP Segment')
                printst(TAB_2 + 'Source Port: {}, Dest Port: {}'.format(src_port, dest_port))
                printst(TAB_2 + 'Sequence: {}, Ack: {}'.format(sequence, ack))
                printst(TAB_2 + 'URG: {}, ACK: {}, PSH: {}, RST: {}, SYN: {}, FIN: {}'.format(flag_urg, flag_ack, flag_psh, flag_rst, flag_syn, flag_fin))
                printst(TAB_2 + 'Data Length: {}, Data:'.format(len(data)))
                printst(format_mult_line(DATA_TAB_3, data))
                
            # UDP
            elif proto == 17:
                src_port, dest_port, size, data = udp_segment(data)
                printst(TAB_1 + 'UDP Segment')
                printst(TAB_2 + 'Source Port: {}, Dest Port: {}, Length: {}'.format(src_port, dest_port, size))
                printst(TAB_2 + 'Data:')
                printst(format_mult_line(DATA_TAB_3, data))
                
                
            # OTHER
            else:
                printst(TAB_1 + 'Data:')
                printst(format_mult_line(DATA_TAB_2, data))
            

# unpack ethernet frame
def ethernet_frame(data):
    dest_mac, src_mac, proto = struct.unpack('! 6s 6s H', data[:14])
    return get_mac_addr(dest_mac), get_mac_addr(src_mac), socket.htons(proto), data[14:]

# Return properly formatted MAC address (ie AA:BB:CC:DD:EE:FF)
def get_mac_addr(bytes_addr):
    byte_str = map('{:02X}'.format, bytes_addr)
    return ':'.join(byte_str).upper()

# Unpacks IPv4 packets
def ipv4_packet(data):
    version_header_length = data[0]
    version = version_header_length >> 4
    header_length = (version_header_length & 0xF) * 4 # multiply by 4 to convert to bytes
    ttl, proto, src, target = struct.unpack('! 8x B B 2x 4s 4s', data[:20]) # 8x and 2x just mean skip those x amount of bytes
    return version, header_length, ttl, proto, ipv4(src), ipv4(target), data[header_length:]

def ipv4(addr):
    return '.'.join(map(str,addr))

# Unpacks ICMP Packet
def icmp_packet(data):
    icmp_type, code, checksum = struct.unpack('! B B H', data[:4])
    return icmp_type, code, checksum, data[4:]

# Unpacks TCP segment
def tcp_segment(data):
    (src_port, dest_port, sequence, ack, offset_reserved_flags) = struct.unpack('! H H L L H', data[:14])
    offset = (offset_reserved_flags >> 12) * 4
    flag_urg = (offset_reserved_flags & 32) >> 5
    flag_ack = (offset_reserved_flags & 16) >> 4
    flag_psh = (offset_reserved_flags & 8) >> 3
    flag_rst = (offset_reserved_flags & 4) >> 2
    flag_syn = (offset_reserved_flags & 2) >> 1
    flag_fin = offset_reserved_flags & 1
    return src_port, dest_port, sequence, ack, flag_urg, flag_ack, flag_psh, flag_rst, flag_syn, flag_fin, data[offset:]

# Unpacks UDP segment
def udp_segment(data):
    src_port, dest_port, size = struct.unpack('! H H 2x H', data[:8])
    return src_port, dest_port, size, data[8:]

#Formats multi-line data
def format_mult_line(prefix, string, size=80):
    size -= len(prefix)
    if isinstance(string, bytes):
        string = ''.join(r'\x{:02x}'.format(byte) for byte in string)
        if size % 2:
            size -= 1
    return '\n'.join([prefix + line for line in textwrap.wrap(string, size)])

def printst(msg):
    print(msg)
    with open("Ethernet_Log.txt", "a") as f:
        f.write(msg + '\n')
    

main()