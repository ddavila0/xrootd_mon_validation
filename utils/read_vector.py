from XRootD import client
import sys

def calculate_len(vector):
    start_n_len = []
    for byte_range in vector:
        start    = byte_range[0]
        offset   = byte_range[1] - start
        start_n_len.append((start, offset))

    return start_n_len

def fetch_vector(fd, vector):
    len_vector = calculate_len(vector)
    try:
        status, vector = fd.vector_read(len_vector)
    except:
        return None

    vector_list = []
    
    for byte_range in vector:
        byte_array =byte_range.buffer
        int_list = []
        for one_byte in byte_array:
            int_list.append(one_byte)
        vector_list.append(int_list)

    return vector_list


if len(sys.argv) < 3:
    print("Unexpected number of arguments")
    print("Usage: read_full_file <FILENAME> Si,Ei [Si+1, Ei+1]")
    sys.exit(1)

filename = sys.argv[1]
num_byte_ranges = (len(sys.argv) -2)

vector = []
for i in range(0, num_byte_ranges):
   one_range = sys.argv[2+i]
   start = int(one_range.split(",")[0])
   end   = int(one_range.split(",")[1])
   vector.append((start,end))
print(vector)

fd = client.File()
server_url = "root://fermicloud157.fnal.gov:1094"
file_url = server_url +"//"+ filename

print("opening: "+file_url)
fd.open(file_url)
vector_list = fetch_vector(fd, vector)
if vector_list is None:
    print("Cannot open file: "+file_url)
else:
    print(vector_list)

fd.close()
