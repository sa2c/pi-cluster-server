import os
import sys
__server_dir = os.path.join(
    os.path.dirname(os.path.abspath(os.path.join(__file__, '..'))), 'client')
sys.path.append(__server_dir)

import time
import requests
from subprocess import call
from settings import cluster_address

print_queue_url = f'{cluster_address}/print_queue'


def get_print_finished_url(sim_id):
    return f'{cluster_address}/print_queue/done/{sim_id}'


def get_print_pdf_url(sim_id):
    return f'{cluster_address}/simulations/{sim_id}/postcard.pdf'


def get_print_queue():
    print("Fetching print queue")
    response = requests.get(print_queue_url, allow_redirects=True)
    return response.json()['jobs']


def download_pdf(sim_id):
    url = get_print_pdf_url(sim_id)
    print(f"Downloading {url}")
    response = requests.get(url, allow_redirects=True)

    filename = f'/tmp/cache{sim_id}.pdf'

    with open(filename, 'wb') as f:
        f.write(response.content)

    return filename


def mark_as_complete(sim_id):
    url = get_print_finished_url(sim_id)
    response = requests.post(url, allow_redirects=True)

def print_pdf(filename):
    call(['lpr', '-o', 'landscape', filename])


def process_pdf(sim_id):
    filename = download_pdf(sim_id)
    print_pdf(filename)

    mark_as_complete(sim_id)

def process_queue():
    for sim_id in get_print_queue():
        process_pdf(sim_id)


def poll_server(interval=10):
    while True:
        process_queue()
        time.sleep(interval)


if __name__ == '__main__':
    poll_server()
