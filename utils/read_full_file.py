import pdb
from XRootD import client

def fetch_full_file(fd):
    int_list = []
    status, byte_array = fd.read()
    for one_byte in byte_array:
        int_list.append(ord(one_byte))
    return int_list, status

fd = client.File()
fd.open('root://fermicloud157.fnal.gov:1094//100_values.bin')
byte_array, status = fetch_full_file(fd)
print(byte_array)
fd.close()
