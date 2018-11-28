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
import pyworkflow.protocol.params as param
from pyworkflow.protocol.params import IntParam, PointerParam, StringParam
from pyworkflow.em.protocol.protocol_micrographs import ProtMicrographs
from pyworkflow.utils.path import cleanPath, makePath, moveFile
from pyworkflow.protocol.constants import STEPS_PARALLEL


class ProtInit3D(ProtMicrographs):
    """
    Ab initio reconstruction from Class Averages
    
    To find more information about Simple.Prime3D go to:
    https://simplecryoem.com/tutorials.html
    """
    _label = 'Init3D'
    
    def __init__(self,**kwargs):
        ProtMicrographs.__init__(self, **kwargs)
        self.stepsExecutionMode = STEPS_PARALLEL
    
    #--------------------------- DEFINE param functions -------------------------------

    def _defineParams(self, form):
        form.addSection(label='Input')
        form.addParam('inputClasses', PointerParam, pointerClass='SetOfClasses2D', allowsNull=False,
                       label='Input Classes', important=True)
        form.addParam('mask', IntParam, default=80, label='Mask radius', help='Mask radius (in Pixels).')
        form.addParam('symmetry', StringParam, important=True, label='Point-group symmetry')
        form.addParallelSection(threads=4, mpi=1)
                
    #--------------------------- INSERT steps functions -------------------------------
    
    def _insertAllSteps(self):
        self._insertFunctionStep("convertInput")
        deps = []
        particleName = self._getExtraPath("particles.mrc")
        SamplingRate = self.inputClasses.get().getSamplingRate()
        deps.append(self._insertFunctionStep('init3DStep', particleName, SamplingRate, prerequisites=[]))
        self._insertFunctionStep("createOutputStep", prerequisites=deps)
        # inputMV = self.inputMovies.get()
        # for movie in inputMV:
        #     # movieName = movie.getFileName()
        #     # SamplingRate = movie.getSamplingRate()
        #     # params = self.getP3DParams(movieName, SamplingRate)
        #     # self._insertRunJobStep('simple_distr_exec', params)
        #     #self.insertFunctionStep("prime3DStep", movie)
        #     self.init3DStep(movie)
        #     self.createOutputStep(movie.getFileName())
        # #self._insertFunctionStep("createOutputStep")
        
    #--------------------------- STEPS functions -------------------------------
    def convertInput(self):
        inputPart = self.inputClasses.get()
        inputPart.writeStack(self._getExtraPath("particles.mrc"))

    def init3DStep(self, partFile,SamplingRate):
        partName = os.path.basename(partFile)
        partName = os.path.splitext(partName)[0]
        tmpDir = self._getTmpPath(partName)
        makePath(tmpDir)

        params = self.getI3DParams(partFile, SamplingRate)

        self.runJob("simple_distr_exec", params, cwd=os.path.abspath(tmpDir))

        #Move output files to ExtraPath and rename them properly
        folder = self._getExtraPath(partName)
        folder = os.path.abspath(folder)
        source_dir = os.path.abspath(tmpDir)
        files1 = glob.iglob(os.path.join(source_dir, "*.txt"))
        files2 = glob.iglob(os.path.join(source_dir, "*.mrc"))
        for file1, file2 in map(None, files1, files2):
            if (file1 != None):
                if os.path.isfile(file1):
                    oldName = os.path.basename(file1)
                    shutil.move(file1, folder + '_' + oldName)
            if (file2 != None):
                if os.path.isfile(file2):
                    oldName = os.path.basename(file2)
                    shutil.move(file2, folder + '_' + oldName)
        cleanPath(tmpDir)

    def getI3DParams(self, partF, SR):
        """Prepare the commmand line to call Prime3D program"""
        fn = os.path.abspath(partF)
        partitions = 1
        params = ' prg=ini3D_from_cavgs stk=%s smpd=%f msk=%d pgrp=%s nparts=%d' % (fn, SR, self.mask.get(), self.symmetry.get(),
                                                                                            partitions)
        return params

    def createOutputStep(self):
        lastIter = self.getLastIteration()

        if lastIter <= 1:
            return

        # if self.Nvolumes == 1:
        vol = em.Volume()
        vol.setLocation(self._getExtraPath('particles_recvol_state01_iter%03d.mrc' % lastIter))
        vol.setSamplingRate(self.inputClasses.get().getSamplingRate())
        self._defineOutputs(outputVol=vol)
        self._defineSourceRelation(self.inputClasses, vol)
        # else:
        #     vol = self._createSetOfVolumes()
        #     vol.setSamplingRate(self.inputClasses.get().getSamplingRate())
        #     fnVolumes = glob(self._getExtraPath('particles_recvol_state*_iter%03d.mrc') % lastIter)
        #     fnVolumes.sort()
        #     for fnVolume in fnVolumes:
        #         aux = em.Volume()
        #         aux.setLocation(fnVolume)
        #         vol.append(aux)
        #     self._defineOutputs(outputVolumes=vol)
        #
        # self._defineSourceRelation(self.inputClasses, vol)
        # pass
        
    #------------------------------- INFO functions ---------------------------------
    def _citations(self):
        cites = ['Elmlund2013']
        return cites

   # -------------------------- UTILS functions ------------------------------
    def getLastIteration(self):
        lastIter = 1
        pattern = self._getExtraPath("particles_recvol_state01_iter%03d.mrc") #Check for larger iterations
        while os.path.exists(pattern % lastIter):
            lastIter += 1
        return lastIter - 1
        
        
