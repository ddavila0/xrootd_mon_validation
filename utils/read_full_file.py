import sys
from XRootD import client

import pdb

def fetch_full_file(fd):
    int_list = []
    status, byte_array = fd.read()
    for one_byte in byte_array:
        int_list.append(ord(one_byte))
    return int_list, status


if len(sys.argv) != 2:
    print("Unexpected number of arguments")
    print("Usage: read_full_file <FILENAME>")
    sys.exit(1)

filename = sys.argv[1]

fd = client.File()
server_url = "root://fermicloud157.fnal.gov:1094"
file_url = server_url +"//"+ filename
print("opening: "+file_url)

fd.open(file_url)
#fd.open('root://fermicloud157.fnal.gov:1094//256_values_001.bin')
byte_array, status = fetch_full_file(fd)
print(byte_array)
fd.close()
