import requests
import hashlib
import logging
import pprint
import os
from requests.exceptions import HTTPError


API_KEY = "8144bd2eb424525853b30e0d3fd1792c"
PASSWORD = "Kera@123456789"
BASE_URL = "https://api.metadefender.com/"
HASH_NOT_FOUND = 404003
server_response = {}

logging.basicConfig(level=logging.DEBUG)


def generate_file_hash(path):
    """ Generate the hash of the given file using MD5 """
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(path, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()


def generate_payload():
    pass


def generate_url_and_params(hash, file_path):
    if hash:
        url = f'{BASE_URL}v4/hash/{hash}'
        headers = {'apikey': API_KEY}
        files = None
    else:
        url = f'{BASE_URL}v4/file'
        headers = {'apikey': API_KEY,
                   'content-type': 'application/octet-stream'}
        files = {'file': open(file_path, 'rb')}
    return(url, headers,files)


def make_request(hash, file_path):
    url, headers, files = generate_url_and_params(hash, file_path)
    try:
        if files is None:
            response = requests.get(
                url,
                headers=headers,
            )
        else:
            with open(file_path, 'rb') as f:
                response = requests.post(
                    url,
                    data= f,
                    headers=headers
                )
        json_response = response.json()
        return response
    except HTTPError as http_err:
        print(f'\n HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'\n Other error occurred: {err}')  # Python 3.6
    else:
        print(f'\n Success! \n {json_response}')


def print_response(response):
    logging.debug(response)


file_path = input("Please enter file name or path: ")

file_hash = generate_file_hash(file_path)

response = make_request(file_hash, None)

# check the status code of the response
if response.status_code != 200:
    json_response = response.json()
    if json_response['error']['code'] == HASH_NOT_FOUND:
        # There is no previously cached result for the file so send a upload request
        response = make_request(None, file_path)
        if response.status_code == requests.codes.ok:
            server_response = response.json()
            pprint.pprint(server_response)
else:
    pprint.pprint(response.json())




