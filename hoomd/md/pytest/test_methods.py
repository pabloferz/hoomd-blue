import hoomd
import pytest
import numpy
import itertools
from copy import deepcopy


def test_brownian_attributes():
    """Test attributes of the Brownian integrator before attaching."""
    all_ = hoomd.filter.All()
    constant = hoomd.variant.Constant(2.0)
    brownian = hoomd.md.methods.Brownian(filter = all_, kT=constant)

    assert brownian.filter is all_
    assert brownian.kT is constant
    assert brownian.alpha is None

    type_A = hoomd.filter.Type(['A'])
    brownian.filter = type_A
    assert brownian.filter is type_A

    ramp = hoomd.variant.Ramp(1, 2, 1000000, 2000000)
    brownian.kT = ramp
    assert brownian.kT is ramp

    brownian.alpha = 0.125
    assert brownian.alpha == 0.125


def test_brownian_attributes_attached(simulation_factory,
                                      two_particle_snapshot_factory):
    """Test attributes of the Brownian integrator after attaching."""
    all_ = hoomd.filter.All()
    constant = hoomd.variant.Constant(2.0)
    brownian = hoomd.md.methods.Brownian(filter = all_, kT=constant)

    sim = simulation_factory(two_particle_snapshot_factory())
    sim.operations.integrator = hoomd.md.Integrator(0.005, methods=[brownian])
    sim.operations._schedule()

    assert brownian.filter is all_
    assert brownian.kT is constant
    assert brownian.alpha is None

    type_A = hoomd.filter.Type(['A'])
    with pytest.raises(AttributeError):
        # filter cannot be set after scheduling
        brownian.filter = type_A

    assert brownian.filter is all_

    ramp = hoomd.variant.Ramp(1, 2, 1000000, 2000000)
    brownian.kT = ramp
    assert brownian.kT is ramp

    brownian.alpha = 0.125
    assert brownian.alpha == 0.125


@pytest.mark.serial
def test_berendsen_attributes(device):
    """Test attributes of the Berendsen integrator before attaching."""
    all_ = hoomd.filter.All()
    constant = hoomd.variant.Constant(2.0)
    berendsen = hoomd.md.methods.Berendsen(filter=all_, kT=constant, tau=10.0)

    assert berendsen.filter == all_
    assert berendsen.kT == constant
    assert berendsen.tau == 10.0

    type_A = hoomd.filter.Type(['A'])
    berendsen.filter = type_A
    assert berendsen.filter == type_A

    ramp = hoomd.variant.Ramp(1, 2, 1000000, 2000000)
    berendsen.kT = ramp
    assert berendsen.kT == ramp

    berendsen.tau = 1.2
    assert berendsen.tau == 1.2


@pytest.mark.serial
def test_berendsen_attributes_attached(simulation_factory,
                                       two_particle_snapshot_factory):
    """Test attributes of the Berendsen integrator after attaching."""
    all_ = hoomd.filter.All()
    constant = hoomd.variant.Constant(2.0)
    berendsen = hoomd.md.methods.Berendsen(filter=all_, kT=constant, tau=10.0)
    sim = simulation_factory(two_particle_snapshot_factory())
    sim.operations.integrator = hoomd.md.Integrator(0.005, methods=[berendsen])
    sim.operations._schedule()

    assert berendsen.filter == all_
    assert berendsen.kT == constant
    assert berendsen.tau == 10.0

    type_A = hoomd.filter.Type(['A'])
    with pytest.raises(AttributeError):
        # filter cannot be set after scheduling
        berendsen.filter = type_A

    assert berendsen.filter == all_

    ramp = hoomd.variant.Ramp(1, 2, 1000000, 2000000)
    berendsen.kT = ramp
    assert berendsen.kT == ramp

    berendsen.tau = 1.2
    assert berendsen.tau == 1.2


def test_langevin_attributes():
    """Test attributes of the Langevin integrator before attaching."""
    all_ = hoomd.filter.All()
    constant = hoomd.variant.Constant(2.0)
    langevin = hoomd.md.methods.Langevin(filter = all_, kT=constant)

    assert langevin.filter is all_
    assert langevin.kT is constant
    assert langevin.alpha is None
    assert (not langevin.tally_reservoir_energy)

    type_A = hoomd.filter.Type(['A'])
    langevin.filter = type_A
    assert langevin.filter is type_A

    ramp = hoomd.variant.Ramp(1, 2, 1000000, 2000000)
    langevin.kT = ramp
    assert langevin.kT is ramp

    langevin.alpha = 0.125
    assert langevin.alpha == 0.125

    langevin.tally_reservoir_energy = True
    assert langevin.tally_reservoir_energy


def test_langevin_attributes_attached(simulation_factory,
                                      two_particle_snapshot_factory):
    """Test attributes of the Langevin integrator before attaching."""
    all_ = hoomd.filter.All()
    constant = hoomd.variant.Constant(2.0)
    langevin = hoomd.md.methods.Langevin(filter = all_, kT=constant)

    sim = simulation_factory(two_particle_snapshot_factory())
    sim.operations.integrator = hoomd.md.Integrator(0.005, methods=[langevin])
    sim.operations._schedule()

    assert langevin.filter is all_
    assert langevin.kT is constant
    assert langevin.alpha is None
    assert (not langevin.tally_reservoir_energy)

    type_A = hoomd.filter.Type(['A'])
    with pytest.raises(AttributeError):
        # filter cannot be set after scheduling
        langevin.filter = type_A

    assert langevin.filter is all_

    ramp = hoomd.variant.Ramp(1, 2, 1000000, 2000000)
    langevin.kT = ramp
    assert langevin.kT is ramp

    langevin.alpha = 0.125
    assert langevin.alpha == 0.125

    langevin.tally_reservoir_energy = True
    assert langevin.tally_reservoir_energy


def test_npt_attributes():
    """Test attributes of the NPT integrator before attaching."""
    all_ = hoomd.filter.All()
    constant_t = hoomd.variant.Constant(2.0)
    constant_s = [hoomd.variant.Constant(1.0),
                  hoomd.variant.Constant(2.0),
                  hoomd.variant.Constant(3.0),
                  hoomd.variant.Constant(0.125),
                  hoomd.variant.Constant(.25),
                  hoomd.variant.Constant(.5)]
    npt = hoomd.md.methods.NPT(filter = all_, kT=constant_t, tau=2.0,
                               S = constant_s,
                               tauS = 2.0,
                               couple='xyz')

    assert npt.filter is all_
    assert npt.kT is constant_t
    assert npt.tau == 2.0
    assert len(npt.S) == 6
    for i in range(6):
        assert npt.S[i] is constant_s[i]
    assert npt.tauS == 2.0
    assert npt.box_dof == (True,True,True,False,False,False)
    assert npt.couple == 'xyz'
    assert not npt.rescale_all
    assert npt.gamma == 0.0

    type_A = hoomd.filter.Type(['A'])
    npt.filter = type_A
    assert npt.filter is type_A

    ramp = hoomd.variant.Ramp(1, 2, 1000000, 2000000)
    npt.kT = ramp
    assert npt.kT is ramp

    npt.tau = 10.0
    assert npt.tau == 10.0

    ramp_s = [hoomd.variant.Ramp(1.0, 4.0, 1000, 10000),
                  hoomd.variant.Ramp(2.0, 4.0, 1000, 10000),
                  hoomd.variant.Ramp(3.0, 4.0, 1000, 10000),
                  hoomd.variant.Ramp(0.125, 4.0, 1000, 10000),
                  hoomd.variant.Ramp(.25, 4.0, 1000, 10000),
                  hoomd.variant.Ramp(.5, 4.0, 1000, 10000)]
    npt.S = ramp_s
    assert len(npt.S) == 6
    for i in range(6):
        assert npt.S[i] is ramp_s[i]

    npt.tauS = 10.0
    assert npt.tauS == 10.0

    npt.box_dof = (True,False,False,False,True,False)
    assert npt.box_dof == (True,False,False,False,True,False)

    npt.couple = 'none'
    assert npt.couple == 'none'

    npt.rescale_all = True
    assert npt.rescale_all

    npt.gamma = 2.0
    assert npt.gamma == 2.0

    assert npt.translational_thermostat_dof == (0.0, 0.0)
    npt.translational_thermostat_dof = (0.125, 0.5)
    assert npt.translational_thermostat_dof == (0.125, 0.5)

    assert npt.rotational_thermostat_dof == (0.0, 0.0)
    npt.rotational_thermostat_dof = (0.5, 0.25)
    assert npt.rotational_thermostat_dof == (0.5, 0.25)

    assert npt.barostat_dof == (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    npt.barostat_dof = (1.0, 2.0, 4.0, 6.0, 8.0, 10.0)
    assert npt.barostat_dof == (1.0, 2.0, 4.0, 6.0, 8.0, 10.0)


def test_nph_attributes():
    """Test attributes of the NPH integrator before attaching."""
    all_ = hoomd.filter.All()
    constant_s = [
        hoomd.variant.Constant(1.0),
        hoomd.variant.Constant(2.0),
        hoomd.variant.Constant(3.0),
        hoomd.variant.Constant(0.125),
        hoomd.variant.Constant(.25),
        hoomd.variant.Constant(.5)
    ]
    nph = hoomd.md.methods.NPH(filter=all_,
                               S=constant_s,
                               tauS=2.0,
                               couple='xyz')

    assert nph.filter == all_
    assert len(nph.S) == 6
    for i in range(6):
        assert nph.S[i] is constant_s[i]
    assert nph.tauS == 2.0
    assert nph.box_dof == (True, True, True, False, False, False)
    assert nph.couple == 'xyz'
    assert not nph.rescale_all
    assert nph.gamma == 0.0

    type_A = hoomd.filter.Type(['A'])
    nph.filter = type_A
    assert nph.filter == type_A

    ramp_s = [
        hoomd.variant.Ramp(1.0, 4.0, 1000, 10000),
        hoomd.variant.Ramp(2.0, 4.0, 1000, 10000),
        hoomd.variant.Ramp(3.0, 4.0, 1000, 10000),
        hoomd.variant.Ramp(0.125, 4.0, 1000, 10000),
        hoomd.variant.Ramp(.25, 4.0, 1000, 10000),
        hoomd.variant.Ramp(.5, 4.0, 1000, 10000)
    ]
    nph.S = ramp_s
    assert len(nph.S) == 6
    for i in range(6):
        assert nph.S[i] is ramp_s[i]

    nph.tauS = 10.0
    assert nph.tauS == 10.0

    nph.box_dof = (True, False, False, False, True, False)
    assert nph.box_dof == (True, False, False, False, True, False)

    nph.couple = 'none'
    assert nph.couple == 'none'

    nph.rescale_all = True
    assert nph.rescale_all

    nph.gamma = 2.0
    assert nph.gamma == 2.0

    assert nph.barostat_dof == (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    nph.barostat_dof = (1.0, 2.0, 4.0, 6.0, 8.0, 10.0)
    assert nph.barostat_dof == (1.0, 2.0, 4.0, 6.0, 8.0, 10.0)


def test_npt_attributes_attached_3d(simulation_factory,
                                      two_particle_snapshot_factory):
    """Test attributes of the NPT integrator before attaching."""
    all_ = hoomd.filter.All()
    constant_t = hoomd.variant.Constant(2.0)
    constant_s = [hoomd.variant.Constant(1.0),
                  hoomd.variant.Constant(2.0),
                  hoomd.variant.Constant(3.0),
                  hoomd.variant.Constant(0.125),
                  hoomd.variant.Constant(.25),
                  hoomd.variant.Constant(.5)]
    npt = hoomd.md.methods.NPT(filter = all_, kT=constant_t, tau=2.0,
                               S = constant_s,
                               tauS = 2.0,
                               couple='xyz')

    sim = simulation_factory(two_particle_snapshot_factory())
    sim.operations.integrator = hoomd.md.Integrator(0.005, methods=[npt])
    sim.operations._schedule()

    assert npt.filter is all_
    assert npt.kT is constant_t
    assert npt.tau == 2.0
    assert len(npt.S) == 6
    for i in range(6):
        assert npt.S[i] is constant_s[i]
    assert npt.tauS == 2.0
    assert npt.couple == 'xyz'

    type_A = hoomd.filter.Type(['A'])
    with pytest.raises(AttributeError):
        # filter cannot be set after scheduling
        npt.filter = type_A

    assert npt.filter is all_

    ramp = hoomd.variant.Ramp(1, 2, 1000000, 2000000)
    npt.kT = ramp
    assert npt.kT is ramp

    npt.tau = 10.0
    assert npt.tau == 10.0

    ramp_s = [hoomd.variant.Ramp(1.0, 4.0, 1000, 10000),
                  hoomd.variant.Ramp(2.0, 4.0, 1000, 10000),
                  hoomd.variant.Ramp(3.0, 4.0, 1000, 10000),
                  hoomd.variant.Ramp(0.125, 4.0, 1000, 10000),
                  hoomd.variant.Ramp(.25, 4.0, 1000, 10000),
                  hoomd.variant.Ramp(.5, 4.0, 1000, 10000)]
    npt.S = ramp_s
    assert len(npt.S) == 6
    for i in range(6):
        assert npt.S[i] is ramp_s[i]

    npt.tauS = 10.0
    assert npt.tauS == 10.0

    npt.box_dof = (True,False,False,False,True,False)
    assert tuple(npt.box_dof) == (True,False,False,False,True,False)

    npt.couple = 'none'
    assert npt.couple == 'none'

    npt.rescale_all = True
    assert npt.rescale_all

    npt.gamma = 2.0
    assert npt.gamma == 2.0

    assert npt.translational_thermostat_dof == (0.0, 0.0)
    npt.translational_thermostat_dof = (0.125, 0.5)
    assert npt.translational_thermostat_dof == (0.125, 0.5)

    assert npt.rotational_thermostat_dof == (0.0, 0.0)
    npt.rotational_thermostat_dof = (0.5, 0.25)
    assert npt.rotational_thermostat_dof == (0.5, 0.25)

    assert npt.barostat_dof == (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    npt.barostat_dof = (1.0, 2.0, 4.0, 6.0, 8.0, 10.0)
    assert npt.barostat_dof == (1.0, 2.0, 4.0, 6.0, 8.0, 10.0)


def test_nph_attributes_attached_3d(simulation_factory,
                                    two_particle_snapshot_factory):
    """Test attributes of the NPH integrator after attaching in 3D."""
    all_ = hoomd.filter.All()
    constant_s = [
        hoomd.variant.Constant(1.0),
        hoomd.variant.Constant(2.0),
        hoomd.variant.Constant(3.0),
        hoomd.variant.Constant(0.125),
        hoomd.variant.Constant(.25),
        hoomd.variant.Constant(.5)
    ]
    nph = hoomd.md.methods.NPH(filter=all_,
                               S=constant_s,
                               tauS=2.0,
                               couple='xyz')

    sim = simulation_factory(two_particle_snapshot_factory())
    sim.operations.integrator = hoomd.md.Integrator(0.005, methods=[nph])
    sim.run(0)

    assert nph.filter == all_
    assert len(nph.S) == 6
    for i in range(6):
        assert nph.S[i] is constant_s[i]
    assert nph.tauS == 2.0
    assert nph.couple == 'xyz'

    type_A = hoomd.filter.Type(['A'])
    with pytest.raises(AttributeError):
        # filter cannot be set after scheduling
        nph.filter = type_A

    assert nph.filter == all_

    nph.tauS = 10.0
    assert nph.tauS == 10.0

    nph.box_dof = (True, False, False, False, True, False)
    assert tuple(nph.box_dof) == (True, False, False, False, True, False)

    nph.couple = 'none'
    assert nph.couple == 'none'

    nph.rescale_all = True
    assert nph.rescale_all

    nph.gamma = 2.0
    assert nph.gamma == 2.0

    assert nph.barostat_dof == (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    nph.barostat_dof = (1.0, 2.0, 4.0, 6.0, 8.0, 10.0)
    assert nph.barostat_dof == (1.0, 2.0, 4.0, 6.0, 8.0, 10.0)

    ramp_s = [
        hoomd.variant.Ramp(1.0, 4.0, 1000, 10000),
        hoomd.variant.Ramp(2.0, 4.0, 1000, 10000),
        hoomd.variant.Ramp(3.0, 4.0, 1000, 10000),
        hoomd.variant.Ramp(0.125, 4.0, 1000, 10000),
        hoomd.variant.Ramp(.25, 4.0, 1000, 10000),
        hoomd.variant.Ramp(.5, 4.0, 1000, 10000)
    ]
    nph.S = ramp_s
    assert len(nph.S) == 6
    for _ in range(5):
        sim.run(1)
        for i in range(6):
            assert nph.S[i] is ramp_s[i]


def test_npt_thermalize_thermostat_and_barostat_dof(
    simulation_factory, two_particle_snapshot_factory):
    """Tests that NPT.thermalize_thermostat_and_barostat_dof can be called."""
    all_ = hoomd.filter.All()
    constant_t = hoomd.variant.Constant(2.0)
    constant_s = [1, 2, 3, 0.125, 0.25, 0.5]
    npt = hoomd.md.methods.NPT(filter=all_,
                               kT=constant_t,
                               tau=2.0,
                               S=constant_s,
                               tauS=2.0,
                               box_dof=[True, True, True, True, True, True],
                               couple='xyz')

    sim = simulation_factory(two_particle_snapshot_factory())
    sim.operations.integrator = hoomd.md.Integrator(0.005, methods=[npt])
    sim.operations._schedule()

    npt.thermalize_thermostat_and_barostat_dof()
    xi, eta = npt.translational_thermostat_dof
    assert xi != 0.0
    assert eta == 0.0

    xi_rot, eta_rot = npt.rotational_thermostat_dof
    assert xi_rot == 0.0
    assert eta_rot == 0.0

    for v in npt.barostat_dof:
        assert v != 0.0


def test_npt_thermalize_thermostat_and_barostat_aniso_dof(
    simulation_factory, two_particle_snapshot_factory):
    """Tests that NPT.thermalize_thermostat_and_barostat_dof can be called."""
    all_ = hoomd.filter.All()
    constant_t = hoomd.variant.Constant(2.0)
    constant_s = [1, 2, 3, 0.125, 0.25, 0.5]
    npt = hoomd.md.methods.NPT(filter=all_,
                               kT=constant_t,
                               tau=2.0,
                               S=constant_s,
                               tauS=2.0,
                               box_dof=[True, True, True, True, True, True],
                               couple='xyz')

    snap = two_particle_snapshot_factory()
    if snap.exists:
        snap.particles.moment_inertia[:] = [[1, 1, 1], [2, 0, 0]]

    sim = simulation_factory(snap)

    sim.operations.integrator = hoomd.md.Integrator(0.005,
                                                    methods=[npt],
                                                    aniso=True)
    sim.run(0)

    npt.thermalize_thermostat_and_barostat_dof()
    xi, eta = npt.translational_thermostat_dof
    assert xi != 0.0
    assert eta == 0.0

    xi_rot, eta_rot = npt.rotational_thermostat_dof
    assert xi_rot != 0.0
    assert eta_rot == 0.0
    for v in npt.barostat_dof:
        assert v != 0.0


def test_nph_thermalize_barostat_dof(simulation_factory,
                                     two_particle_snapshot_factory):
    """Tests that NPT.thermalize_thermostat_and_barostat_dof can be called."""
    all_ = hoomd.filter.All()
    constant_s = [1, 2, 3, 0.125, 0.25, 0.5]
    nph = hoomd.md.methods.NPH(filter=all_,
                               S=constant_s,
                               tauS=2.0,
                               box_dof=[True, True, True, True, True, True],
                               couple='xyz')

    sim = simulation_factory(two_particle_snapshot_factory())
    sim.operations.integrator = hoomd.md.Integrator(0.005, methods=[nph])
    sim.run(0)

    nph.thermalize_barostat_dof()
    for v in nph.barostat_dof:
        assert v != 0.0


def test_npt_attributes_attached_2d(simulation_factory,
                                      two_particle_snapshot_factory):
    """Test attributes of the NPT integrator specific to 2D simulations."""
    all_ = hoomd.filter.All()
    npt = hoomd.md.methods.NPT(filter = all_, kT=1.0, tau=2.0,
                               S = 2.0,
                               tauS = 2.0,
                               couple='xy')


    assert npt.box_dof == (True,True,True,False,False,False)
    assert npt.couple == 'xy'

    sim = simulation_factory(two_particle_snapshot_factory(dimensions=2))
    sim.operations.integrator = hoomd.md.Integrator(0.005, methods=[npt])
    sim.operations._schedule()

    # after attaching in 2d, only some coupling modes and box dof are valid
    assert tuple(npt.box_dof) == (True,True,False,False,False,False)
    assert npt.couple == 'xy'

    with pytest.raises(ValueError):
        npt.couple = 'xyz'
    with pytest.raises(ValueError):
        npt.couple = 'xz'
    with pytest.raises(ValueError):
        npt.couple = 'yz'

    npt.couple = 'none'
    assert npt.couple == 'none'

    npt.box_dof = (True, True, True, True, True, True)
    assert tuple(npt.box_dof) == (True, True, False, True, False, False)


def test_nph_attributes_attached_2d(simulation_factory,
                                    two_particle_snapshot_factory):
    """Test attributes of the NPH integrator specific to 2D simulations."""
    all_ = hoomd.filter.All()
    nph = hoomd.md.methods.NPH(filter=all_, S=2.0, tauS=2.0, couple='xy')

    assert nph.box_dof == (True, True, True, False, False, False)
    assert nph.couple == 'xy'

    sim = simulation_factory(two_particle_snapshot_factory(dimensions=2))
    sim.operations.integrator = hoomd.md.Integrator(0.005, methods=[nph])
    sim.run(0)

    # after attaching in 2d, only some coupling modes and box dof are valid
    assert tuple(nph.box_dof) == (True, True, False, False, False, False)
    assert nph.couple == 'xy'

    with pytest.raises(ValueError):
        nph.couple = 'xyz'
    with pytest.raises(ValueError):
        nph.couple = 'xz'
    with pytest.raises(ValueError):
        nph.couple = 'yz'

    nph.couple = 'none'
    assert nph.couple == 'none'

    nph.box_dof = (True, True, True, True, True, True)
    assert tuple(nph.box_dof) == (True, True, False, True, False, False)


def test_nve_attributes():
    """Test attributes of the NVE integrator before attaching."""
    all_ = hoomd.filter.All()
    constant = hoomd.variant.Constant(2.0)
    nve = hoomd.md.methods.NVE(filter = all_)

    assert nve.filter is all_

    type_A = hoomd.filter.Type(['A'])
    nve.filter = type_A
    assert nve.filter is type_A


def test_nve_attributes_attached(simulation_factory,
                                 two_particle_snapshot_factory):
    """Test attributes of the NVE integrator before attaching."""
    all_ = hoomd.filter.All()
    nve = hoomd.md.methods.NVE(filter = all_)

    sim = simulation_factory(two_particle_snapshot_factory())
    sim.operations.integrator = hoomd.md.Integrator(0.005, methods=[nve])
    sim.operations._schedule()

    assert nve.filter is all_

    type_A = hoomd.filter.Type(['A'])
    with pytest.raises(AttributeError):
        # filter cannot be set after scheduling
        nve.filter = type_A

    assert nve.filter is all_


def test_nvt_attributes():
    """Test attributes of the NVT integrator before attaching."""
    all_ = hoomd.filter.All()
    constant = hoomd.variant.Constant(2.0)
    nvt = hoomd.md.methods.NVT(filter = all_, kT=constant, tau=2.0)

    assert nvt.filter is all_
    assert nvt.kT is constant
    assert nvt.tau == 2.0

    type_A = hoomd.filter.Type(['A'])
    nvt.filter = type_A
    assert nvt.filter is type_A

    ramp = hoomd.variant.Ramp(1, 2, 1000000, 2000000)
    nvt.kT = ramp
    assert nvt.kT is ramp

    nvt.tau = 10.0
    assert nvt.tau == 10.0

    assert nvt.translational_thermostat_dof == (0.0, 0.0)
    nvt.translational_thermostat_dof = (0.125, 0.5)
    assert nvt.translational_thermostat_dof == (0.125, 0.5)

    assert nvt.rotational_thermostat_dof == (0.0, 0.0)
    nvt.rotational_thermostat_dof = (0.5, 0.25)
    assert nvt.rotational_thermostat_dof == (0.5, 0.25)


def test_nvt_attributes_attached(simulation_factory,
                                      two_particle_snapshot_factory):
    """Test attributes of the NVT integrator before attaching."""
    all_ = hoomd.filter.All()
    constant = hoomd.variant.Constant(2.0)
    nvt = hoomd.md.methods.NVT(filter = all_, kT=constant, tau=2.0)

    sim = simulation_factory(two_particle_snapshot_factory())
    sim.operations.integrator = hoomd.md.Integrator(0.005, methods=[nvt])
    sim.operations._schedule()

    assert nvt.filter is all_
    assert nvt.kT is constant
    assert nvt.tau == 2.0

    type_A = hoomd.filter.Type(['A'])
    with pytest.raises(AttributeError):
        # filter cannot be set after scheduling
        nvt.filter = type_A

    assert nvt.filter is all_

    ramp = hoomd.variant.Ramp(1, 2, 1000000, 2000000)
    nvt.kT = ramp
    assert nvt.kT is ramp

    nvt.tau = 10.0
    assert nvt.tau == 10.0

    assert nvt.translational_thermostat_dof == (0.0, 0.0)
    nvt.translational_thermostat_dof = (0.125, 0.5)
    assert nvt.translational_thermostat_dof == (0.125, 0.5)

    assert nvt.rotational_thermostat_dof == (0.0, 0.0)
    nvt.rotational_thermostat_dof = (0.5, 0.25)
    assert nvt.rotational_thermostat_dof == (0.5, 0.25)


def test_nvt_thermalize_thermostat_dof(simulation_factory,
                                       two_particle_snapshot_factory):
    """Tests that NVT.thermalize_thermostat_dof can be called."""
    all_ = hoomd.filter.All()
    constant = hoomd.variant.Constant(2.0)
    nvt = hoomd.md.methods.NVT(filter=all_, kT=constant, tau=2.0)

    sim = simulation_factory(two_particle_snapshot_factory())
    sim.operations.integrator = hoomd.md.Integrator(0.005, methods=[nvt])
    sim.operations._schedule()

    nvt.thermalize_thermostat_dof()
    xi, eta = nvt.translational_thermostat_dof
    assert xi != 0.0
    assert eta == 0.0

    xi_rot, eta_rot = nvt.rotational_thermostat_dof
    assert xi_rot == 0.0
    assert eta_rot == 0.0


def test_nvt_thermalize_thermostat_aniso_dof(simulation_factory,
                                             two_particle_snapshot_factory):
    """Tests that NVT.thermalize_thermostat_dof can be called."""
    all_ = hoomd.filter.All()
    constant = hoomd.variant.Constant(2.0)
    nvt = hoomd.md.methods.NVT(filter=all_, kT=constant, tau=2.0)

    snap = two_particle_snapshot_factory()
    if snap.exists:
        snap.particles.moment_inertia[:] = [[1, 1, 1], [2, 0, 0]]

    sim = simulation_factory(snap)
    sim.operations.integrator = hoomd.md.Integrator(0.005,
                                                    methods=[nvt],
                                                    aniso=True)
    sim.run(0)

    nvt.thermalize_thermostat_dof()
    xi, eta = nvt.translational_thermostat_dof
    assert xi != 0.0
    assert eta == 0.0

    xi_rot, eta_rot = nvt.rotational_thermostat_dof
    assert xi_rot != 0.0
    assert eta_rot == 0.0
