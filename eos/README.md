# Equation of state

This folder hosts the example implementation of the equation of state workflow for the various workflow engines.

## Logic

The workflow should take an input structure and implement the following:

1. Optimize the geometry of the structure (both cell and atomic positions).
2. Starting from the optimized geometry, create a list of new structures with a range of volumes around the equilibrium.
3. Calculate the energy for each volume using an external code (e.g. Quantum ESPRESSO).
4. Combine results and fit with a Birch-Murnaghan.
