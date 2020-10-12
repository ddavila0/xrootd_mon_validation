#!/usr/bin/env python3

import pika
import argparse
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import time

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--remove", "-r", help="Remove the messages retrieved from the queue permamently.  Default: Requeue Messages",
                        action="store_true")
    parser.add_argument("--number", "-n", metavar="COUNT", help="Number of messages to retrieve",
                        default=10, type=int)
    parser.add_argument("--timeout", "-t", help="Timeout to stop sonsuming after no new message received",
                        default=3, type=int)
    parser.add_argument("--queue", "-q", default="xrd.wlcg-itb", help="Queue to receive messages")
    parser.add_argument("--out", "-o", help="file to store the output dictionary")

    return parser.parse_args()

class ValidationClient:

    def __init__(self, args):
        self.queue = args.queue
        self.receivedMsgs = 0
        self.targetMsgs = args.number
        self.remove = args.remove
        self.timeout = args.timeout
        if args.out:
            self.outfile = args.out
        else:
            self.outfile = None
        self.timer_id = 0
        self.last_messages = 0
        self.my_dict = {}
    
    
    def print_dictionary(self):
        for key in sorted(self.my_dict):
            print(f'{key:20} : '+ str(self.my_dict[key]))
        if self.outfile:
            with open(self.outfile, 'w') as outfile:
                json.dump(self.my_dict, outfile)

    def push_in_dict(self, body):
        json_dict = json.loads(body)
        crab_id = file_lfn = read_bytes = ""
        read_bytes = -1
        if "CRAB_Id" in json_dict:
            crab_id = json_dict["CRAB_Id"]
        
        if "file_lfn" in json_dict:
            file_lfn = json_dict["file_lfn"]

        if "read_bytes" in json_dict:
            read_bytes = json_dict["read_bytes"]

        self.my_dict[crab_id]=[file_lfn, read_bytes]

    def pretty_print(self, body, index):
        json_dict = json.loads(body)
        #print(json.dumps(json_dict, indent=4, sort_keys=True))
        ts = json_dict["metadata"]["timestamp"] /1000
        ts_hr = time.strftime("%D %H:%M", time.localtime(ts-3600*7))
        print(f'{"index":20} : '+ str(index))
        print(f'{"timestamp":20} : '+ ts_hr)
        for key in ["CRAB_Id", "file_lfn", "read_bytes", "read_single_bytes", "read_vector_bytes"]:
            value=""
            if key in sorted(json_dict):
                value = str(json_dict[key])
            print(f'{key:20} : '+ value)
        print("====================================================")

    def recvMsg(self, channel: pika.channel, method, properties, body):
        self.pretty_print(body, self.receivedMsgs)
        self.push_in_dict(body)
        self.receivedMsgs += 1
        if self.receivedMsgs == self.targetMsgs:
            if self.remove:
                channel.basic_ack(method.delivery_tag, multiple=True)
            else:
                channel.basic_nack(method.delivery_tag, multiple=True, requeue=True)
            channel.stop_consuming()
            self.print_dictionary() 
    def createConnection(self):
        # Load the credentials into pika
        if 'RABBIT_URL' not in os.environ:
            raise Exception("Unable to find RABBIT_URL in environment file, .env")
        
        parameters = pika.URLParameters(os.environ["RABBIT_URL"])
        self.conn = pika.adapters.blocking_connection.BlockingConnection(parameters)

        # Connect to the queue
        self.channel = self.conn.channel()

        # Consume from the queue
        self.channel.basic_consume(self.queue, self.recvMsg)

    def _checkStatus(self):
        """
        Called every X seconds to check the status of the transfer.
        If nothing has happened lately, then kill the connection.
        """
        if self.last_messages == self.receivedMsgs:
            print("Time is out") 
            self.channel.stop_consuming()
            self.print_dictionary() 
        else:
            self.last_messages = self.receivedMsgs
            self.timer_id = self.conn.call_later(self.timeout, self._checkStatus)

    def start(self):
        self.createConnection()

        # Create a timeout
        self.timer_id = self.conn.call_later(self.timeout, self._checkStatus)

        self.channel.start_consuming()
        self.conn.close()
        return self.receivedMsgs

        
        

def main():
    args = parse_args()
    load_dotenv()

    validation_client = ValidationClient(args)
    validation_client.start()
    




if __name__ == "__main__":
    main()

