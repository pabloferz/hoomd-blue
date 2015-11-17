/*
Highly Optimized Object-oriented Many-particle Dynamics -- Blue Edition
(HOOMD-blue) Open Source Software License Copyright 2009-2015 The Regents of
the University of Michigan All rights reserved.

HOOMD-blue may contain modifications ("Contributions") provided, and to which
copyright is held, by various Contributors who have granted The Regents of the
University of Michigan the right to modify and/or distribute such Contributions.

You may redistribute, use, and create derivate works of HOOMD-blue, in source
and binary forms, provided you abide by the following conditions:

* Redistributions of source code must retain the above copyright notice, this
list of conditions, and the following disclaimer both in the code and
prominently in any materials provided with the distribution.

* Redistributions in binary form must reproduce the above copyright notice, this
list of conditions, and the following disclaimer in the documentation and/or
other materials provided with the distribution.

* All publications and presentations based on HOOMD-blue, including any reports
or published results obtained, in whole or in part, with HOOMD-blue, will
acknowledge its use according to the terms posted at the time of submission on:
http://codeblue.umich.edu/hoomd-blue/citations.html

* Any electronic documents citing HOOMD-Blue will link to the HOOMD-Blue website:
http://codeblue.umich.edu/hoomd-blue/

* Apart from the above required attributions, neither the name of the copyright
holder nor the names of HOOMD-blue's contributors may be used to endorse or
promote products derived from this software without specific prior written
permission.

Disclaimer

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER AND CONTRIBUTORS ``AS IS'' AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND/OR ANY
WARRANTIES THAT THIS SOFTWARE IS FREE OF INFRINGEMENT ARE DISCLAIMED.

IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

// Maintainer: mphoward

#ifndef __NEIGHBORLOSTGPUMULTIBINNED_CUH__
#define __NEIGHBORLOSTGPUMULTIBINNED_CUH__

#include <cuda_runtime.h>

#include "HOOMDMath.h"
#include "Index1D.h"
#include "ParticleData.cuh"

/*! \file NeighborListGPUMultiBinned.cuh
    \brief Declares GPU kernel code for neighbor list generation on the GPU
*/

#define WARP_SIZE 32
const unsigned int min_threads_per_particle=1;
const unsigned int max_threads_per_particle=WARP_SIZE;

//! Kernel driver for gpu_compute_nlist_multi_binned_kernel()
cudaError_t gpu_compute_nlist_multi_binned(unsigned int *d_nlist,
                                           unsigned int *d_n_neigh,
                                           Scalar4 *d_last_updated_pos,
                                           unsigned int *d_conditions,
                                           const unsigned int *d_Nmax,
                                           const unsigned int *d_head_list,
                                           const unsigned int *d_pid_map,
                                           const Scalar4 *d_pos,
                                           const unsigned int *d_body,
                                           const Scalar *d_diameter,
                                           const unsigned int N,
                                           const unsigned int *d_cell_size,
                                           const Scalar4 *d_cell_xyzf,
                                           const Scalar4 *d_cell_tdb,
                                           const Index3D& ci,
                                           const Index2D& cli,
                                           const Scalar4 *d_stencil,
                                           const unsigned int *d_n_stencil,
                                           const Index2D& stencil_idx,
                                           const BoxDim& box,
                                           const Scalar *d_r_cut,
                                           const Scalar r_buff,
                                           const unsigned int ntypes,
                                           const Scalar3& ghost_width,
                                           bool filter_body,
                                           bool diameter_shift,
                                           const unsigned int threads_per_particle,
                                           const unsigned int block_size,
                                           const unsigned int compute_capability);

//! Kernel driver for filling the particle types for sorting
cudaError_t gpu_compute_nlist_multi_fill_types(unsigned int *d_pids,
                                               unsigned int *d_types,
                                               const Scalar4 *d_pos,
                                               const unsigned int N);

//! Wrapper to CUB sorting
void gpu_compute_nlist_multi_sort_types(unsigned int *d_pids,
                                        unsigned int *d_pids_alt,
                                        unsigned int *d_types,
                                        unsigned int *d_types_alt,
                                        void *d_tmp_storage,
                                        size_t &tmp_storage_bytes,
                                        bool &swap,
                                        const unsigned int N);
#endif // __NEIGHBORLOSTGPUMULTIBINNED_CUH__
