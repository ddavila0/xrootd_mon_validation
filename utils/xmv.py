from XRootD import client
from multiprocessing import Process, Value, Lock
import time
import sys

import pdb


class Server:
    def __init__(self, url):
        self.url = url
    
    def get_full_file(self, filename):
        fd = client.File()
        file_url = self.url +"//"+ filename[:-1]
        print(file_url)
        pdb.set_trace()
        fd.open(file_url)
        print("root://fermicloud157.fnal.gov:1094//256_values_001.bin")
        #fd.open("root://fermicloud157.fnal.gov:1094//256_values_001.bin")
        status, byte_array = fd.read()
        fd.close()
        int_list = []
        for one_byte in byte_array:
            int_list.append(ord(one_byte))
        return int_list, status


def request_file(xrd_server, filename):
	byte_array=""
	byte_array, status = xrd_server.get_full_file(filename)
	#print(filename+": "+byte_array[:10])
	print(filename)



#---------------------------------------------------------
# Config
#---------------------------------------------------------
server_url = "root://fermicloud157.fnal.gov:1094"
list_of_files = "list_of_files.txt"
total_files = 4
files_per_second = 1
rounds = total_files/files_per_second
workers = files_per_second 

#---------------------------------------------------------

# Get list of test files
fd1 = open(list_of_files)
files = fd1.readlines()
fd1.close()

# Create server obj
xrd_server = Server(server_url)
a, b = xrd_server.get_full_file(files[0])
print(a)
sys.exit(0)

for i in range(0, rounds):
	process_list = []
	for j in range(0, workers):
	    p = Process(target=request_file, args=(xrd_server, files[i*rounds + j]))
	    p.start()
	    process_list.append(p)
	
	time.sleep(1)	
	
	for p in process_list:
	    p.join()

