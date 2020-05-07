import sys

def create_file(filepath, array_len):
    array_numbers = range(0, array_len)
    array_bytes = bytearray(array_numbers)
    fd_bin = open(filepath, "wb")
    fd_bin.write(array_bytes)
    fd_bin.close()

def print_help():
    print("unexpected number of arguments")
    print("usage: create_file <filename> <file_lenght>")

if len(sys.argv) != 3:
    print_help()
    sys.exit(1)

filepath = sys.argv[1]
array_len = int(sys.argv[2])

create_file(filepath, array_len)
