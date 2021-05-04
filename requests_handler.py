import requests
import logging
import pprint
from requests.exceptions import HTTPError
from constants import BASE_URL, HASH_NOT_FOUND
from dotenv import load_dotenv
import os
logging.basicConfig(level=logging.DEBUG)

# load environment variable from the .env file to the os.environ dictionary
load_dotenv()


def make_request_with_hash(hash, data_id=None):
    """ 
    Make request with the hash value of a given file to see if the scan result is already available in 
    the server

    Parameters:
      hash: The hash value of the file. Can be any of the following:
      SHA256,SHA1,MD5, etc
    """
    try:
        if data_id is None:
            url = f'{BASE_URL}v4/hash/{hash}'
        else:
            url = f'{BASE_URL}v4/file/{data_id}'
        headers = {'apikey': os.environ.get('API_KEY')}
        response = requests.get(
            url,
            headers=headers,
        )
        return response
    except HTTPError as http_err:
        print(f'\n HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'\n Other error occurred: {err}')  # Python 3.6
    else:
        print(f'\n Success! \n {json_response}')


def make_request_with_file(file_path):
    """ 
    Make request with the file when the the scan result of a given file is not available.

    Parameters:
      file_path: The path of the file to be uploaded to the server
    """
    try:
        url = f'{BASE_URL}v4/file'
        headers = {'apikey': os.environ.get('API_KEY'),
                   'content-type': 'application/octet-stream'}
        # files = {'file': open(file_path, 'rb')}
        with open(file_path, 'rb') as f:
            response = requests.post(
                url,
                data=f,
                headers=headers
            )
        return response
    except HTTPError as http_err:
        print(f'\n HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'\n Other error occurred: {err}')  # Python 3.6
    else:
        print(f'\n Success! \n {json_response}')