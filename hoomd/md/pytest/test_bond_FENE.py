import hoomd
import pytest
import numpy as np


def get_bond_params():
    k = [30.0, 25.0, 20.0]
    r0 = [1.6, 1.7, 1.8]
    epsilon = [0.9, 1.0, 1.1]
    sigma = [1.1, 1.0, 0.9]
    return zip(k, r0, epsilon, sigma)


@pytest.mark.parametrize("bond_params_tuple", get_bond_params())
def test_before_attaching(bond_params_tuple):
    k, r0, epsilon, sigma = bond_params_tuple
    bond_params = dict(k=k, r0=r0, epsilon=epsilon, sigma=sigma)
    bond_potential = hoomd.md.bond.FENE()
    bond_potential.params['bond'] = bond_params

    for key in bond_params.keys():
        np.testing.assert_allclose(bond_potential.params['bond'][key],
                                   bond_params[key],
                                   rtol=1e-6)


@pytest.mark.parametrize("bond_params_tuple", get_bond_params())
def test_after_attaching(two_particle_snapshot_factory,
                         simulation_factory,
                         bond_params_tuple):
    snap = two_particle_snapshot_factory(d=0.969, L=5)
    if snap.exists:
        snap.bonds.N = 1
        snap.bonds.types = ['bond']
        snap.bonds.typeid[0] = 0
        snap.bonds.group[0] = (0, 1)
    sim = simulation_factory(snap)

    k, r0, epsilon, sigma = bond_params_tuple
    bond_params = dict(k=k, r0=r0, epsilon=epsilon, sigma=sigma)
    bond_potential = hoomd.md.bond.FENE()
    bond_potential.params['bond'] = bond_params

    integrator = hoomd.md.Integrator(dt=0.005)

    integrator.forces.append(bond_potential)

    nvt = hoomd.md.methods.Langevin(kT=1, filter=hoomd.filter.All(), alpha=0.1)
    integrator.methods.append(nvt)
    sim.operations.integrator = integrator

    sim.run(0)
    for key in bond_params.keys():
        np.testing.assert_allclose(bond_potential.params['bond'][key],
                                   bond_params[key],
                                   rtol=1e-6)
