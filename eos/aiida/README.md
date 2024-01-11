# EOS - AiiDA example

## Setup

### Environment

First, create a conda environment from the `environment.yml` file:

```
mamba env create -f environment.yml
```

This will install `aiida-core`, a binary for Quantum ESPRESSO, and some other tools like `ase` and `jupyterlab` into the `adis-aiida` environment.
Once complete, activate the environment and start the rabbitmq service:

```
mamba activate adis-aiida
rabbitmq-server -detached
```

I've written a basic parser for QE and added it to the `adis-tools` package:

```
pip install -e ../../parsers/adis-tools
```

Due to the "plugin nature" of AiiDA, all calculation jobs and parsers must be added to a package and assigned an entry point.
A very basic example for the `pw.x` binary of Quantum ESPRESSO has been added in the `aiida_qe_basic` package:

```
pip install -e aiida_qe_basic
```

### Profile

Next, let's set up a testing profile:

```
verdi profile setup core.sqlite_dos -n --profile test --email no@email.com
```

And run the cells in `qe-setup.ipynb`.
These will set up the `localhost` computer and `pw` code, then do a test run.
