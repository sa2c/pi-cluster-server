from flask import Flask, request, render_template, send_from_directory
from flask_cors import CORS

from werkzeug.serving import run_simple
from werkzeug.datastructures import FileStorage

from snapshots import snapshots

import glob
import json
import simulation_proxy

def create_app():
    app = Flask(__name__)

    params = {
        'WTF_CSRF_ENABLED': False,
        'DEBUG': True,
    }

    app.config['WTF_CSRF_ENABLED'] = False

    app.config.update(params)

    return app


app = create_app()

# Enable cross-site scripting
CORS(app)


# Static routes for simulation data
@app.route('/snapshots/<path:filename>')
def custom_static(filename):
    return send_from_directory(snapshots.dir(), filename)

@app.route('/snapshots/')
def snapshot_list():
    json_string = json.dumps({'snapshots' : {
        s_id : snapshot_data(request.host_url, s_id)
        for s_id in snapshots.ids()
    }})

    return json_string

@app.route('/dispatch/', methods=['POST'])
def snapshot_dispatch():
    # construct a simulation object, it has keys: contour, snapshot-id, name, email
    simulation = request.json

    # when I save data, I need to save also:
    rgb, rgb_with_contour, depth, background, contour-orig
    # ['name', 'email', 'rgb', 'rgb_with_contour', 'depth', 'background', 'contour', 'contour-orig'])

    # rgb_with_contour
    breakpoint()

    id = simulation_proxy.dispatch(simulation)

    return id

def snapshot_data(host_url, id):
    return {'image' : f'{host_url}/snapshots/{id}/image.png',
            'depth-image' : f'{host_url}/snapshots/{id}/depth.png',
            'contour' : {'points' : snapshots.get_contour(id),
                         'offset' : {'x' : 0,
                                     'y' : 0}}}


def run_app():
    run_simple(hostname='0.0.0.0',
               port=8374,
               application=app,
               use_reloader=True,
               use_debugger=True,
               threaded=True)

if __name__ == '__main__':
    run_app()
