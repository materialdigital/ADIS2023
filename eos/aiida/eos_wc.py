from aiida import orm

from aiida import engine
from aiida_quantumespresso.workflows.pw.base import PwBaseWorkChain

@engine.calcfunction
def rescale_list(structure: orm.StructureData, factor_list: orm.List):

    scaled_structure_dict = {}

    for index, scaling_factor in enumerate(factor_list.get_list()):

        ase_structure = structure.get_ase()

        new_cell = ase_structure.get_cell() * scaling_factor
        ase_structure.set_cell(new_cell, scale_atoms=True)

        scaled_structure_dict[f'structure_{index}'] = orm.StructureData(ase=ase_structure)

    return scaled_structure_dict


@engine.calcfunction
def create_eos_dictionary(**kwargs) -> orm.Dict:
    eos = {
        label: (result['volume'], result['energy'], result['energy_units'])
        for label, result in kwargs.items()
    }
    return orm.Dict(eos)


class EquationOfState(engine.WorkChain):
    """WorkChain to compute Equation of State using Quantum ESPRESSO."""

    @classmethod
    def define(cls, spec):
        """Specify inputs and outputs."""
        super().define(spec)
        spec.input("code", valid_type=orm.Code)
        spec.input("structure", valid_type=orm.StructureData)
        spec.input("scale_factors", valid_type=orm.List)

        spec.outline(
            cls.run_eos,
            cls.results,
        )
        spec.output("eos_dict", valid_type=orm.Dict)

    def run_eos(self):

        calcjob_dict = {}

        for label, rescaled_structure in rescale_list(self.inputs.structure, self.inputs.scale_factors).items():

            builder = PwBaseWorkChain.get_builder_from_protocol(
                code=self.inputs.code,
                structure=rescaled_structure,
                protocol='fast'
            )
            calcjob_dict[label] = self.submit(builder)

        self.ctx.labels = list(calcjob_dict.keys())

        return calcjob_dict

    def results(self):

        self.report(self.ctx)

        eos_results = {
            label: self.ctx[label].outputs['output_parameters'] for label in self.ctx.labels
        }
        eos_dict = create_eos_dictionary(**eos_results)
        self.out('eos_dict', eos_dict)
