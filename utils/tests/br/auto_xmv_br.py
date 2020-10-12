#!/usr/bin/env python3

from multiprocessing import Process, Value, Lock
import time
import sys
import pdb
import json
import argparse
from ValidationClient import *
from Server import *
import random


def request_byte_range(server, random_file, seek, byte_range_size, appinfo):
    byte_array, status = server.fetch_byte_range(random_file, seek, seek+byte_range_size, appinfo)
    if status == -1:
        print("### ERROR: Cannot open file: "+ random_file +" at server: "+server.server_url)
    else:
        assert(len(byte_array) == byte_range_size)

def run_test(server, initial_job_id, num_rounds, num_workers, random_file, file_size, byte_range_size, file_out):
    job_id = initial_job_id
    my_dict = {}
    for i in range(0, num_rounds):
        process_list = []
        for j in range(0, num_workers):
            seek = random.randint(0, file_size - byte_range_size)
            job_id_s = f'{job_id:03}'
            appinfo = job_id_s+"_https://glidein.cern.ch/1-519/0:0:ddavila:crab:TEST:0:0:TEST:TEST-TEST_1"
            my_dict[job_id_s]=[random_file, byte_range_size]
            p = Process(target=request_byte_range, args=(server, random_file, seek, byte_range_size, appinfo))
            p.start()
            process_list.append(p)
            job_id +=1
    
        for p in process_list:
            p.join()
        time.sleep(1)
    
    #for key in my_dict:
        #print(f'{key:20} : '+ my_dict[key])
    
    with open(file_out, 'w') as outfile:
        json.dump(my_dict, outfile)
    
    return my_dict

def main():
    #--------------------------------------------------------
    # Args
    #--------------------------------------------------------
    if len(sys.argv) == 2:
        tests_file = sys.argv[1]
    else:
        print("expected: xmv <tests_file>")
        print("format of tests_file: <total_files> <files_per_second> <initial_job_id> <file_out>")
        sys.exit(1)
    
    #---------------------------------------------------------
    # Fixed Config
    #---------------------------------------------------------
    server_url="root://fermicloud157.fnal.gov:1094"
    list_of_files = "br_list_of_files.txt"
    #---------------------------------------------------------
    # Rabbit
    queue="xrd.wlcg-itb"
    remove = True
    timeout= 5
    load_dotenv()
    #---------------------------------------------------------

    # Get list of test files
    fd_list = open(list_of_files)
    files_n_sizes = fd_list.readlines()
    fd_list.close()

    # Create server obj
    server = Server(server_url)

    # Per each test in the file 
    fd_tests = open(tests_file)
    lines = fd_tests.readlines()
    for line in lines:
        total_requests = int(line.split()[0]) 
        requests_per_second = int(line.split()[1])
        byte_range_size = int(line.split()[2])
        initial_job_id = int(line.split()[3])
        file_base = line.split()[4]
    
        # Configure the test
        file_out = file_base+"_requested.json" 
        num_rounds = int(total_requests/requests_per_second)
        num_workers = requests_per_second 
        
        # Configure Rabbit
        num_messages = total_requests
        outfile = file_base+"_recorded.txt"
        
        # Pick random file
        num_files = len(files_n_sizes)
        random_index = random.randint(0,num_files-1)
        #print("num_files: "+str(num_files))
        #print("random_index: "+str(random_index))
        random_file = files_n_sizes[random_index].split()[0]
        file_size = int(files_n_sizes[random_index].split()[1])
        print("random_file: "+str(random_file))
        print("file_size: "+str(file_size))
        
        # Run test
        print("running test: " + str(total_requests) +" "+ str(requests_per_second)+" "+ str(byte_range_size)+ " " + str(initial_job_id) + " " + file_base)
        request_dict = run_test(server, initial_job_id, num_rounds, num_workers, random_file, file_size, byte_range_size, file_out)
        
        ###DEBUG
        ### Read test
        ##remove =False
        #with open(file_out) as json_file: 
        #    request_dict = json.load(json_file)  
        
        ##print ("Requested dictionary")
        ##for key in request_dict:
        ##    print(f'{key:20} : '+ str(request_dict[key]))
            
        # Wait for the data to be sent to the message bus
        ###print("Sleeping...")
        time.sleep(60)
        
        # Query rabbitMQ
        #pdb.set_trace()
        validation_client = ValidationClient(queue, num_messages, remove, timeout, outfile)
        recorded_dict, received_messages = validation_client.start_br()

        ##print ("Recorded dictionary")
        ##for key in recorded_dict:
        ##    print(f'{key:20} : '+ str(recorded_dict[key]))
 

        # Check Requested vs recorded
        num_req_good = num_req_wrong = num_req_missing =0
        for key in request_dict:
            req_filename = request_dict[key][0]
            req_bytes    = request_dict[key][1]
            if key in recorded_dict:
                rec_filename  = recorded_dict[key][0][1:]
                rec_bytes     = recorded_dict[key][1]
                if rec_filename == req_filename and rec_bytes == req_bytes:
                    num_req_good +=1
                else:
                    num_req_wrong +=1
            else:
                num_req_missing +=1
        if(num_req_good + num_req_wrong +num_req_missing != total_requests):
            print("ERROR: sum(num_req_*) doesn't match total_request")
 
        print("*** test: "+file_base + "; num requests good: "+str(num_req_good) + "; num requests wrong: "+str(num_req_wrong)+ "; num requests missing: "+str(num_req_missing))
        
        # Remove if queue is < total_requests
        if remove and num_messages > received_messages and received_messages > 0:
            validation_client = ValidationClient(queue, received_messages, remove, timeout, None)
            whatever, received_messages2 = validation_client.start_br()
            if received_messages > received_messages2:
                print("ERROR while trying to remove shorter queue")

        

if __name__ == "__main__":
    main()


