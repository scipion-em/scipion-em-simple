# **************************************************************************
# *
# * Authors:     Carlos Oscar S. Sorzano (coss@cnb.csic.es)
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
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

import os
from glob import glob

import pyworkflow.em as em
import pyworkflow.protocol.params as params
from pyworkflow.utils.path import cleanPath, cleanPattern

import simple
from simple.constants import *



class ProtPrime(em.ProtInitialVolume):
    """
    Produces one or several initial 3D volumes from two-dimensional class averages
    or particle averages using PRIME-based ab initio reconstruction approaches.

    AI Generated:

    PRIME Initial Volume Reconstruction (ProtPrime) - User Manual
        Overview

        The PRIME Initial Volume Reconstruction protocol generates one or more
        starting three-dimensional maps directly from a set of two-dimensional
        class averages or particle averages. Its primary objective is to provide
        biologically meaningful initial models that can serve as starting points
        for subsequent refinement and high-resolution reconstruction workflows.

        In cryo-EM studies, obtaining a reliable initial volume is often one of
        the most important steps in the reconstruction process. A suitable starting
        model helps guide refinement toward the correct structural solution while
        reducing the risk of convergence to incorrect maps. This protocol is
        particularly useful when no prior structural model is available or when an
        independent reconstruction is desired to minimize model bias.

        Inputs and General Workflow

        The protocol requires a collection of two-dimensional class averages or
        particle averages representing different views of the biological specimen.
        These inputs should ideally contain clear structural features and provide
        broad angular coverage of the particle. Better class averages generally
        lead to more reliable initial reconstructions.

        During processing, the protocol analyzes the supplied images and estimates
        one or more plausible three-dimensional structures that explain the observed
        projections. The resulting maps can then be evaluated visually and used as
        starting points for downstream refinement procedures.

        Symmetry Considerations

        An important aspect of initial model generation is the specification of
        particle symmetry. When the biological assembly possesses known rotational
        or dihedral symmetry, providing the appropriate symmetry group can
        significantly improve reconstruction quality and stability.

        For highly symmetric particles such as viral capsids, applying the correct
        symmetry can greatly enhance signal recovery and facilitate convergence.
        However, incorrect symmetry assignment may introduce structural artifacts
        and distort biologically relevant features. When uncertainty exists, it is
        often safer to begin with the lowest symmetry consistent with current
        biological knowledge.

        Multiple Initial Models

        The protocol can generate more than one candidate volume during a single
        execution. This capability is especially valuable when the dataset may
        contain structural heterogeneity or when several alternative solutions are
        plausible.

        Producing multiple candidate maps allows users to compare independent
        reconstructions and identify the most biologically meaningful result.
        Different initial volumes may represent alternative conformations,
        different reconstruction hypotheses, or varying levels of structural
        detail. Careful inspection and validation remain essential before
        proceeding to refinement.

        Resolution and Filtering

        Initial models are intended to capture the overall architecture of the
        particle rather than high-resolution atomic detail. The protocol provides
        mechanisms to control the effective resolution of the reconstructed maps,
        either through user-defined limits or through automatic estimation.

        Conservative filtering is often beneficial during early stages of analysis
        because it reduces the influence of noise and emphasizes robust structural
        features. Users should interpret fine details cautiously, as initial
        reconstructions are primarily intended to establish global shape and
        orientation information.

        Particle Inclusion and Data Quality

        The protocol can operate using all available particle information or a
        selected fraction of the dataset. Restricting reconstruction to a subset
        of particles may sometimes improve robustness when large datasets contain
        significant variability or outliers.

        From a biological perspective, the quality of the resulting volume depends
        strongly on the quality of the input classes. Well-defined classes that
        represent consistent particle views generally produce more reliable initial
        models than noisy or poorly aligned averages.

        Molecular Weight Constraints

        When approximate molecular weight information is available, it can be used
        as an additional source of biological knowledge during reconstruction. Such
        constraints may help guide the generation of physically realistic maps and
        improve the consistency of the resulting structures.

        Nevertheless, inaccurate molecular weight estimates can bias the outcome.
        Users should apply such constraints only when supported by independent
        biochemical or structural evidence.

        Outputs and Their Interpretation

        Upon completion, the protocol produces either a single reconstructed volume
        or a collection of candidate volumes. These maps represent low- to
        intermediate-resolution structural hypotheses derived from the supplied
        two-dimensional information.

        The generated volumes should be examined carefully for overall shape,
        symmetry consistency, and biological plausibility. Independent validation,
        comparison with known structural information, and subsequent refinement are
        recommended before drawing biological conclusions.

        Practical Recommendations

        For most applications, it is advisable to begin with high-quality class
        averages that span a wide range of particle orientations. When prior
        symmetry information is known with confidence, incorporating it can improve
        reconstruction quality. If uncertainty exists regarding the correct
        structural solution, generating multiple candidate volumes is often a
        valuable strategy.

        Initial models should be regarded as starting points rather than final
        structures. Their primary purpose is to provide a reliable foundation for
        subsequent refinement and validation steps within the cryo-EM workflow.

        Final Perspective

        Initial volume generation is a critical bridge between two-dimensional
        image analysis and three-dimensional structural interpretation. The quality
        and biological realism of the resulting models can strongly influence all
        downstream processing. Careful selection of input classes, thoughtful use
        of symmetry information, and rigorous evaluation of candidate volumes are
        essential for obtaining trustworthy structural reconstructions.
    """
    _label = 'prime'

    # --------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        form.addSection('Input')
        form.addParam('inputClasses', params.PointerParam,
                      label="Input classes", important=True,
                      pointerClass='SetOfClasses2D, SetOfAverages',
                      help='Select either a SetOfClasses2D or a '
                           'SetOfAverages from the project. ')
        form.addParam('symmetryGroup', params.TextParam,
                      default='c1',
                      label="Symmetry group",
                      help='cn or dn. For icosahedral viruses, use c5. \n'
                           'If no symmetry is present, give c1.')  
        form.addParam('Nvolumes', params.IntParam,
                      default=1,
                      label='Number of volumes', 
                      help="Number of volumes to reconstruct")
        form.addParam('maximumShift', params.IntParam,
                      default=0,
                      expertLevel=params.LEVEL_ADVANCED,
                      label='Maximum shift (px)',
                      help="Set to 0 for free shift search")
        form.addParam('shiftStep', params.IntParam,
                      default=1,
                      expertLevel=params.LEVEL_ADVANCED,
                      label='Shift step (px)',
                      help="Step for exhaustive shift search")
        form.addParam('outerMask', params.FloatParam,
                      default=-1,
                      expertLevel=params.LEVEL_ADVANCED,
                      label='Outer mask radius (px)',
                      help="Set to -1 for half the image size")
        form.addParam('dynamicFilter', params.BooleanParam,
                      default=False,
                      expertLevel=params.LEVEL_ADVANCED,
                      label='Dynamic filtering?',
                      help="Let the program estimate the maximum resolution")
        form.addParam('maxResolution', params.FloatParam,
                      default=20,
                      expertLevel=params.LEVEL_ADVANCED,
                      condition="not dynamicFilter",
                      label='Max. resolution (A)',
                      help="The reconstructed volume will be limited to \n"
                           "this resolution in Angstroms.")
        form.addParam('fractionParticles', params.FloatParam,
                      default=1,
                      expertLevel=params.LEVEL_ADVANCED,
                      label='Fraction of particles',
                      help="Fraction of particles to include in the refinement. \n"
                           "1=all particles, 0.8=80% of particles")
        form.addParam('molecularWeight', params.FloatParam,
                      default=-1,
                      expertLevel=params.LEVEL_ADVANCED,
                      label='Molecular weight (kDa)',
                      help="Molecular weight in kilodaltons, \n"
                           "set to -1 for no constraint")
        form.addParam('keepIntermediate', params.BooleanParam,
                      default=False,
                      expertLevel=params.LEVEL_ADVANCED,
                      label='Keep intermediate volumes?',
                      help='Keep all volumes along iterations')

        form.addParallelSection(threads=8, mpi=0)
    
    # --------------------------- INSERT steps functions ----------------------
    def _insertAllSteps(self):
        self._insertFunctionStep('convertInputStep')
        self._insertFunctionStep('runPrime')
        if not self.keepIntermediate:
            self._insertFunctionStep('cleanPrime')
        self._insertFunctionStep('createOutputStep')        

    # --------------------------- STEPS functions -----------------------------
    def convertInputStep(self):
        self.inputClasses.get().writeStack(self._getExtraPath("classes.spi:stk"))
            
    def runPrime(self):
        # simple_prime stk=stack.spi [vol1=invol.spi] [vol2=<refvol_2.spi> etc.] box=<image size(in pixels)> 
        #              smpd=<sampling distance(in A)> [ring2=<outer mask radius(in pixels){box/2}>] 
        #              [trs=<origin shift(in pixels){0}>] [trsstep=<origin shift stepsize{1}>] [lp=<low-pass limit{20}>]
        #              [dynlp=<yes|no{no}>] [nstates=nstates to reconstruct>] [frac=<fraction of ptcls to include{1}>]
        #              [mw=<molecular weight (in kD)>] [oritab=<previous rounds alignment doc>] [nthr=<nr of OpenMP threads{1}>]

        inputClasses = self.inputClasses.get()
        xdim, _, _ = inputClasses.getDimensions()
        args = "stk=classes.spi box=%d smpd=%f pgrp=%s" % (xdim,
                                                           inputClasses.getSamplingRate(),
                                                           self.symmetryGroup)
        
        if self.dynamicFilter:
            args += " dynlp=yes"
        else:
            args += " lp=%f" % self.maxResolution
        args += " trs=%d trsstep=%d" % (self.maximumShift,
                                        self.shiftStep)
        args += " nstates=%d" % self.Nvolumes
        args += " nthr=%d" % self.numberOfThreads
        
        if self.outerMask > 0:
            args += " ring2=%f" % self.outerMask
        args += " frac=%f" % self.fractionParticles
        
        if self.molecularWeight > 0:
            args += " mw=%f" % self.molecularWeight
        
        self.runJob(simple.Plugin.getProgram(), args,
                    cwd=self._getExtraPath(),
                    env=simple.Plugin.getEnviron())

    def cleanPrime(self):
        self._enterDir(self._getExtraPath())
        cleanPath("cmdline.txt")
        cleanPattern("*.txt")
        cleanPattern("startvol_state*.spi")
        # Get last iteration
        for i in range(1, self.getLastIteration()):
            cleanPattern("recvol_state*_iter%d.spi" % i)
        self._leaveDir()
    
    def createOutputStep(self):
        lastIter = self.getLastIteration()
        
        if lastIter <= 1:
            return
        
        if self.Nvolumes == 1:
            vol = em.Volume()
            vol.setLocation(self._getExtraPath('recvol_state1_iter%d.spi' % lastIter))
            vol.setSamplingRate(self.inputClasses.get().getSamplingRate())
            self._defineOutputs(outputVol=vol)
        else:
            vol = self._createSetOfVolumes()
            vol.setSamplingRate(self.inputClasses.get().getSamplingRate())
            fnVolumes = glob(self._getExtraPath('recvol_state*_iter%d.spi') % lastIter)
            fnVolumes.sort()
            for fnVolume in fnVolumes:
                aux = em.Volume()
                aux.setLocation(fnVolume)
                vol.append(aux)
            self._defineOutputs(outputVolumes=vol)

        self._defineSourceRelation(self.inputClasses, vol)

    # --------------------------- INFO functions ------------------------------
    def _validate(self):
        errors = []
        return errors

    def _summary(self):
        summary = []
        summary.append("Input classes: %s" % self.getObjectTag('inputClasses'))
        summary.append("Starting from: %d random volumes" % self.Nvolumes )
        return summary
    
    def _methods(self):
        if self.inputClasses.get() is not None:
            retval = "We used *simple_prime* program [Elmlund2013] to produce " \
                     "an initial volume from the set of classes %s."
            return [retval % self.getObjectTag('inputClasses')]
        else:
            return []

    # -------------------------- UTILS functions ------------------------------
    def getLastIteration(self):
        lastIter = 1
        pattern = self._getExtraPath("recvol_state1_iter%d.spi")
        while os.path.exists(pattern % lastIter):
            lastIter += 1
        return lastIter - 1
