import requests
import logging
import pprint
import os
import sys
from pathlib import Path
from constants import HASH_NOT_FOUND, MAX_FILE_SIZE, WAIT_TIME_SECONDS
from utils import generate_file_hash
from requests_handler import make_request_with_file, make_request_with_hash
import threading


logging.basicConfig(level=logging.DEBUG)


def print_response(responseJSON):
    """ 
    Display the results of a scan. 
    Parameters:
      responseJSON: The JSON response from the server
    """
    key_scan_results = 'scan_results'
    key_scan_details = 'scan_details'
    key_def_time = 'def_time'
    key_threat_found = 'threat_found'
    key_scan_result = 'scan_result_i'
    key_overall_status = 'scan_all_result_a'

    # look for key_scan_results
    if key_scan_results in responseJSON:
        print(f'overall_status: {responseJSON[key_scan_results][key_overall_status]}')
        for key, value in responseJSON[key_scan_results][key_scan_details].items():
            message = f'engine: {key} \nthreat_found:{value[key_threat_found]}\nscan_result: {value[key_scan_result]}\ndef_time: {value[key_def_time]}'
            print(message)
        print('\nEND')


if __name__ == '__main__':
    file_path = Path(input("Please enter file name or path: ").strip())
    print(file_path.name)

    if not os.path.exists(file_path):
        print('File does not exist at path: ', file_path)
        sys.exit()
    else:
        # Check file size to make sure it does not exceed the max file size
        if os.stat(file_path).st_size > MAX_FILE_SIZE:
            print('File size must be less than or equal to ', MAX_FILE_SIZE)
            sys.exit()
        file_hash = generate_file_hash(file_path)
        response = make_request_with_hash(file_hash, None)

        # check the status code of the response and process the result accordingly
        if response.status_code != requests.codes.ok:
            json_response = response.json()
            if json_response['error']['code'] == HASH_NOT_FOUND:
                # There is no previously cached result for the file so send a upload request
                response = make_request_with_file(file_path)
                if response.status_code == requests.codes.ok:
                    server_response = response.json()
                    # save data_id for future requests
                    if "data_id" in server_response:
                        data_id = server_response['data_id']
                        # create a thread to continuously call the web api to query the scan results using the data_id
                        api_caller_event = threading.Event()
                        while not api_caller_event.wait(WAIT_TIME_SECONDS):
                            results = make_request_with_hash('', data_id).json()
                            if results['scan_results']['progress_percentage'] == 100:
                                # stop the thread when scan results have been obtained
                                api_caller_event.set()
                                print_response(results)
        else:
            print_response(response.json())
