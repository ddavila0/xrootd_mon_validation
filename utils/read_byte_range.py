from XRootD import client
import sys
import pdb

def fetch_byte_range(fd, start, end):
    #pdb.set_trace()
    chunk_size = end - start
    int_list = []
    try:
        status, byte_array = fd.read(start, chunk_size)
    except:
        return None

    for one_byte in byte_array:
        int_list.append(one_byte)
    return int_list

if len(sys.argv) != 4:
    print("Unexpected number of arguments")
    print("Usage: read_full_file <FILENAME> start end")
    sys.exit(1)

filename = sys.argv[1]
start = int(sys.argv[2])
end = int(sys.argv[3])

fd = client.File()
server_url = "root://fermicloud157.fnal.gov:1094"
file_url = server_url +"//"+ filename

print("opening: "+file_url)
fd.open(file_url)
byte_array = fetch_byte_range(fd, start, end)
if byte_array is None:
    print("Cannot open file: "+file_url)
else:
    print(byte_array)

fd.close()
