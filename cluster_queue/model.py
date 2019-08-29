from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, PickleType
from sqlalchemy.sql import select

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
                    Column('contour', PickleType)
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
        contour = simulation['contour']
        )

    result = engine.execute(insert)

    return result.lastrowid

def all_simulations():
    sql = simulations.select()

    results = engine.execute(sql)

    columns = ['name', 'email']

    return results_to_simulation(results)

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
