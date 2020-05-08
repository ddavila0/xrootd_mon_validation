import pdb
from XRootD import client

def fetch_byte_range(fd, start, end):
    #pdb.set_trace()
    chunk_size = end - start
    int_list = []
    status, byte_array = fd.read(start, chunk_size)
    for one_byte in byte_array:
        int_list.append(ord(one_byte))
    return int_list

fd = client.File()
fd.open('root://fermicloud157.fnal.gov:1094//100_values.bin')
byte_array = fetch_byte_range(fd, 0, 10)
print(byte_array)
fd.close()
