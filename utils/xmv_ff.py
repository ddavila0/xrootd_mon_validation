#!/usr/bin/env python3

from XRootD import client
from multiprocessing import Process, Value, Lock
import time
import sys
import socket
import pdb
import json

class Server:
    def __init__(self, url):
        self.server_url = url
    
    def fetch_full_file(self, filename, appinfo=""):
        fd = client.File()
        file_url = self.server_url +"//"+ filename
        print("opening: "+file_url)
        fd.open(file_url)
        if appinfo:
            c = client.FileSystem(server_url)
            c_status, c_response = c.sendinfo(appinfo)
            print(appinfo)

        int_list = []
        try:
            status, byte_array = fd.read()
        except:
            return None, -1
    
        for one_byte in byte_array:
            int_list.append(one_byte)
        
        fd.close()
        return int_list, status

def request_file(server, filename, appinfo):
    print(appinfo)
    byte_array, status = server.fetch_full_file(filename, appinfo)
    if status == -1:
        print("Cannot open file: "+ filename +" at server: "+server.server_url)
    else:
        assert(len(byte_array) == 256)

# ---------------------------------------------------------
#                       MAIN
# ---------------------------------------------------------
###--------------------------------------------------------
### Args
###--------------------------------------------------------
if len(sys.argv) == 5:
    total_files = int(sys.argv[1]) 
    files_per_second = int(sys.argv[2]) 
    initial_job_id = int(sys.argv[3]) 
    file_out = sys.argv[4] 
else:
    print("expected: xmv <total_files> <files_per_second> <initial_job_id> <file_out>")
    sys.exit(1)

###---------------------------------------------------------
### Config
###---------------------------------------------------------
server_url="root://fermicloud157.fnal.gov:1094"
list_of_files = "list_of_files.txt"
num_rounds = int(total_files/files_per_second)
num_workers = files_per_second 
###---------------------------------------------------------

# Get list of test files
fd_list = open(list_of_files)
files = fd_list.readlines()
fd_list.close()

# Create server obj
server = Server(server_url)

job_id = initial_job_id
my_dict = {}
for i in range(0, num_rounds):
    process_list = []
    for j in range(0, num_workers):
        filename = files[i*num_workers + j][:-1]
        job_id_s = f'{job_id:03}'
        appinfo = job_id_s+"_https://glidein.cern.ch/1-519/0:0:ddavila:crab:TEST:0:0:TEST:TEST-TEST_1"
        my_dict[job_id_s]=filename
        p = Process(target=request_file, args=(server, filename, appinfo))
        p.start()
        process_list.append(p)
        job_id +=1

    for p in process_list:
        p.join()

for key in my_dict:
    print(f'{key:20} : '+ my_dict[key])

with open(file_out, 'w') as outfile:
    json.dump(my_dict, outfile)

#byte_message = bytes("XMV_STOP", "utf-8")
#opened_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#opened_socket.sendto(byte_message, ("131.225.155.180", 9930))
#time.sleep(1)
#opened_socket.sendto(byte_message, ("131.225.155.180", 9930))
