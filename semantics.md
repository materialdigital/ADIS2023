# Semantics

## Common language and definitionns

### Parsers

Wikipedia definition: https://en.wikipedia.org/wiki/Parsing#Parser

A parser is a tool that takes input data and converts the contents into **serialized** or **serializable** data using an established format or schema.
Immediately, we can consider two types of input data:

* Text: the `stdout` of VASP, an XML file, ...
* Software/language-specific data structures: a float, a Python `dict`, FORTRAN array, ...

One can develop parsers for both the inputs and outputs of a software package or code.
Still, some distinctions between the two can be made:

#### Output parser

* Typically does not have to be complete. The `stdout` of a code often will contain information that does not require parsing.
  Moreover, we might not be interested in _all_ of the output provided (e.g. the difference in integrated charge density for each SCF step.)
* Typically shouldn't be able to _generate_ the data that we want to parse.

#### Input parser

* Typically _does_ have to be complete, or _as complete_ as the parser of the software we are running.
  If we want to understand how a certain calculation was run, we need to know all of the inputs.
  Exceptions here are comments that are not processed by the software.
* Typically _should_ be able to generate the data that we want to parse.
  That is, if we consider this to be part of the functions of a parser.

  - `serialized data`: JSON, XML, yml etc.
  - `serializable data`: python dictionary (entries must be also serializable), python list, numbers etc.

## Software-specific semantics
### AiiDA

- `Work chain`: A work chain is one of the two types of workflows that AiiDA (currently) offers. Its defining feature (in contrast with work _functions_) is that it allows for checkpoints. The work chain is defined as a `class`:

    ```python
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
    ```

    Let's look at the various components:
    
    * All work chains start with the `define` method and calling the corresponding method of its parent class.

    ```python
        @classmethod
        def define(cls, spec):
            """Specify inputs and outputs."""
            super().define(spec)
    ```

    * All inputs and outputs are defined as [ports](https://aiida.readthedocs.io/projects/aiida-core/en/latest/topics/processes/usage.html?highlight=port%20namespace#ports-and-port-namespaces):

    ```python
        spec.input("code", valid_type=orm.Code)
        spec.input("structure", valid_type=orm.StructureData)
        spec.input("scale_factors", valid_type=orm.List)

        ...

        spec.output("eos_dict", valid_type=orm.Dict)
    ```
           
    * The logic of the workflow is specified in the _outline_:

    ```python
            spec.outline(
                cls.run_eos,
                cls.results,
            )
    ```
    
    and is defined using methods specified on the class. These methods are then executed according to the logic of the outline. In between the execution, the work chain is checkpointed; i.e. the daemon will wait until other processes in the "context" are finished. The usual use case is that you want to run a list of e.g. Quantum ESPRESSO calculations in the `run_eos` step before executing the next step.
    
    More information in the documentation: https://aiida.readthedocs.io/projects/aiida-core/en/latest/topics/workflows/concepts.html#work-chains

- [`Builder`](https://aiida.readthedocs.io/projects/aiida-core/en/latest/topics/processes/usage.html?highlight=builder#process-builder): The process builder is a tool that helps you "build" the inputs of a calculation job or work chain. Say you want to run the EoS work chain. One way to run the work chain would be:

    ```python
    engine.run(EquationOfState, code=orm.load_code('qe-7.2-pw@localhost'),
               structure=si_structure,
               scale_factors=orm.List([0.9, 0.95, 1.0, 1.05, 1.1]))
    ```
    
    However, this means you would need to _know_ what the inputs of the process are, their types, etc. The builder makes this easier, since you can tab-complete the inputs. Moreover, you can get information on each of the inputs: 

    ```python
    builder.code?

    Type:        property
    String form: <property object at 0x7f04c8ce1c00>
    Docstring:
        "name": "code",
        "required": "True"
        "non_db": "False"
        "valid_type": "<class 'aiida.orm.nodes.data.code.abstract.AbstractCode'>"
        "help": "The Code to use for this job.",

        builder.structure?
    ```

- `profile`: A profile is similar to a "project" in a sense. Each profile defines:

    * The user: this is stored in a separate table in the database, and every node is linked to a user.
    * The storage, which consists of two components:
        * PostgreSQL database
        * Repository (i.e. files), stored as a [disk objectstore](https://pypi.org/project/disk_objectstore/).

    Typically you would only need one profile and never look back. However, I find it useful to have a `dev` profile for testing things and then a `prod` profile for the actual runs I want to keep.
    
    Another note here is that since profiles share the same AiiDA install, they have the same Python environment. What _I_ typically call an [AiiDA project](https://github.com/aiidateam/aiida-project) is a Python environment with a corresponding structured directory. This is because for different projects, I typically would install different plugin packages, so I don't want to use one environment for all my projects. Especially when I'm developing in one project, I don't want this to mess up the runs that are active in other one. So each project will have its own environment, and in one project I will have multiple profiles in case I want to separate the data.

- port: Ports are basically the definition of the in- and outputs of a process. Compared to e.g. the inputs of a function, the process ports allow you to specify more details on the input:

    * Validation: You can specify the "data type" of the input nodes (with the `valid_type` argument), but also do more validation by specifying a `validator` to check not only the types but also the value.
    * Documentation: By adding the `help` argument, you can explain the input/output. This can be used to automatically generate documentation, see e.g. [here](https://aiida-quantumespresso.readthedocs.io/en/latest/topics/calculations/pw.html).
    * Specify if an input is metadata or not. Metadata is stored in the database (as an attribute on the node), but is not a node in itself. An example is the Slurm account you want to run the calculation with.

    Besides simple ports, you also can specify _port namespaces_. These allow you to define multiple ports in one port namespace (think of it like a dictionary).


    More links:

    * https://aiida.readthedocs.io/projects/aiida-core/en/latest/topics/processes/usage.html?highlight=port%20namespace#ports-and-port-namespaces
    * https://plumpy.readthedocs.io/en/latest/tutorial.html#defining-inputs-and-outputs

- `context`: The context of a work chain is in essence a dictionary that can be used to pass information between the steps (defined as separate methods) of the work chain.

- `daemon`: This is explained quite well and succinctly in the documentation: https://aiida.readthedocs.io/projects/aiida-core/en/latest/topics/daemon.html

- `attributes/extras`: Every node stores data in the database in two ways:

    * attributes: once a node is stored, the attributes become immutable, so can never be changed from this point.
    * extras: this is data you can still add to/change on a node even after it is stored.


    Also relevant: https://aiida.readthedocs.io/projects/aiida-core/en/latest/topics/processes/concepts.html?highlight=attributes#process-sealing
    

### Automate

- `Job`: A class that allows to delay the execution of a function. The outputs of jobs are stored in databases.
- `Flow`: Class that contains Jobs and other Flows. Jobs and Flows are typically connected via the outputs of individual jobs that are inputs of other jobs (A Flow can be represented as a directed, acyclic graph with the jobs as nodes)
- `Maker`: Class (typically a dataclass) to generate a Job or Flow in a convenient way 
- `Response`: Class to replace a job with another job or flow during the run time (also additions and detours are possible) (Use case: structure optimization changes a structure so drastically that the space group changes, i.e. it is not known how many displacement runs one would need to perform in a harmonic phonon run before the optimization has taken place)
- `Generator`: way to create an Input Set (in VASP: INCAR parameters, kpoint settings etc. ) for a computation. Additional logic was needed to adapt input sets to structures that have been changed during the workflow (e.g., volume of the structure could chance) (will be connected to the pymatgen input sets again in the future, under active development)

### pyiron
