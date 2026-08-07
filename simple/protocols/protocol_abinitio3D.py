 **************************************************************************
# *
# * Authors:     David Herreros
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
from pwem.objects import SetOfParticles, SetOfAverages, SetOfClasses2D
import pyworkflow.em as em
from pyworkflow.protocol.params import IntParam, PointerParam, StringParam, FloatParam, EnumParam
from pyworkflow.utils.path import makePath, moveFile
from pyworkflow.protocol.constants import LEVEL_ADVANCED
import simple

ABINIT_MODE_AVGS = 0
ABINIT_MODE_AVGS_T = "Initialize from 2D classes"
ABINIT_MODE_PARTS = 1
ABINIT_MODE_PARTS_T = "Directly from particles"
ABINIT_MODE_ABINIT = 2
ABINIT_MODE_ABINIT_T = "SIMPLE abinitio2D protocol"

ABINIT_MODES = [ABINIT_MODE_AVGS, ABINIT_MODE_PARTS, ABINIT_MODE_ABINIT]
ABINIT_MODES_T = [ABINIT_MODE_AVGS_T, ABINIT_MODE_PARTS_T, ABINIT_MODE_ABINIT_T]

MMOD_IND = 0
MMOD_IND_T = "Independent"
MMOD_DOCK = 1
MMOD_DOCK_T = "Docked"

MMOD_MODES = [MMOD_IND, MMOD_DOCK]
MMOD_MODES_T = [MMOD_IND_T, MMOD_DOCK_T]

class ProtSimpleAbInitio3D(em.ProtInitialVolume):
    """
    Ab initio reconstruction from Class Averages
    
    To find more information about Simple.Prime3D go to:
    https://simplecryoem.com/tutorials.html
    """
    _label = 'initial_3Dmodel'
    
    def __init__(self,**kwargs):
        em.ProtInitialVolume.__init__(self, **kwargs)

    #--------------------------- DEFINE param functions -----------------------

    def _defineParams(self, form):
        form.addSection(label='Model generation')
        form.addParam('initMethod', EnumParam, 
                      label='Initialization method',
                      choices = ABINIT_MODES_T,
                      default = ABINIT_MODE_AVGS,
                      help = "SIMPLE can generate models directly from "
                      "particles, from 2D class averages or from a previous "
                      "class-average initialization. "
                      )
        form.addParam('inputClasses', PointerParam, 
                      pointerClass='SetOfClasses2D, SetOfAverages',
                      condition = f"initMethod == {ABINIT_MODE_AVGS}",
                      label="Input classes",
                      important=True, 
                      help="Select either a SetOfClasses2D or a "
                      "SetOfAverages from the project."
                      )
        form.addParam('inputParticles', PointerParam,
                      pointerClass = 'SetOfParticles',
                      condition = f"initMethod == {ABINIT_MODE_PARTS}",
                      label = "Input particles",
                      important = True,
                      help = "Select the input particles for model generation"
                      )
        form.addParam('inputProtocol', PointerParam,
                      pointerClass = 'ProtInit3D'
                      )
        form.addParam('nModels', IntParam,
                      label='Initial models',
                      default=1,
                      help = "Select how many initial models will SIMPLE be "
                      "generating."
                      )
        form.addParam('multiModelStrategy', EnumParam,
                      label='Multimodel strategy',
                      condition = "nModels > 1",
                      choices = MMOD_MODES_T,
                      default = MMOD_IND,
                      help = ""
                      )

        form.addParam('startSym', StringParam,
                      level=LEVEL_ADVANCED,
                      label='Starting Symmetry',
                      default="C1",
                      help=""
                      )
        form.addParam('endSym', StringParam,
                      level=LEVEL_ADVANCED,
                      label='Final Symmetry',
                      default="C1",
                      help=""
                      )

        form.addParam('mask', IntParam, default=80, label='Mask radius', help='Mask radius (in Pixels).')
        form.addParam('lp', FloatParam, default=0.5, expertLevel=LEVEL_ADVANCED,
                      label='Low pass limit', help='Low pass limit in normalized frequency (<0.5)')
        form.addParam('symmetry', StringParam, default='c5', important=True, label='Point-group symmetry',
                      help='cn or dn. For icosahedral viruses, use c5. \n If no symmetry is present, give c1.')
        form.addParallelSection(threads=4, mpi=0)
                
    #--------------------------- INSERT steps functions -------------------------------
    
    def _insertAllSteps(self):
        self._initialize()
        self._insertFunctionStep(self.convertInput)
        self._insertFunctionStep(self.init3DStep)
        self._insertFunctionStep(self.createOutputStep)

    def _initialize(self):
        # Initialization methods
        self.init_method = self.initMethod.get()
        self.input_parts = None
        self.input_avgs = None
        self.input_prot = None
        if self.init_method is ABINIT_MODE_PARTS:
            print("Ab initio will be done from particles\n")
            self.input_parts = self.inputParticles.get()
        elif self.init_method is ABINIT_MODE_AVGS:
            print("Ab initio will be done with 2D classes\n")
            self.input_avgs = self.inputClasses.get()
        else:
            print("Ab initio will continue from previous run\n")
            self.input_prot = self.inputProtocol.get()

        # Number of classes and multiclass method
        self.n_classes = self.nModels.get()
        self.mclass_method = None
        if self.n_classes > 1:
            print("More than 1 models/classes selected... \n")
            self.mclass_method = self.multiModelStrategy.get()
            if self.mclass_method is MMOD_IND:
                print("\tEach class will be treated as an individual\n")
            elif self.mclass_method is MMOD_DOCK:
                print("\tClasses will be docked in the end\n")

        
    #--------------------------- STEPS functions -------------------------------
    def convertInput(self):
        # Prepare the inputs
        if self.init_method is ABINIT_MODE_PARTS:
            print("Preparing the input SetOfParticles for SIMPLE...\n")
        elif self.init_method is ABINIT_MODE_AVGS:
            print("Preparing the input averages or 2D classes for SIMPLE...\n")
            if isinstance(self.input_avgs, SetOfAverages):
                pass
            elif isinstance(self.input_avgs, SetOfClasses2D):
                pass
        elif self.init_method is ABINIT_MODE_ABINIT:
            print("Passing the SIMPLE protocol to SIMPLE...\n")

        inputPart = self.inputClasses.get()
        inputPart.writeStack(self._getTmpPath("particles.mrc"))

    def init3DStep(self):
        partFile = self._getTmpPath("particles.mrc")
        SamplingRate = self.inputClasses.get().getSamplingRate()
        partName = os.path.basename(partFile)
        partName = os.path.splitext(partName)[0]
        tmpDir = self._getTmpPath(partName)
        makePath(tmpDir)

        partitions = 1
        params3D = ' prg=initial_3Dmodel msk=%d pgrp=%s lpstart=%f lpstop=%f nparts=%d nthr=%d' % \
                   (self.mask.get(), self.symmetry.get(), self.lp.get(), self.lp.get(), partitions,
                    self.numberOfThreads.get())
        paramsImp = ' prg=import_cavgs stk=%s smpd=%f' %(os.path.abspath(partFile), SamplingRate)

        self.runJob(simple.Plugin.sim_exec(), 'prg=new_project projname=temp', cwd=os.path.abspath(tmpDir),
                    env=simple.Plugin.getEnviron())
        self.runJob(simple.Plugin.sim_exec(), paramsImp, cwd=os.path.abspath(tmpDir) + '/temp', env=simple.Plugin.getEnviron())
        self.runJob(simple.Plugin.distr_exec(), params3D, cwd=os.path.abspath(tmpDir)+'/temp', env=simple.Plugin.getEnviron())

        #Move output files to ExtraPath and rename them properly
        mvRoot1 = os.path.join(tmpDir+'/temp/2_initial_3Dmodel', "rec_final.mrc")
        mvRoot2 = os.path.join(tmpDir+'/temp/2_initial_3Dmodel',"final_oris.txt")
        moveFile(mvRoot1, self._getExtraPath(partName + "_rec_final.mrc"))
        moveFile(mvRoot2, self._getExtraPath(partName + "_projvol_oris.txt"))

    def createOutputStep(self):
        vol = em.Volume()
        vol.setLocation(self._getExtraPath('particles_rec_final.mrc'))
        vol.setSamplingRate(self.inputClasses.get().getSamplingRate())
        self._defineOutputs(outputVol=vol)
        self._defineSourceRelation(self.inputClasses, vol)
        
    #------------------------------- INFO functions ---------------------------------
    def _citations(self):
        cites = ['Elmlund2013']
        return cites

