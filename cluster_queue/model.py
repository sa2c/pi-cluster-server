from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, PickleType, Float
from sqlalchemy.sql import select
import status_codes
import numpy as np
import utils
import settings
import os
import subprocess

engine = create_engine('sqlite:///db.sql', echo=True)

# Creates tables if the don't exist
metadata = MetaData()

simulations = Table('runs', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('name', String),
                    Column('email',String),
                    Column('rgb', PickleType ),
                    Column('rgb_with_contour', PickleType),
                    Column('depth', PickleType),
                    Column('background', PickleType),
                    Column('contour', PickleType),
                    Column('drag', Float),
                    Column('status', Integer)
)

metadata.create_all(engine)

def create_simulation(simulation):
    insert = simulations.insert().values(
        name = simulation['name'],
        email = simulation['email'],
        rgb = simulation['rgb'],
        rgb_with_contour = simulation['rgb_with_contour'],
        depth = simulation['depth'],
        background = simulation['background'],
        contour = simulation['contour'],
        status = status_codes.SIMULATION_WAITING
        )

    result = engine.execute(insert)

    return result.lastrowid

def all_simulations():
    sql = simulations.select()

    results = engine.execute(sql)

    return results_to_simulation(results)

def waiting_simulations():
    return simulations_by_status(status_codes.SIMULATION_WAITING)

def set_started(sim_id):
    set_simulation_status(sim_id, status_codes.SIMULATION_STARTED)

def simulations_by_status(status):
    sql = simulations.select().where(simulations.c.status == status)

    results = engine.execute(sql)

    sims = results_to_simulation(results)

    # results_to_simulation returns a dictionary with IDs as keys, we just want a list
    sims = [ sims[key]['id'] for key in sims.keys() ]

    return sims

def set_simulation_status(sim_id, status):
    sql = simulations.update().where(simulations.c.id == sim_id).values(status = status_codes.SIMULATION_STARTED)

    results = engine.execute(sql)

    return results

def results_to_simulation(results):

    results = [ dict(row) for row in results ]

    # index by ID
    results = { row['id'] : row for row in results }

    return results


def get_simulation(id):
    sql = simulations.select().where(simulations.c.id == id)

    results = engine.execute(sql)

    results = results_to_simulation(results)

    result = results[int(id)]

    return result

def write_outline(filename, outline):
    "Takes an outline as an array and saves it to file outline file"
    outline = np.array(outline)
    flipped_outline = np.copy(outline.reshape((-1, 2)))
    flipped_outline[:, 1:] = 480 - flipped_outline[:, 1:]
    np.savetxt(filename, flipped_outline, fmt='%i %i')


def run_simulation(sim_id, hostfilename):

    simulation = get_simulation(sim_id)

    set_started(sim_id)

    run_dir = run_directory(sim_id)

    utils.ensure_exists(run_dir)

    outline_coords = f'{run_dir}/outline-coords.dat'

    write_outline(outline_coords, simulation['contour'])

    outfile = f'{run_dir}/output'

    command = settings.cfdcommand.format(
        id=sim_id,
        ncores=settings.nodes_per_job*settings.cores_per_node,
        hostfile=hostfilename,
        output=outfile
    )

    process = subprocess.Popen(command, shell=True)

    return process

def set_drag(sim_id, drag):
    sql = simulations.update().where(simulations.c.id == sim_id).values(drag = drag)

    results = engine.execute(sql)

    return results


def run_directory(index):
    directory = f'{settings.root_dir}/simulations/{index}'.format(index=index)

    utils.ensure_exists(directory)

    return directory

def outline_coords_file(sim_id):
    return '{dir}/outline-coords.dat'.format(dir=run_directory(sim_id))
