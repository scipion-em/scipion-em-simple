# **************************************************************************
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

import os, glob, shutil
import pyworkflow.em as em
from pyworkflow import VERSION_1_1
from pyworkflow.protocol.params import IntParam, PointerParam, StringParam, EnumParam
from pyworkflow.em.protocol.protocol_micrographs import ProtMicrographs
from pyworkflow.utils.path import cleanPath, makePath, moveFile
from pyworkflow.protocol.constants import LEVEL_ADVANCED
import simple

class ProtInit3D(ProtMicrographs):
    """
    Ab initio reconstruction from Class Averages
    
    To find more information about Simple.Prime3D go to:
    https://simplecryoem.com/tutorials.html
    """
    _label = 'initial_3Dmodel'
    
    def __init__(self,**kwargs):
        ProtMicrographs.__init__(self, **kwargs)

    #--------------------------- DEFINE param functions -------------------------------

    def _defineParams(self, form):
        form.addSection(label='Input')
        form.addParam('inputClasses', PointerParam, label="Input classes",
                      important=True, pointerClass='SetOfClasses2D, SetOfAverages',
                      help="Select either a SetOfClasses2D or a SetOfAverages from the project.")
        form.addParam('mask', IntParam, default=80, label='Mask radius', help='Mask radius (in Pixels).')
        form.addParam('symmetry', StringParam, default='c5', important=True, label='Point-group symmetry',
                      help='cn or dn. For icosahedral viruses, use c5. \n If no symmetry is present, give c1.')
        form.addParallelSection(threads=4, mpi=0)
                
    #--------------------------- INSERT steps functions -------------------------------
    
    def _insertAllSteps(self):
        self._insertFunctionStep("convertInput")
        self._insertFunctionStep('init3DStep')
        self._insertFunctionStep("createOutputStep")
        
    #--------------------------- STEPS functions -------------------------------
    def convertInput(self):
        inputPart = self.inputClasses.get()
        inputPart.writeStack(self._getExtraPath("particles.mrc"))

    def init3DStep(self):
        partFile = self._getExtraPath("particles.mrc")
        SamplingRate = self.inputClasses.get().getSamplingRate()
        partName = os.path.basename(partFile)
        partName = os.path.splitext(partName)[0]
        tmpDir = self._getTmpPath(partName)
        makePath(tmpDir)

        partitions = 1
        params3D = ' prg=initial_3Dmodel msk=%d pgrp=%s nparts=%d nthr=%d eo=no' % (self.mask.get(), self.symmetry.get(),
                                                                               partitions, self.numberOfThreads.get())
        paramsImp = ' prg=import_cavgs stk=%s smpd=%f' %(os.path.abspath(partFile), SamplingRate)

        self.runJob(simple.Plugin.sim_exec(), 'prg=new_project projname=temp', cwd=os.path.abspath(tmpDir),
                    env=simple.Plugin.getEnviron())
        self.runJob(simple.Plugin.sim_exec(), paramsImp, cwd=os.path.abspath(tmpDir) + '/temp', env=simple.Plugin.getEnviron())
        self.runJob(simple.Plugin.distr_exec(), params3D, cwd=os.path.abspath(tmpDir)+'/temp', env=simple.Plugin.getEnviron())

        #Move output files to ExtraPath and rename them properly
        os.remove(os.path.abspath(self._getExtraPath("particles.mrc")))
        mvRoot1 = os.path.join(tmpDir+'/temp/2_initial_3Dmodel', "rec_final.mrc")
        mvRoot2 = os.path.join(tmpDir+'/temp/2_initial_3Dmodel',"final_oris.txt")
        moveFile(mvRoot1, self._getExtraPath(partName + "_rec_final.mrc"))
        moveFile(mvRoot2, self._getExtraPath(partName + "_projvol_oris.txt"))
        cleanPath(tmpDir)

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

