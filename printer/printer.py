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

def print_simulation(self, index):
    simulation = simulation_proxy.load_simulation(index)

    rgb = simulation['rgb']
    depth = simulation['depth']
    rgb = simulation['rgb_with_contour']

    a = PlotCanvas()

    vtk_filename = simulation_proxy.run_filepath(index, 'elmeroutput0010.vtk')
    vtk_to_plot(a, vtk_filename, 16, True, False, True, None)
    data = np.fromstring(a.tostring_rgb(), dtype=np.uint8, sep='')
    data = data.reshape(a.get_width_height()[::-1] + (3, ))

    a = PlotCanvas()
    vtk_to_plot(a, vtk_filename, 16, True,False,True,None)

    filename = str(index)+'.pdf'

    generator = PDFPrinter(filename, rgb, depth, data, data,
                            simulation['name'], simulation['drag'])
    generator.run(send_to_printer = send_to_printer)
