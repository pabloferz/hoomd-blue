// Copyright (c) 2009-2021 The Regents of the University of Michigan
// This file is part of the HOOMD-blue project, released under the BSD 3-Clause License.

#ifdef __HIPCC__
#error This header cannot be compiled by nvcc
#endif

#pragma once

#include "Updater.h"
#include "ForceCompute.h"
#include "ForceConstraint.h"
#include "md/ForceComposite.h"
#include "HalfStepHook.h"
#include "ParticleGroup.h"
#include <string>
#include <vector>
#include <pybind11/pybind11.h>

#ifdef ENABLE_HIP
#include <hip/hip_runtime.h>
#endif

/// Base class that defines an integrator
/** An Integrator steps the entire simulation forward one time step in time.
    Prior to calling update(timestep), the system is at time step \a timestep.
    After the call to update completes, the system is at \a timestep + 1.

    All integrators have the common property that they add up many forces to
    get the net force on each particle. This task is performed by the
    base class Integrator. Similarly, all integrators share the
    property that they have a time step, \a deltaT.

    Any number of ForceComputes can be used to specify the net force
    for use with this integrator. They are added via calling
    addForceCompute(). Any number of forces can be added in this way.

    All forces added via addForceCompute() are computed independently and then totaled up to calculate the net force
    and energy on each particle. Constraint forces (ForceConstraint) are unique in that they need to be computed
    \b after the net forces is already available. To implement this behavior, call addForceConstraint() to add any
    number of constraint forces. All constraint forces will be computed independently and will be able to read the
    current unconstrained net force. Separate constraint forces should not overlap. Degrees of freedom removed
    via the constraint forces can be totaled up with a call to getNDOFRemoved for convenience in derived classes
    implementing correct counting in getTranslationalDOF() and getRotationalDOF().

    Integrators take "ownership" of the particle's accelerations. Any other updater
    that modifies the particles accelerations will produce undefined results. If
    accelerations are to be modified, they must be done through forces, and added to
    an Integrator via addForceCompute().

    No such ownership is taken of the particle positions and velocities. Other Updaters
    can modify particle positions and velocities as they wish. Those updates will be taken
    into account by the Integrator. It would probably make the most sense to have such updaters
    run BEFORE the Integrator, since an Integrator actually moves the particles to the next time
    step. This is handled correctly by System.

    \ingroup updaters
*/
class PYBIND11_EXPORT Integrator : public Updater
    {
    public:
        /// Constructor
        Integrator(std::shared_ptr<SystemDefinition> sysdef, Scalar deltaT);

        /// Destructor
        virtual ~Integrator();

        /// Take one timestep forward
        virtual void update(uint64_t timestep);

        /// Add a ForceCompute to the list
        virtual void addForceCompute(std::shared_ptr<ForceCompute> fc);

        /// Get the list of force computes
        std::vector< std::shared_ptr<ForceCompute> >& getForces()
            {
            return m_forces;
            }

        /// Add a ForceConstraint to the list
        virtual void addForceConstraint(std::shared_ptr<ForceConstraint> fc);

        /// Get the list of force computes
        std::vector< std::shared_ptr<ForceConstraint> >& getConstraintForces()
            {
            return m_constraint_forces;
            }

        /// Set HalfStepHook
        virtual void setHalfStepHook(std::shared_ptr<HalfStepHook> hook);

        /// Removes all ForceComputes from the list
        virtual void removeForceComputes();

        /// Removes HalfStepHook
        virtual void removeHalfStepHook();

        /// Change the timestep
        virtual void setDeltaT(Scalar deltaT);

        /// Return the timestep
        Scalar getDeltaT();

        /// Update the number of degrees of freedom for a group
        /** @param group Group to set the degrees of freedom for.
        */
        void updateGroupDOF(std::shared_ptr<ParticleGroup> group)
            {
            group->setTranslationalDOF(getTranslationalDOF(group));
            group->setRotationalDOF(getRotationalDOF(group));
            }

        /// Get the number of degrees of freedom granted to a given group
        /** @param group Group over which to count degrees of freedom.
            Base class Integrator returns 0. Derived classes should override.
        */
        virtual Scalar getTranslationalDOF(std::shared_ptr<ParticleGroup> group)
            {
            return 0;
            }

        /** Get the number of rotational degrees of freedom granted to a given group

            @param group Group over which to count degrees of freedom.
            Base class Integrator returns 0. Derived classes should override.
        */
        virtual Scalar getRotationalDOF(std::shared_ptr<ParticleGroup> group)
            {
            return 0;
            }

        /// Count the total number of degrees of freedom removed by all constraint forces
        Scalar getNDOFRemoved(std::shared_ptr<ParticleGroup> query);

        /// Returns a list of log quantities this compute calculates
        virtual std::vector< std::string > getProvidedLogQuantities();

        /// Calculates the requested log value and returns it
        virtual Scalar getLogValue(const std::string& quantity, uint64_t timestep);

        /// helper function to compute total momentum
        virtual Scalar computeTotalMomentum(uint64_t timestep);

        /// Prepare for the run
        virtual void prepRun(uint64_t timestep);

        #ifdef ENABLE_MPI
        /// Set the communicator to use
        /** @param comm The Communicator
         */
        virtual void setCommunicator(std::shared_ptr<Communicator> comm);

        /// Callback for pre-computing the forces
        void computeCallback(uint64_t timestep);
        #endif

    protected:
        /// The step size
        Scalar m_deltaT;

        /// List of all the force computes
        std::vector< std::shared_ptr<ForceCompute> > m_forces;

        /// List of all the constraints
        std::vector< std::shared_ptr<ForceConstraint> > m_constraint_forces;

        /// The HalfStepHook, if active
        std::shared_ptr<HalfStepHook> m_half_step_hook;

        /// helper function to compute initial accelerations
        void computeAccelerations(uint64_t timestep);

        /// helper function to compute net force/virial
        void computeNetForce(uint64_t timestep);

#ifdef ENABLE_HIP
        /// helper function to compute net force/virial on the GPU
        void computeNetForceGPU(uint64_t timestep);
#endif

#ifdef ENABLE_MPI
        /// helper function to determine the ghost communication flags
        CommFlags determineFlags(uint64_t timestep);
#endif

        /// Check if any forces introduce anisotropic degrees of freedom
        bool getAnisotropic();

    private:
        #ifdef ENABLE_MPI
        /// Connection to Communicator to request communication flags
        bool m_request_flags_connected = false;

        /// Track if we have already connected signals
        bool m_signals_connected = false;
        #endif
    };

/// Exports the NVEUpdater class to python
void export_Integrator(pybind11::module& m);
