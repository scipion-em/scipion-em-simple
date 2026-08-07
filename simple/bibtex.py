# -*- coding: utf-8 -*-
# **************************************************************************
# *
# * Authors:     Carlos Oscar Sorzano (coss@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'coss@cnb.csic.es'
# *
# **************************************************************************
"""

@article{Elmlund2010,
  Title                    = {Ab initio structure determination from electron microscopic images of single molecules coexisting in different functional states.},
  Author                   = {Elmlund, D. and Davis, R. and Elmlund, H.},
  Journal                  = {Structure},
  Year                     = {2010},
  Month                    = {Jul},
  Number                   = {7},
  Pages                    = {777--786},
  Volume                   = {18},
  Doi                      = {http://dx.doi.org/10.1016/j.str.2010.06.001},
  Keywords                 = {Algorithms; Cryoelectron Microscopy, methods; Escherichia coli; Fourier Analysis; Image Processing, Computer-Assisted, methods; Models, Molecular; Nanoparticles, chemistry; RNA Polymerase II, chemistry; Ribosomes, ultrastructure; Yeasts},
  Pii                      = {S0969-2126(10)00192-9},
  Pmid                     = {20637414},
  Url                      = {http://dx.doi.org/10.1016/j.str.2010.06.001}
}

@article{Elmlund2012,
  Title                    = {SIMPLE: Software for ab initio reconstruction of heterogeneous single-particles.},
  Author                   = {Elmlund, D. and Elmlund, H.},
  Journal                  = {J Struct Biol},
  Year                     = {2012},
  Month                    = {Dec},
  Number                   = {3},
  Pages                    = {420--427},
  Volume                   = {180},
  Doi                      = {http://dx.doi.org/10.1016/j.jsb.2012.07.010},
  Keywords                 = {Algorithms; Computer Simulation; Cryoelectron Microscopy; Fourier Analysis; Image Processing, Computer-Assisted; Imaging, Three-Dimensional; Models, Molecular; Software},
  Pii                      = {S1047-8477(12)00218-3},
  Pmid                     = {22902564},
  Url                      = {http://dx.doi.org/10.1016/j.jsb.2012.07.010}
}

@article{Elmlund2013,
  Title                    = {PRIME: probabilistic initial {3D} model generation for single-particle cryo-electron microscopy.},
  Author                   = {Elmlund, Hans and Elmlund, Dominika and Bengio, Samy},
  Journal                  = {Structure},
  Year                     = {2013},

  Month                    = {Aug},
  Number                   = {8},
  Pages                    = {1299--1306},
  Volume                   = {21},

  Abstract                 = {Low-dose electron microscopy of cryo-preserved individual biomolecules (single-particle cryo-EM) is a powerful tool for obtaining information about the structure and dynamics of large macromolecular assemblies. Acquiring images with low dose reduces radiation damage, preserves atomic structural details, but results in low signal-to-noise ratio of the individual images. The projection directions of the two-dimensional images are random and unknown. The grand challenge is to achieve the precise three-dimensional (3D) alignment of many (tens of thousands to millions) noisy projection images, which may then be combined to obtain a faithful 3D map. An accurate initial 3D model is critical for obtaining the precise 3D alignment required for high-resolution (<10 Å) map reconstruction. We report a method (PRIME) that, in a single step and without prior structural knowledge, can generate an accurate initial 3D map directly from the noisy images.},
  Doi                      = {http://dx.doi.org/10.1016/j.str.2013.07.002},
  Institution              = {Department of Structural Biology, Stanford University Medical School, Fairchild Building, 1st Floor, 299 Campus Drive, Stanford, CA 94305-5126, USA. hael@stanford.edu},
  Keywords                 = {Cryoelectron Microscopy, methods; Imaging, Three-Dimensional, methods; Macromolecular Substances, ultrastructure; Models, Molecular; Models, Statistical; Ribosomes, ultrastructure; Software},
  Pii                      = {S0969-2126(13)00250-5},
  Pmid                     = {23931142},
  Timestamp                = {2014.06.26},
  Url                      = {http://dx.doi.org/10.1016/j.str.2013.07.002}
}

@article{Van_2025_abinitio3d,
author = "Van, Cong T. S. and Reboul, Cyril F. and Caesar, Joseph J. E. and Meana-Pa{\~{n}}eda, Rub{\'{e}}n and Lountos, George T. and Deme, Justin C. and Bryant, Owain J. and Johnson, Steven and Piczak, Claire T. and Valkov, Eugene and Lea, Susan M. and Elmlund, Hans",
title = "{Probabilistic single-particle cryo-EM {\it ab initio} 3D reconstruction in {\it SIMPLE}}",
journal = "Acta Crystallographica Section D",
year = "2025",
volume = "81",
number = "8",
pages = "396--409",
month = "Aug",
doi = {10.1107/S2059798325005686},
url = {https://doi.org/10.1107/S2059798325005686},
abstract = {Three-dimensional (3D) structure determination by single-particle analysis of cryo-electron microscopy (cryo-EM) images requires {\it ab initio} 3D reconstruction of density volume(s) from 2D images (particles). This large-scale inverse problem requires the determination of many million degrees of freedom from extremely noisy experimental measurements. Here, we introduce a new approach to probabilistic multi-volume {\it ab initio} 3D reconstruction for simultaneous estimation of the relative particle 3D orientations and partitioning of the particles into groups with distinct structural states. To account for further structural variability within the discrete state groups, due to for example regional disorder, flexibility or partial occupancy of associating ligands, we introduce a new method for adaptive non-uniform regularization based on iterated conditional modes (ICMs). Our ICM regularization approach can be viewed as a spatially varying real-space prior that optimizes the connectivity of the reconstructed density map(s). Our method is designed to run in real time as the microscope collects the data, which puts significant constraints on algorithm scalability and flexibility with regard to how new particles are incorporated. We describe the probabilistic optimization and non-uniform regularization theory in detail. Finally, we provide numerous benchmarking examples, both on publicly available standard test data sets and on data sets acquired at our cryo-EM facility at the National Cancer Institute, National Institutes of Health. The implementation of our new multi-volume {\it ab initio} 3D reconstruction approach is part of the {\it SIMPLE} software suite, which is provided open source at https://github.com/hael/SIMPLE.},
keywords = {cryo-EM, single particle, reconstruction, probabilistic, heterogeneity},
}

@article{Van_2026_polar,
author = "Van, Cong T. S. and Reboul, Cyril F. and Caesar, Joseph J. E. and Meana-Pa{\~{n}}eda, Rub{\'{e}}n and Elmlund, Hans",
title = "{A polar Fourier geometric approach to volume-free single-particle 3D reconstruction}",
journal = "IUCrJ",
year = "2026",
volume = "13",
number = "4",
pages = "354--363",
month = "Jul",
doi = {10.1107/S2052252526003611},
url = {https://doi.org/10.1107/S2052252526003611},
abstract = {We introduce a compact mathematical formulation for the inverse single-particle 3D reconstruction problem, a high-dimensional inverse problem in which millions of parameters are estimated from extremely noisy experimental measurements. Given a collection of noisy 2D projection images (particles) of an unknown 3D charge-density distribution, the objective is to infer the unknown particle orientations and thereby enable {\it ab initio} 3D reconstruction via tomographic methods. We develop a method for generating regularized reprojections directly from the noisy particles that does not rely on explicit 3D density reconstruction. Instead, we recast the {\it ab initio} orientation-recovery problem in polar Fourier coordinates through discretization of the rotation group SO(3). The directions of projection are mapped onto slices intersecting the origin of the 3D Fourier transform. The rotations in the plane normal to a projection direction are mapped onto radial lines in the 2D Fourier transforms of the particles. An optimization procedure jointly estimates particle projection directions, in-plane rotation angles and rotational origin offsets. Regularized reprojections are computed by averaging along lines in the polar Fourier representation, exploiting data redundancy to suppress noise and improve stability. We present the mathematical framework in detail and provide initial benchmarks demonstrating the performance and robustness of the approach.},
keywords = {single-particle 3D reconstruction, polar Fourier coordinates, orientation-recovery problem},
}

"""
