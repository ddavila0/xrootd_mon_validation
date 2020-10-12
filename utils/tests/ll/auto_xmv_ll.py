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


def request_multi_byte_range(server, requests_per_job, minutes_between_requests, random_file, file_size, byte_range_size, appinfo):
    s = Server(server)
    s.only_open(random_file, appinfo)    
    for i in range(0, requests_per_job):
        seek = random.randint(0, file_size - byte_range_size)
        byte_array, status = s.only_fetch_byte_range(seek, seek+byte_range_size)
        print("appinfo: "+appinfo+", "+"status: "+str(status) + "bytes_read: "+str(len(byte_array)))
        if status == -1:
            print("### ERROR: Cannot open file: "+ random_file +" at server: "+server.server_url)
        else:
            assert(len(byte_array) == byte_range_size)
        
        print("job: "+appinfo+ "requested N bytes and now going to sleep")
        time.sleep(60*minutes_between_requests)
    s.only_close()
    print("done with: "+appinfo)


def main():
    #--------------------------------------------------------
    # Args
    #--------------------------------------------------------
    if len(sys.argv) == 2:
        tests_file = sys.argv[1]
    else:
        print("expected: xmv <tests_file>")
        print("format of tests_file:")
        print("{test_name: ll_xx, tests: {job_id_0 : [request_per_job, minutes_between_requests, byte_range_size], job_id_1 : [request_per_job, , ...], ...}}")
        sys.exit(1)
    
    #---------------------------------------------------------
    # Fixed Config
    #---------------------------------------------------------
    server_url="root://fermicloud157.fnal.gov:1094"
    list_of_files = "ll_list_of_files.txt"
    #---------------------------------------------------------
    # Rabbit
    queue="xrd.wlcg-itb"
    remove = False
    timeout= 5
    load_dotenv()
    #---------------------------------------------------------

    # Get list of test files
    fd_list = open(list_of_files)
    files_n_sizes = fd_list.readlines()
    num_files = len(files_n_sizes)
    fd_list.close()

    # Per each test in the file 
    fd_tests = open(tests_file)
    test_dict = json.load(fd_tests)
    fd_tests.close()
    file_base  = test_dict["test_name"]
    tests_dict = test_dict["tests"]
    total_jobs = len(tests_dict)
    print("total_jobs: "+str(total_jobs))
    
    # Configure the test
    file_out = file_base+"_requested.json" 

    # Configure Rabbit
    num_messages = total_jobs
    outfile = file_base+"_recorded.txt"
    
    request_dict = {}
    process_list = []
   
    for key in tests_dict:
        job_id              = int(key)
        requests_per_job            = int(tests_dict[key][0])
        minutes_between_requests    = int(tests_dict[key][1])
        byte_range_size             = int(tests_dict[key][2])
         
        print("job_id: "+str(job_id))
        print("requests_per_job: "+str(requests_per_job))
        print("minutes_between_requests: "+str(minutes_between_requests))
        print("byte_range_size: "+str(byte_range_size))
        
       
        # Pick random file
        random_index = random.randint(0,num_files-1)
        random_file = files_n_sizes[random_index].split()[0]
        file_size = int(files_n_sizes[random_index].split()[1])
        
        job_id_s = f'{job_id:03}'
        appinfo = job_id_s+"_https://glidein.cern.ch/1-519/0:0:ddavila:crab:TEST:0:0:TEST:TEST-TEST_1"
        request_dict[job_id_s]=[random_file, requests_per_job * byte_range_size, requests_per_job, byte_range_size]
        p = Process(target=request_multi_byte_range, args=(server_url, requests_per_job, minutes_between_requests, random_file, file_size, byte_range_size, appinfo))
        p.start()
        process_list.append(p)
        print("queued job_id: "+str(job_id))
        #time.sleep(5)    
        job_id +=1

    #Wait for the processes to finish
    for p in process_list:
        p.join()
    
    # Write requested records
    with open(file_out, 'w') as writefile:
        json.dump(request_dict, writefile)
 
    ###DEBUG
    ### Read test
    #remove =False
    #with open(file_out) as json_file: 
    #    request_dict = json.load(json_file)  
    
    print ("Requested dictionary")
    for key in request_dict:
        print(f'{key:20} : '+ str(request_dict[key]))
    
    #exit(0)    
    # Wait for the data to be sent to the message bus
    print("Sleeping...")
    time.sleep(60)
    
    # Query rabbitMQ
    #pdb.set_trace()
    validation_client = ValidationClient(queue, num_messages, remove, timeout, outfile)
    recorded_dict, received_messages = validation_client.start_br()

    print ("Recorded dictionary")
    for key in recorded_dict:
        print(f'{key:20} : '+ str(recorded_dict[key]))
 
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
    if(num_req_good + num_req_wrong +num_req_missing != len(request_dict)):
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


