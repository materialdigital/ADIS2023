# Quantum Espresso Workflow
The structure optimization of an Aluminium bulk structure followed by the calculation of the bulk modulus by computing the energy for different volumes is implemented in three different workflow frameworks, [Aiida](https://aiida.net), [jobflow](https://materialsproject.github.io/jobflow/) and [pyiron_base](https://pyiron.org). 

Test it on: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/materialdigital/ADIS2023/HEAD)

## Explanation 
* `adis_tools` - quantum espresso parser independent of the workflow frameworks. 
* `aiida_qe_basic` - simple Aiida interface.
* `espresso/pseudo/Al.pbe-n-kjpaw_psl.1.0.0.UPF` - This is the pseudo potential for qunatum espresso. By placing it in `~/espresso/pseudo`, it is automatically detected by quantum espresso.
* `aiida.ipynb` - workflow implemented in [Aiida](https://aiida.net)
* `environment.yml` - Conda environment to define the dependencies.
* `jobflow.ipynb` - workflow implemented in [jobflow](https://materialsproject.github.io/jobflow/)
* `postBuild` - script to install `aiida_qe_basic` in the mybinder environment.
* `pyiron_base.ipynb` - workflow implemented in [pyiron_base](https://pyiron.org) 
