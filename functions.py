import os

from ase import Atoms
from ase.io import write
from adis_tools.parsers import parse_pw
import matplotlib.pyplot as plt


def generate_structures(
        structure: Atoms,
        strain_lst: list
    ) -> list[Atoms]:

    structure_lst = []

    for strain in strain_lst:
        structure_strain = structure.copy()
        structure_strain.set_cell(
            structure_strain.cell * strain**(1/3), 
            scale_atoms=True
        )
        structure_lst.append(structure_strain)

    return structure_lst


def append_to_list(lst: list, item: float):
    lst.append(item)


def split_string(string: str, character: str) -> list:
    return string.split(character)


def write_input(input_dict, working_directory=".", return_string=False):

    filename = os.path.join(working_directory, 'input.pwi')

    os.makedirs(working_directory, exist_ok=True)

    write(
        filename=filename, 
        images=input_dict["structure"], 
        Crystal=True, 
        kpts=input_dict["kpts"], 
        input_data={
            'calculation': input_dict["calculation"],
            'occupations': 'smearing',
            'degauss': input_dict["smearing"],
        }, 
        pseudopotentials=input_dict["pseudopotentials"],
        tstress=True, 
        tprnfor=True
    )

    if return_string:
        with open(filename) as f:
            return f.read()


def collect_output(working_directory="."):
    output = parse_pw(os.path.join(working_directory, 'pwscf.xml'))
    return {
        "structure": output['ase_structure'],
        "energy": output["energy"],
        "volume": output['ase_structure'].get_volume(),
    }


def plot_energy_volume_curve(volume_lst, energy_lst):
    plt.plot(volume_lst, energy_lst)
    plt.xlabel("Volume")
    plt.ylabel("Energy")
    plt.savefig("evcurve.png")
