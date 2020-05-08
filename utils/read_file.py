import sys

def read_file(filepath, num_bytes):
    int_list = []
    fd_bin = open(filepath, "rb")
    array_bytes = fd_bin.read(num_bytes)
    for one_byte in array_bytes:
        int_list.append(ord(one_byte))
    return int_list
    
def print_help():
    print("unexpected number of arguments")
    print("usage: read_file <filename> <num_bytes>")

if len(sys.argv) != 3:
    print_help()
    sys.exit(1)

filepath = sys.argv[1]
num_bytes = int(sys.argv[2])

int_list = read_file(filepath, num_bytes)
print(int_list)
