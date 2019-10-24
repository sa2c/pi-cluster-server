from images_to_pdf.pdfgen import PDFPrinter
import simulation_proxy
import requests
from settings import cluster_address

print_queue_url = f'{cluster_address}/print_queue'

def get_print_finished_url(sim_id):
    return f'{cluster_address}/print_queue/done/{sim_id}'

def process_queue(printfunc):
    response = requests.get(print_queue_url)
    print_queue = response.json()['jobs']
    for item in print_queue:
        printfunc(item)
