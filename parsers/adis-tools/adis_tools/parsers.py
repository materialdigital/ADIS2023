import numpy

from xmlschema import XMLSchema
from qe_tools import CONSTANTS

from ase import Atoms
from importlib.resources import files

from . import schemas


def parse_pw(xml_file):
    """Parse a Quantum Espresso XML output file."""

    xml_dict = XMLSchema(files(schemas) / 'qes_230310.xsd').to_dict(xml_file)

    cell = numpy.array(
        [ v for v in xml_dict['output']['atomic_structure']['cell'].values()]
    ) * CONSTANTS.bohr_to_ang
    symbols = [el['@name'] for el in xml_dict['output']['atomic_structure']['atomic_positions']['atom']]
    positions = numpy.array(
        [el['$'] for el in xml_dict['output']['atomic_structure']['atomic_positions']['atom']]
    ) * CONSTANTS.bohr_to_ang

    atoms = Atoms(
        cell=cell,
        positions=positions,
        symbols=symbols,
        pbc=True,
    )
    return {
        'ase_structure': atoms,
        'energy': xml_dict['output']['total_energy']['etot'] * 2 * CONSTANTS.ry_to_ev,
        'forces': (
            numpy.array(xml_dict['output']['forces']['$']).reshape(xml_dict['output']['forces']['@dims'])
            * 2 * CONSTANTS.ry_to_ev / CONSTANTS.bohr_to_ang
        )
    }
