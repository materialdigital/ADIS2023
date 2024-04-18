from ase.io import write

from aiida import orm, engine
from aiida.parsers import Parser
from aiida.common import datastructures

from adis_tools.parsers import parse_pw


class PwCalculation(engine.CalcJob):

    @classmethod
    def define(cls, spec):
        """Define the specification."""
        super().define(spec)

        spec.inputs['metadata']['options']['parser_name'].default = 'qe.pw'

        spec.input('structure', valid_type=orm.StructureData)
        spec.input('parameters', valid_type=orm.Dict)
        spec.input('pseudopotentials', valid_type=orm.Dict)

        spec.output('structure', valid_type=orm.StructureData)
        spec.output('properties', valid_type=orm.Dict)

    def prepare_for_submission(self, folder):
        """Create the input files from the input nodes passed to this instance of the `CalcJob`.

        :param folder: an `aiida.common.folders.Folder` to temporarily write files on disk
        """

        with folder.open('input.pwi', 'w') as handle:
            write(
                handle, 
                self.inputs.structure.get_ase(), 
                kpts=(3, 3, 3), 
                input_data=self.inputs.parameters.get_dict(), 
                pseudopotentials=self.inputs.pseudopotentials.get_dict(),
                tstress=True, 
                tprnfor=True
            )

        codeinfo = datastructures.CodeInfo()
        codeinfo.cmdline_params = ['-in', 'input.pwi']
        codeinfo.code_uuid = self.inputs.code.uuid

        calcinfo = datastructures.CalcInfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.retrieve_list = ['pwscf.xml']

        return calcinfo


class PwParser(Parser):
    """Parser class for parsing output of pw.x."""

    def parse(self, **kwargs):
        """Parse the Quantum ESPRESSO outputs."""

        with self.retrieved.open('pwscf.xml', 'r') as handle:
            xml_outputs = parse_pw(handle)

        self.out('structure', orm.StructureData(ase=xml_outputs['ase_structure']))
        self.out('properties', orm.Dict({
            'energy': xml_outputs['energy'],
            'volume': xml_outputs['ase_structure'].get_volume(),
        }))
